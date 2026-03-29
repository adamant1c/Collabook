from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_llm_client, get_redis_client
from app.core.llm_client import LLMClient
from app.core.redis_client import RedisClient
from app.core.context_optimizer import create_compact_context, create_optimized_prompt
from app.core.content_filter import validate_user_input, sanitize_llm_output, log_violation
from app.core.game_rules import GameRules
from app.api.auth import get_current_user
from app.models.schemas import InteractionRequest, InteractionResponse
from app.models.db_models import Turn, Character, Story, User, PlayerQuest, QuestStatus, Enemy, MapNode, MapEdge

from app.services.combat_service import resolve_inline_combat, start_combat_from_event
from app.services.narration_service import generate_narration, parse_llm_response
from app.services.survival_service import process_survival_turn
from app.services.quest_service import check_quest_completion_hints

router = APIRouter(prefix="/interact", tags=["interactions"])


@router.post("", response_model=InteractionResponse)
async def create_interaction(
    interaction: InteractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    llm: LLMClient = Depends(get_llm_client),
    redis: RedisClient = Depends(get_redis_client),
):
    """Process user action with OPTIMIZED token usage"""

    # ------------------------------------------------------------------
    # PHASE 1: PRE-PROCESSING
    # ------------------------------------------------------------------
    character = db.query(Character).filter(Character.id == interaction.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")

    # Content moderation
    validation_result = validate_user_input(interaction.user_action)
    if not validation_result["is_valid"]:
        log_violation(current_user.id, list(validation_result["violations"].keys())[0], interaction.user_action)
        raise HTTPException(status_code=400, detail=validation_result["message"])

    story = db.query(Story).filter(Story.id == character.story_id).first()
    max_turn = db.query(Turn).filter(Turn.character_id == character.id).count()
    turn_number = max_turn + 1

    # Context building
    recent_turns = (
        db.query(Turn)
        .filter(Turn.character_id == character.id)
        .order_by(Turn.turn_number.desc())
        .limit(3)
        .all()
    )
    recent_turns = list(reversed(recent_turns))

    active_quests = db.query(PlayerQuest).filter(
        PlayerQuest.character_id == character.id,
        PlayerQuest.status == QuestStatus.IN_PROGRESS,
    ).all()

    # Multiplayer context
    active_char_ids = redis.get_active_characters(story.id)
    other_players = []
    if active_char_ids:
        other_ids = [cid for cid in active_char_ids if cid != character.id]
        if other_ids:
            other_players = db.query(Character).join(User).filter(Character.id.in_(other_ids)).all()

    # Map context
    current_location = None
    nearby_locations = []
    if character.current_location_id:
        current_location = db.query(MapNode).filter(MapNode.id == character.current_location_id).first()
        if current_location:
            # Find neighbors
            edges = db.query(MapEdge).filter(
                (MapEdge.from_node_id == current_location.id) |
                (MapEdge.bidirectional & (MapEdge.to_node_id == current_location.id))
            ).all()
            
            neighbor_ids = set()
            for edge in edges:
                if edge.from_node_id == current_location.id:
                    neighbor_ids.add(edge.to_node_id)
                else:
                    neighbor_ids.add(edge.from_node_id)
            
            if neighbor_ids:
                nearby_locations = db.query(MapNode).filter(MapNode.id.in_(list(neighbor_ids))).all()
    else:
        # Fallback: find starting location for the story
        starting_loc = db.query(MapNode).filter(
            MapNode.story_id == story.id,
            MapNode.is_starting_location == True
        ).first()
        if starting_loc:
            character.current_location_id = starting_loc.id
            current_location = starting_loc
            # (No neighbors for now till logic is fully initialized)

    compact_context = create_compact_context(
        user=current_user,
        character=character,
        story=story,
        recent_turns=recent_turns,
        active_quests=active_quests,
        max_turns=3,
        other_players=other_players,
        current_location=current_location,
        nearby_locations=nearby_locations
    )

    # System prompt
    json_desc_en = """
    IMPORTANT: Respond ONLY in valid JSON format.
    JSON structure:
    {
        "narration": "story text...",
        "event": "start_combat" | null,
        "enemy": "enemy_name" | null,
        "suggested_actions": ["action 1", "action 2"],
        "rewards": {"gold": 0, "xp": 0}
    }
    """
    system_prompt = f"""You are a Dungeon Master. {json_desc_en}

    RULES:
    1. The narration must be engaging and descriptive.
    2. If the user wants to fight, use 'event': 'start_combat' and put the enemy name in 'enemy'.
    3. If you receive a 'SYSTEM DIRECTIVE', use it as absolute truth for the narration.
    4. ALWAYS include 2 plausible suggested actions in the 'suggested_actions' field.
    5. Do NOT invent player stats in the narration, use the ones provided in context.
    6. Do NOT add extra fields beyond the ones specified above.
    """
    if interaction.language and interaction.language.lower().startswith("it"):
        json_desc = """
        IMPORTANTE: Rispondi SOLO in formato JSON valido.
        Struttura JSON:
        {
            "narration": "testo della storia...",
            "event": "start_combat" | null,
            "enemy": "nome_nemico" | null,
            "suggested_actions": ["azione 1", "azione 2"],
            "rewards": {"gold": 0, "xp": 0},
            "new_location": "nome_località" | null
        }
        """
        system_prompt = f"""Sei un Dungeon Master italiano. {json_desc}
        
        REGOLE:
        1. La narrazione deve essere in ITALIANO puro.
        2. Se l'utente vuole combattere, usa 'event': 'start_combat' e metti il nome del nemico.
        3. Se l'utente si sposta in una nuova località (tra quelle vicine o una nuova descritta), inserisci il nome esatto della località in 'new_location'.
        4. Se ricevi una 'SYSTEM DIRECTIVE', usala come verità assoluta per la narrazione.
        5. Includi SEMPRE 2 azioni suggerite plausibili nel campo 'suggested_actions'.
        6. NON inventare stats del giocatore nella narrazione, usa quelle fornite nel contesto.
        """

    # ------------------------------------------------------------------
    # PHASE 2: COMBAT RESOLUTION (delegated)
    # ------------------------------------------------------------------
    combat_result = resolve_inline_combat(character, current_user, interaction.user_action, db)
    combat_active = combat_result["combat_active"]

    # ------------------------------------------------------------------
    # PHASE 3: LLM NARRATION (delegated)
    # ------------------------------------------------------------------
    optimized_prompt = create_optimized_prompt(compact_context, interaction.user_action)

    try:
        raw_response = await generate_narration(system_prompt, optimized_prompt, llm_client=llm)
        parsed = parse_llm_response(raw_response)
        narration = parsed.narration
        suggested_actions = parsed.suggested_actions
    except Exception as e:
        print(f"❌ Critical LLM Error: {e}")
        narration = "⚠️ (System) The Dungeon Master is temporarily unavailable."
        suggested_actions = []
        parsed = None

    # ------------------------------------------------------------------
    # PHASE 4: POST-LLM PROCESSING
    # ------------------------------------------------------------------
    if parsed and not parsed.parse_error:
        # Apply rewards from LLM response
        if parsed.rewards:
            if parsed.rewards.get("gold"):
                character.gold += int(parsed.rewards["gold"])
            if parsed.rewards.get("xp"):
                current_user.xp += int(parsed.rewards["xp"])
                new_level = GameRules.get_level_from_xp(current_user.xp)
                if new_level > current_user.level:
                    current_user.level = new_level
                    current_user.max_hp += 10
                    current_user.hp = current_user.max_hp

        # Handle combat start event
        if parsed.event == "start_combat" and parsed.enemy_name and not character.combat_state:
            combat_active = start_combat_from_event(
                character, story, parsed.enemy_name, turn_number, db
            )

        # Handle movement from LLM
        if parsed.new_location:
            # Try to find the node by name (case-insensitive) in the same story
            target_node = db.query(MapNode).filter(
                MapNode.story_id == story.id,
                (MapNode.name.ilike(parsed.new_location)) | (MapNode.name_it.ilike(parsed.new_location))
            ).first()
            
            if target_node:
                 character.current_location_id = target_node.id
                 # Refresh for response
                 current_location = target_node

    # Content filter
    narration, was_sanitized = sanitize_llm_output(narration)
    if was_sanitized:
        print(f"⚠️ LLM output sanitized for character {character.id}")

    # Quest hints
    quest_hint = check_quest_completion_hints(active_quests, narration)

    # ------------------------------------------------------------------
    # PHASE 5: TURN CREATION
    # ------------------------------------------------------------------
    db_turn = Turn(
        story_id=story.id,
        character_id=character.id,
        user_action=interaction.user_action,
        narration=narration,
        turn_number=turn_number,
    )
    db.add(db_turn)
    db.flush()

    # ------------------------------------------------------------------
    # PHASE 6: SURVIVAL (delegated)
    # ------------------------------------------------------------------
    survival = process_survival_turn(
        character, current_user, story, db_turn, turn_number, db,
        existing_quest_hint=quest_hint,
    )
    if survival.early_return:
        return survival.early_return
    quest_hint = survival.quest_hint

    # ------------------------------------------------------------------
    # PHASE 7: RESPONSE BUILDING
    # ------------------------------------------------------------------
    character.current_state = f"{interaction.user_action[:100]}... {narration[:150]}"
    db.commit()
    db.refresh(db_turn)

    detected_entities = []
    if combat_active and character.combat_state:
        enemy_id = character.combat_state.get("enemy_id")
        current_enemy = db.query(Enemy).filter(Enemy.id == enemy_id).first()
        if current_enemy:
            detected_entities.append({
                "type": "enemy",
                "name": current_enemy.name,
                "hp": character.combat_state.get("enemy_hp"),
                "max_hp": current_enemy.max_hp,
                "ac": current_enemy.ac,
                "image_url": current_enemy.image_url,
                "active": True,
            })

    return InteractionResponse(
        turn_id=db_turn.id,
        narration=narration,
        turn_number=turn_number,
        quest_hint=quest_hint,
        survival_warnings=survival.warnings,
        critical_condition=survival.critical,
        detected_entities=detected_entities,
        suggested_actions=suggested_actions,
        player_stats={
            "hp": current_user.hp,
            "max_hp": current_user.max_hp,
            "xp": current_user.xp,
            "level": current_user.level,
            "gold": character.gold,
        },
        current_location_id=character.current_location_id,
        current_location_name=current_location.name_it if current_location and interaction.language.startswith("it") else (current_location.name if current_location else None),
        nearby_locations=[
            {"id": n.id, "name": n.name_it if n.name_it and interaction.language.startswith("it") else n.name}
            for n in nearby_locations
        ]
    )
