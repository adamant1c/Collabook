from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

# User schemas
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1, max_length=100)
    profession: Optional[str] = None
    description: Optional[str] = None
    avatar_description: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    name: str
    profession: Optional[str]
    description: Optional[str]
    avatar_description: Optional[str]
    level: int
    xp: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

# Character/Story schemas (updated)
class StoryCreate(BaseModel):
    title: str
    world_description: str
    genre: Optional[str] = None
    world_metadata: Optional[Dict[str, Any]] = None

class StoryResponse(BaseModel):
    id: str
    title: str
    world_description: str
    genre: Optional[str]
    current_state: Optional[str]
    world_metadata: Optional[Dict[str, Any]]
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CharacterCreate(BaseModel):
    story_id: str

class CharacterResponse(BaseModel):
    id: str
    user_id: str
    story_id: str
    insertion_point: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class InteractionRequest(BaseModel):
    character_id: str
    user_action: str

class InteractionResponse(BaseModel):
    turn_id: str
    narration: str
    turn_number: int
    
    class Config:
        from_attributes = True
