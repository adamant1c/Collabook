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
    
    # Verify ownership
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")
    
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
    system_prompt = "You are a Dungeon Master. Respond in 2-3 paragraphs."
    if interaction.language and interaction.language.lower().startswith("it"):
        system_prompt = """Sei un Dungeon Master italiano. IMPORTANTE: Devi scrivere SOLO in ITALIANO.

⚠️ ATTENZIONE - REGOLE OBBLIGATORIE:
- Scrivi ESCLUSIVAMENTE in italiano puro.
- È VIETATO usare parole o frasi inglesi.
- NON includere etichette, ritorni a capo per titoli o introduzioni in inglese.
- La narrazione deve essere coinvolgente e usare il "tu" per il personaggio.

Rispondi direttamente in 2-3 paragrafi."""
    
    # Generate narration with minimal tokens
    try:
        narration = await llm_client.generate(
            system_prompt=system_prompt,
            user_message=optimized_prompt
        )
    except Exception as e:
        print(f"❌ Critical LLM Error: {e}")
        narration = "⚠️ (System) The Dungeon Master is temporarily unavailable. Please try your action again in a moment."
    
    # Phase 6: Sanitize LLM output
    narration, was_sanitized = sanitize_llm_output(narration)
    if was_sanitized:
        # Log that LLM output was filtered
        print(f"⚠️ LLM output sanitized for character {character.id}")
    
    # Check for quest completion hints
    quest_hint = None
    if "✨" in narration or "quest" in narration.lower() and "complete" in narration.lower():
        quest_hint = "Quest progress detected! Check your active quests."
    
    # Calculate turn number
    max_turn = db.query(Turn).filter(Turn.character_id == character.id).count()
    turn_number = max_turn + 1
    
    # Create turn
    db_turn = Turn(
        story_id=story.id,
        character_id=character.id,
        user_action=interaction.user_action,
        narration=narration,
        turn_number=turn_number
    )
    db.add(db_turn)
    
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
    
    # Phase 7: Entity detection in narration
    detected_entities = []
    
    # Check for Enemies
    for enemy in story.enemies:
        if enemy.name.lower() in narration.lower():
            detected_entities.append({
                "type": "enemy",
                "name": enemy.name,
                "image_url": enemy.image_url
            })
            
    # Check for NPCs
    for npc in story.npcs:
        if npc.name.lower() in narration.lower():
            detected_entities.append({
                "type": "npc",
                "name": npc.name,
                "image_url": npc.image_url
            })
    
    return InteractionResponse(
        turn_id=db_turn.id,
        narration=narration,
        turn_number=turn_number,
        quest_hint=quest_hint,
        survival_warnings=survival_result.get("warnings", []),
        critical_condition=survival_result.get("critical", False),
        detected_entities=detected_entities
    )
