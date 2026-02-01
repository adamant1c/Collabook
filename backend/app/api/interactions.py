from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.core.context_optimizer import create_compact_context, create_optimized_prompt
from app.core.survival import update_survival_stats, get_survival_penalties, apply_starvation_death
from app.core.content_filter import validate_user_input, sanitize_llm_output, log_violation
from app.core.llm_client import llm_client
from app.api.auth import get_current_user
from app.models.schemas import InteractionRequest, InteractionResponse
from app.models.db_models import Turn, Character, Story, User, PlayerQuest, QuestStatus, Enemy, NPC
from app.core.game_rules import GameRules, EnemyTemplates
import json
import random
import re

router = APIRouter(prefix="/interact", tags=["interactions"])

@router.post("", response_model=InteractionResponse)
async def create_interaction(
    interaction: InteractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process user action with OPTIMIZED token usage"""
    
    # Get character
    character = db.query(Character).filter(Character.id == interaction.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Initialize response variables
    suggested_actions = []
    
    # Calculate turn number early for combat state
    max_turn = db.query(Turn).filter(Turn.character_id == character.id).count()
    turn_number = max_turn + 1
    
    # Initialize response variables
    suggested_actions = []
    
    # Verify ownership
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")
    
    # ------------------------------------------------------------------
    # PHASE 1: COMBAT INTERCEPTION (Backend Authority)
    # ------------------------------------------------------------------
    combat_log = []
    directive_prompt = ""
    combat_active = False
    
    # Check if character is currently in combat
    if character.combat_state:
        combat_active = True
        state = character.combat_state
        enemy_id = state.get('enemy_id')
        enemy = db.query(Enemy).filter(Enemy.id == enemy_id).first()
        
        if not enemy:
            # Fallback if enemy deleted
            character.combat_state = None
            combat_active = False
        else:
            # Resolve Combat Round
            # 1. Parse User Action (basic keyword matching for now)
            action_type = "attack"
            if "fuga" in interaction.user_action.lower() or "flee" in interaction.user_action.lower():
                action_type = "flee"
            elif "pozione" in interaction.user_action.lower() or "potion" in interaction.user_action.lower():
                action_type = "heal"
                
            # 2. Execute Rules
            # Reconstruct temporary stats for calculation
            player_stats = {
                "attack_bonus": current_user.strength // 2, # Simplified D&D mod
                "ac": 10 + (current_user.dexterity // 2),
                "dmg_bonus": current_user.strength // 2
            }
            # Use enemy current HP from state, or max if not set
            current_enemy_hp = state.get('enemy_hp', enemy.hp)
            
            enemy_stats = {
                "name": enemy.name,
                "ac": enemy.ac,
                "hp": current_enemy_hp,
                "attack_bonus": enemy.attack_bonus
            }
            
            round_result = GameRules.resolve_combat_round(player_stats, enemy_stats, action_type)
            
            # 3. Apply Results to DB/State
            # Player Damage
            if round_result['enemy_dmg'] > 0:
                current_user.hp = max(0, current_user.hp - round_result['enemy_dmg'])
            
            # Enemy Damage
            if round_result['player_dmg'] > 0:
                current_enemy_hp -= round_result['player_dmg']
                state['enemy_hp'] = current_enemy_hp
            
            # 4. Check for Win/Loss
            if current_user.hp <= 0:
                # Player Died
                character.combat_state = None # End combat
                character.deaths += 1
                character.status = "dead" # Or handle resurrection logic
                directive_prompt = f"""
                SYSTEM DIRECTIVE: The player has DIED in combat against {enemy.name}.
                Enemy HP remaining: {current_enemy_hp}.
                Narrate the hero's tragic fall.
                """
            elif current_enemy_hp <= 0:
                # Victory!
                character.combat_state = None
                xp_gain = enemy.xp_reward
                current_user.xp += xp_gain
                
                # Check Level Up
                new_level = GameRules.get_level_from_xp(current_user.xp)
                level_up_msg = ""
                if new_level > current_user.level:
                    current_user.level = new_level
                    current_user.max_hp += 10 # Simple level up bonus
                    current_user.hp = current_user.max_hp # Full heal on level up? Or just increase cap? Let's full heal.
                    level_up_msg = f"LEVEL UP! You are now level {new_level}!"
                
                directive_prompt = f"""
                SYSTEM DIRECTIVE: Information provided by Game Engine.
                Player DEFEATED the {enemy.name}!
                Combat Log: {'. '.join(round_result['log'])}
                Rewards: +{xp_gain} XP. {level_up_msg}
                
                Narrate the victory and the loot found.
                """
            else:
                # Fight continues
                character.combat_state = state # Save updated state
                # db_models_Enemy = enemy # Keep reference if needed
                directive_prompt = f"""
                SYSTEM DIRECTIVE: COMBAT ROUND RESOLVED BY ENGINE.
                Player Status: {current_user.hp}/{current_user.max_hp} HP
                Enemy Status: {enemy.name} has {current_enemy_hp} HP left.
                
                Round Details:
                {'. '.join(round_result['log'])}
                
                Narrate this specific exchange of blows based on the logs above. Do NOT invent new damage.
                """
    
    # Phase 6: Content moderation - validate user input
    validation_result = validate_user_input(interaction.user_action)
    if not validation_result["is_valid"]:
        # Log violation
        log_violation(current_user.id, list(validation_result["violations"].keys())[0], interaction.user_action)
        
        raise HTTPException(
            status_code=400,
            detail=validation_result["message"]
        )
    
    # Get story
    story = db.query(Story).filter(Story.id == character.story_id).first()
    
    # Get recent turns (only last 3 for context)
    recent_turns = db.query(Turn).filter(
        Turn.character_id == character.id
    ).order_by(Turn.turn_number.desc()).limit(3).all()
    recent_turns = list(reversed(recent_turns))
    
    # Get active quests
    active_quests = db.query(PlayerQuest).filter(
        PlayerQuest.character_id == character.id,
        PlayerQuest.status == QuestStatus.IN_PROGRESS
    ).all()
    
    # Multiplayer: Get other active characters in this story
    active_char_ids = redis_client.get_active_characters(story.id)
    other_players = []
    if active_char_ids:
        # Filter out current character
        other_ids = [cid for cid in active_char_ids if cid != character.id]
        if other_ids:
            # Query db for details - join with User for names
            other_players = db.query(Character).join(User).filter(
                Character.id.in_(other_ids)
            ).all()

    # Create OPTIMIZED compact context (200-400 tokens vs 1000-2000)
    compact_context = create_compact_context(
        user=current_user,
        character=character,
        story=story,
        recent_turns=recent_turns,
        active_quests=active_quests,
        max_turns=3,  # Only last 3 turns
        other_players=other_players  # Pass other players to context
    )
    
    # Create optimized prompt
    optimized_prompt = create_optimized_prompt(compact_context, interaction.user_action)
    
    # Determine system prompt based on language
    system_prompt = "You are a Dungeon Master. Respond in JSON format."
    if interaction.language and interaction.language.lower().startswith("it"):
        json_desc = """
        IMPORTANTE: Rispondi SOLO in formato JSON valido.
        Struttura:
        {
            "narration": "testo della storia...",
            "event": "start_combat" | null,
            "enemy": "nome_nemico" | null,
            "suggested_actions": ["azione 1", "azione 2"]
        }
        """
        system_prompt = f"""Sei un Dungeon Master italiano. {json_desc}
        
        REGOLE:
        1. La narrazione deve essere in ITALIANO puro.
        2. Se l'utente vuole combattere, usa 'event': 'start_combat' e metti il nome del nemico.
        3. Se ricevi una 'SYSTEM DIRECTIVE', usala come verità assoluta per la narrazione.
        4. Includi SEMPRE 2 azioni suggerite plausibili nel campo 'suggested_actions'.
        5. NON inventare stats del giocatore nella narrazione, usa quelle fornite nel contesto.
        """
    
    # Generate narration with minimal tokens
    try:
        raw_response = await llm_client.generate(
            system_prompt=system_prompt,
            user_message=optimized_prompt
        )
        
        # Parse JSON response
        try:
            # Try to find JSON block
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                try:
                    response_data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    # If direct parsing fails, try cleaning the match
                    cleaned_json = json_match.group(0).replace('\n', '').replace('\r', '')
                    # Remove potential trailing commas before closing braces
                    cleaned_json = re.sub(r',\s*\}', '}', cleaned_json)
                    cleaned_json = re.sub(r',\s*\]', ']', cleaned_json)
                    response_data = json.loads(cleaned_json)

                narration = response_data.get("narration", raw_response)
                suggested_actions = response_data.get("suggested_actions", [])
                event = response_data.get("event")
                enemy_name = response_data.get("enemy")
                
                # Handle Start Combat Trigger
                if event == "start_combat" and enemy_name and not character.combat_state:
                    template = EnemyTemplates.get_template(enemy_name)
                    new_enemy = Enemy(
                        story_id=story.id,
                        name=template['name'],
                        hp=template['hp'],
                        max_hp=template['hp'],
                        ac=template['ac'],
                        attack_bonus=template['attack_bonus'],
                        xp_reward=template['xp_reward'],
                        level=template['level'],
                        damage_dice="1d6", attack=0, defense=0
                    )
                    db.add(new_enemy)
                    db.flush()
                    character.combat_state = {
                        "enemy_id": new_enemy.id,
                        "enemy_hp": new_enemy.hp,
                        "start_turn": turn_number
                    }
                    combat_active = True
                    # Do not append (COMBAT STARTED!) to narration, the UI will handle it
            else:
                # If no JSON block but looks like it might be JSON-ish, try to extract narration
                if '"narration":' in raw_response:
                    nar_match = re.search(r'"narration":\s*"([^"]*)"', raw_response)
                    if nar_match:
                        narration = nar_match.group(1)
                    else:
                        narration = raw_response
                else:
                    narration = raw_response
                suggested_actions = ["Attacca", "Difenditi"]
        except Exception as e:
            print(f"⚠️ JSON Parsing Error: {e}")
            narration = raw_response
            suggested_actions = []
            
    except Exception as e:
        print(f"❌ Critical LLM Error: {e}")
        narration = "⚠️ (System) The Dungeon Master is temporarily unavailable."
    
    # Phase 6: Sanitize LLM output
    narration, was_sanitized = sanitize_llm_output(narration)
    if was_sanitized:
        # Log that LLM output was filtered
        print(f"⚠️ LLM output sanitized for character {character.id}")
    
    # Check for quest completion hints
    quest_hint = None
    if "✨" in narration or "quest" in narration.lower() and "complete" in narration.lower():
        quest_hint = "Quest progress detected! Check your active quests."
    
    # Turn creation logic proceeds...
    
    # Create turn
    db_turn = Turn(
        story_id=story.id,
        character_id=character.id,
        user_action=interaction.user_action,
        narration=narration,
        turn_number=turn_number
    )
    db.add(db_turn)
    db.flush()  # Ensure db_turn.id is populated immediately
    
    # Update survival stats (Phase 5)
    survival_result = update_survival_stats(character, turns_elapsed=1)
    
    # Survival Mode: Day Counter Logic
    today = datetime.utcnow().date()
    if character.last_played_date is None or character.last_played_date.date() != today:
        character.days_survived += 1
        character.last_played_date = datetime.utcnow()
        
        goal = story.survival_goal_days if hasattr(story, "survival_goal_days") else 10
        
        # Win Condition Check
        if character.days_survived >= goal:
             db.commit()
             db.refresh(db_turn)
             return InteractionResponse(
                turn_id=db_turn.id,
                narration=f"CONGRATULATIONS! You have survived {goal} days! You have won the Survival Mode!",
                turn_number=turn_number,
                quest_hint="SURVIVAL COMPLETED!"
            )
            
        # Add a notification about the new day
        if character.days_survived == 1:
            quest_hint = f"Day 1/{goal}. Survive!"
        else:
            day_msg = f"Day {character.days_survived}/{goal}"
            quest_hint = f"{quest_hint} | {day_msg}" if quest_hint else day_msg
    
    # Apply HP drain if any
    if survival_result["penalties"]["hp_drain"] > 0:
        current_user.hp = max(0, current_user.hp - survival_result["penalties"]["hp_drain"])
    
    # Check for death from starvation/dehydration
    death_result = apply_starvation_death(character, current_user, db)
    if death_result.get("permanent_death"):
        db.commit()
        db.refresh(db_turn)
        return InteractionResponse(
            turn_id=db_turn.id,
            narration=death_result["message"],
            turn_number=turn_number,
            critical_warning=True
        )
    
    # Update character current_state (compact summary)
    last_action = interaction.user_action[:100]
    last_result = narration[:150]
    character.current_state = f"{last_action}... {last_result}"
    
    db.commit()
    db.refresh(db_turn)
    
    # Return Response with Entities (Pre-detected or from state)
    detected_entities = []
    if combat_active:
        enemy_id = character.combat_state.get('enemy_id')
        current_enemy = db.query(Enemy).filter(Enemy.id == enemy_id).first()
        if current_enemy:
            detected_entities.append({
                "type": "enemy",
                "name": current_enemy.name,
                "hp": character.combat_state.get('enemy_hp'), 
                "max_hp": current_enemy.max_hp,
                "ac": current_enemy.ac,
                "active": True
            })

    return InteractionResponse(
        turn_id=db_turn.id,
        narration=narration,
        turn_number=turn_number,
        quest_hint=quest_hint,
        survival_warnings=survival_result.get("warnings", []),
        critical_condition=survival_result.get("critical", False),
        detected_entities=detected_entities,
        suggested_actions=suggested_actions
    )
