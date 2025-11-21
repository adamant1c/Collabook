from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.models.schemas import StoryCreate, StoryResponse, CharacterCreate, CharacterResponse
from app.models.db_models import Story, Character, User
from app.agents.matchmaker import matchmaker_agent

router = APIRouter(prefix="/stories", tags=["stories"])

@router.post("/", response_model=StoryResponse)
async def create_story(story: StoryCreate, db: Session = Depends(get_db)):
    """Create a new story world"""
    db_story = Story(
        title=story.title,
        world_description=story.world_description,
        genre=story.genre,
        metadata=story.metadata,
        current_state="The story is beginning..."
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    
    # Cache story context in Redis
    redis_client.set_story_context(db_story.id, {
        "world_description": db_story.world_description,
        "genre": db_story.genre,
        "current_state": db_story.current_state,
        "metadata": db_story.metadata
    })
    
    return db_story

@router.get("/", response_model=List[StoryResponse])
async def list_stories(db: Session = Depends(get_db)):
    """List all available stories"""
    stories = db.query(Story).all()
    return stories

@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str, db: Session = Depends(get_db)):
    """Get story by ID"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.post("/{story_id}/join", response_model=CharacterResponse)
async def join_story(story_id: str, character: CharacterCreate, user_id: str, db: Session = Depends(get_db)):
    """Join an existing story with a character"""
    # Verify story exists
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get story context
    story_context = redis_client.get_story_context(story_id)
    if not story_context:
        story_context = {
            "world_description": story.world_description,
            "genre": story.genre,
            "current_state": story.current_state,
            "metadata": story.metadata
        }
    
    # Use matchmaker agent to find insertion point
    character_info = {
        "name": user.name,
        "profession": user.profession,
        "description": user.description
    }
    insertion_point = await matchmaker_agent.find_insertion_point(story_context, character_info)
    
    # Create character
    db_character = Character(
        user_id=user_id,
        story_id=story_id,
        insertion_point=insertion_point,
        status="active"
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    
    # Add to active characters in Redis
    redis_client.add_active_character(story_id, db_character.id)
    
    return db_character
