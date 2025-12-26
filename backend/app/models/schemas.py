from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
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

class CharacterUpdate(BaseModel):
    profession: Optional[str] = None
    description: Optional[str] = None
    strength: Optional[int] = None
    magic: Optional[int] = None
    dexterity: Optional[int] = None
    defense: Optional[int] = None
    hp: Optional[int] = None
    max_hp: Optional[int] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    """Schema for creating a new user (admin only)"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1, max_length=100)
    role: str = "player"  # admin or player

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CharacterCreate(BaseModel):
    story_id: Optional[str] = None  # Optional since story_id comes from URL path in join_story

class CharacterResponse(BaseModel):
    id: str
    user_id: str
    story_id: str
    insertion_point: Optional[str]
    status: str
    gold: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    name: str
    profession: Optional[str]
    description: Optional[str]
    avatar_description: Optional[str]
    characters: List[CharacterResponse] = []
    
    # RPG Stats
    hp: int
    max_hp: int
    strength: int
    magic: int
    dexterity: int
    defense: int
    xp: int
    level: int
    
    created_at: datetime
    
    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

# Character/Story schemas
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



class InteractionRequest(BaseModel):
    character_id: str
    user_action: str
    language: Optional[str] = "en"

class InteractionResponse(BaseModel):
    turn_id: str
    narration: str
    turn_number: int
    quest_hint: Optional[str] = None
    survival_warnings: List[str] = []
    critical_condition: bool = False
    # Phase 3: LLM can suggest quest completion
    
    class Config:
        from_attributes = True

# Quest schemas (Phase 3)
class QuestObjective(BaseModel):
    id: str
    description: str

class QuestCreate(BaseModel):
    story_id: str
    title: str
    description: str
    quest_type: str  # "main" or "side"
    objectives: List[QuestObjective]
    xp_reward: int = 0
    gold_reward: int = 0
    quest_giver: Optional[str] = None
    quest_giver_description: Optional[str] = None
    required_level: int = 1
    is_repeatable: bool = False

class QuestResponse(BaseModel):
    id: str
    story_id: str
    title: str
    description: str
    quest_type: str
    objectives: List[Dict[str, Any]]
    xp_reward: int
    gold_reward: int
    quest_giver: Optional[str]
    quest_giver_description: Optional[str]
    required_level: int
    is_repeatable: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PlayerQuestResponse(BaseModel):
    id: str
    quest: QuestResponse
    status: str
    objectives_completed: List[str]
    progress_notes: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class QuestAccept(BaseModel):
    character_id: str

class QuestComplete(BaseModel):
    character_id: str

# Combat schemas (Phase 4)
class CombatEncounterCheck(BaseModel):
    character_id: str
    turn_number: int = 1

class CombatActionRequest(BaseModel):
    character_id: str
    action: str  # "attack", "magic", "defend", "flee"

class EnemyInfo(BaseModel):
    name: str
    description: Optional[str]
    level: int
    hp: int
    max_hp: int
    type: str  # "common", "elite", "boss"
    image_url: Optional[str] = None

class CombatResult(BaseModel):
    success: bool
    message: str
    combat_log: List[str]
    
    # Combat state
    combat_continues: bool = False
    player_hp: Optional[int] = None
    player_max_hp: Optional[int] = None
    enemy_hp: Optional[int] = None
    enemy_max_hp: Optional[int] = None
    
    # Outcomes
    victory: bool = False
    defeat: bool = False
    fled: bool = False
    
    # Rewards (on victory)
    xp_gained: Optional[int] = None
    gold_gained: Optional[int] = None
    level_up: bool = False
    new_level: Optional[int] = None
    
    # Death/Resurrection
    resurrected: bool = False
    permanent_death: bool = False
    penalty: Optional[str] = None

# NPC schemas
class NPCBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class NPCCreate(NPCBase):
    story_id: str

class NPCResponse(NPCBase):
    id: str
    story_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Item schemas (Phase 5)
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    item_type: str  # food, water, potion, misc
    description: Optional[str] = None
    hunger_restore: int = 0
    thirst_restore: int = 0
    fatigue_restore: int = 0
    hp_restore: int = 0
    gold_cost: int = 0
    is_consumable: bool = True

class ItemResponse(BaseModel):
    id: str
    name: str
    item_type: str
    description: Optional[str]
    hunger_restore: int
    thirst_restore: int
    fatigue_restore: int
    hp_restore: int
    gold_cost: int
    is_consumable: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class InventoryResponse(BaseModel):
    id: str
    character_id: str
    item_id: str
    quantity: int
    item: ItemResponse
    created_at: datetime
    
    class Config:
        from_attributes = True

class UseItemRequest(BaseModel):
    character_id: str
    item_id: str

class RestRequest(BaseModel):
    character_id: str
    hours: int = Field(default=8, ge=1, le=24)
