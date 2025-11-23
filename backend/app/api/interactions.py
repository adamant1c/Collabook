from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.models.schemas import InteractionRequest, InteractionResponse
from app.models.db_models import Turn, Character, Story, User
from app.agents.narrator import narrator_agent
from app.agents.world_keeper import world_keeper_agent

router = APIRouter(prefix="/interact", tags=["interactions"])

@router.post("/", response_model=InteractionResponse)
async def create_interaction(interaction: InteractionRequest, db: Session = Depends(get_db)):
    """Process a user action and generate narration"""
    # Get character
    character = db.query(Character).filter(Character.id == interaction.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get story
    story = db.query(Story).filter(Story.id == character.story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Get user
    user = db.query(User).filter(User.id == character.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get story context from Redis or DB
    story_context = redis_client.get_story_context(story.id)
    if not story_context:
        story_context = {
            "world_description": story.world_description,
            "genre": story.genre,
            "current_state": story.current_state,
            "world_metadata": story.world_metadata
        }
    
    # Validate action with World Keeper
    validation = await world_keeper_agent.validate_action(story_context, interaction.user_action)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=f"Invalid action: {validation['reason']}")
    
    # Get previous turns for context
    previous_turns = db.query(Turn).filter(
        Turn.story_id == story.id
    ).order_by(Turn.turn_number.desc()).limit(5).all()
    
    history = [
        {"user": turn.user_action, "ai": turn.narration}
        for turn in reversed(previous_turns)
    ]
    
    # Generate narration with Narrator agent
    character_info = {
        "name": user.name,
        "profession": user.profession,
        "description": user.description
    }
    
    narration = await narrator_agent.generate_narration(
        story_context, 
        character_info, 
        interaction.user_action,
        history
    )
    
    # Calculate turn number
    max_turn = db.query(Turn).filter(Turn.story_id == story.id).count()
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
    
    # Update story state with World Keeper
    updated_state = await world_keeper_agent.update_world_state(
        story_context["current_state"],
        f"Character {user.name} {interaction.user_action}. {narration}"
    )
    
    story.current_state = updated_state
    story_context["current_state"] = updated_state
    
    db.commit()
    db.refresh(db_turn)
    
    # Update Redis cache
    redis_client.set_story_context(story.id, story_context)
    
    return InteractionResponse(
        turn_id=db_turn.id,
        narration=narration,
        turn_number=turn_number
    )
