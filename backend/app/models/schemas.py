from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    profession: Optional[str] = None
    description: Optional[str] = None
    avatar_description: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    profession: Optional[str]
    description: Optional[str]
    avatar_description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class StoryCreate(BaseModel):
    title: str
    world_description: str
    genre: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class StoryResponse(BaseModel):
    id: str
    title: str
    world_description: str
    genre: Optional[str]
    current_state: Optional[str]
    metadata: Optional[Dict[str, Any]]
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
