"""
User management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.schemas import UserCreate, UserResponse
from app.models.db_models import User, Character
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/users", tags=["users"])

class CharacterUpdate(BaseModel):
    profession: Optional[str] = None
    description: Optional[str] = None

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new anonymous user profile"""
    db_user = User(
        name=user.name,
        profession=user.profession,
        description=user.description,
        avatar_description=user.avatar_description
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/me")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        # Map User fields to "character" object for frontend compatibility
        # The User model holds the global character stats and profile
        "character": {
            "id": current_user.id,  # Use User ID as Character ID for global profile
            "name": current_user.name,
            "profession": current_user.profession,
            "description": current_user.description,
            "level": current_user.level,
            "xp": current_user.xp,
            "hp": current_user.hp,
            "max_hp": current_user.max_hp
        }
    }

@router.patch("/character/{character_id}")
async def update_character(
    character_id: str,
    update_data: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's character profile (profession, description)"""
    # We update the User object directly as it holds the global character info
    
    # Update fields on User
    if update_data.profession:
        current_user.profession = update_data.profession
    if update_data.description:
        current_user.description = update_data.description
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "name": current_user.name,
        "profession": current_user.profession,
        "description": current_user.description,
        "level": current_user.level,
        "xp": current_user.xp,
        "hp": current_user.hp,
        "max_hp": current_user.max_hp
    }
