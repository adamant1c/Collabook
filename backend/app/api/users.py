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
        "character": {
            "id": current_user.character.id,
            "name": current_user.character.name,
            "profession": current_user.character.profession,
            "description": current_user.character.description,
            "level": current_user.character.level,
            "xp": current_user.character.xp,
            "hp": current_user.character.hp,
            "max_hp": current_user.character.max_hp
        } if current_user.character else None
    }

@router.patch("/character/{character_id}")
async def update_character(
    character_id: str,
    update_data: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update character profession and description"""
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")
    
    # Update fields
    if update_data.profession:
        character.profession = update_data.profession
    if update_data.description:
        character.description = update_data.description
    
    db.commit()
    db.refresh(character)
    
    return {
        "id": character.id,
        "name": character.name,
        "profession": character.profession,
        "description": character.description,
        "level": character.level,
        "xp": character.xp,
        "hp": character.hp,
        "max_hp": character.max_hp
    }
