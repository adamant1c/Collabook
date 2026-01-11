from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.models.schemas import StoryCreate, StoryResponse, CharacterCreate, CharacterResponse
from app.models.db_models import Story, Character, User
from app.agents.matchmaker import matchmaker_agent
from app.api.auth import get_current_user, require_admin

router = APIRouter(prefix="/stories", tags=["stories"])

@router.post("/", response_model=StoryResponse)
async def create_story(
    story: StoryCreate, 
    current_user: User = Depends(require_admin),  # Only admins can create worlds!
    db: Session = Depends(get_db)
):
    """Create a new story world (Admin only)"""
    db_story = Story(
        title=story.title,
        world_description=story.world_description,
        genre=story.genre,
        world_metadata=story.world_metadata,
        survival_goal_days=story.survival_goal_days,
        created_by=current_user.id  # Track who created it
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    
    # Cache story context in Redis
    redis_client.set_story_context(db_story.id, {
        "world_description": db_story.world_description,
        "genre": db_story.genre,
        "world_metadata": db_story.world_metadata
    })
    
    return db_story

@router.get("/", response_model=List[StoryResponse])
async def list_stories(
    current_user: User = Depends(get_current_user),  # Must be logged in
    db: Session = Depends(get_db)
):
    """List all available stories"""
    # Players see all stories (default + custom)
    # Admins see all stories
    stories = db.query(Story).all()
    return stories

@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get story by ID"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

class JoinStoryRequest(BaseModel):
    language: str = "en"

@router.post("/{story_id}/join", response_model=CharacterResponse)
async def join_story(
    story_id: str, 
    request: JoinStoryRequest,
    current_user: User = Depends(get_current_user),  # Auto-get user from token
    db: Session = Depends(get_db)
):
    """Join an existing story with a character"""
    # Verify story exists
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Check if user already has a character in this story
    existing = db.query(Character).filter(
        Character.user_id == current_user.id,
        Character.story_id == story_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already have a character in this story")
    
    # Get story context
    story_context = redis_client.get_story_context(story_id)
    if not story_context:
        story_context = {
            "world_description": story.world_description,
            "genre": story.genre,
            "world_metadata": story.world_metadata
        }
    
    # Use matchmaker agent to find insertion point
    character_info = {
        "name": current_user.name,
        "profession": current_user.profession,
        "description": current_user.description
    }
    insertion_point = await matchmaker_agent.find_insertion_point(
        story_context, 
        character_info,
        language=request.language
    )
    
    # Create character
    db_character = Character(
        user_id=current_user.id,
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
