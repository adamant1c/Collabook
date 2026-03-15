from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Dict, Any, List
import re
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

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

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
    user_id: int
    story_id: str
    insertion_point: Optional[str]
    status: str
    gold: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
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

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

# Character/Story schemas
class StoryCreate(BaseModel):
    title: str
    world_description: str
    genre: Optional[str] = None
    
    # Localization
    title_it: Optional[str] = None
    world_description_it: Optional[str] = None
    genre_it: Optional[str] = None
    
    world_metadata: Optional[Dict[str, Any]] = None
    survival_goal_days: Optional[int] = 10

class StoryResponse(BaseModel):
    id: str
    title: str
    world_description: str
    genre: Optional[str]
    
    # Localization
    title_it: Optional[str]
    world_description_it: Optional[str]
    genre_it: Optional[str]
    
    world_metadata: Optional[Dict[str, Any]]
    survival_goal_days: int
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PublicEntity(BaseModel):
    name: str
    description: Optional[str]
    image_url: Optional[str]

class PublicMap(BaseModel):
    name: str
    name_it: Optional[str] = None
    description: Optional[str] = None
    description_it: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class PublicStoryResponse(BaseModel):
    id: str
    title: str
    world_description: str
    genre: Optional[str]
    title_it: Optional[str]
    world_description_it: Optional[str]
    genre_it: Optional[str]
    entities: List[PublicEntity] = []
    maps: List[PublicMap] = []

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
    detected_entities: List[Dict[str, Any]] = []
    suggested_actions: List[str] = []
    player_stats: Optional[Dict[str, Any]] = None
    
    # Map context
    current_location_id: Optional[str] = None
    current_location_name: Optional[str] = None
    nearby_locations: List[Dict[str, str]] = []  # [{"id": "...", "name": "..."}]
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


# Map schemas
class MapNodeResponse(BaseModel):
    id: str
    story_id: str
    parent_id: Optional[str] = None
    name: str
    name_it: Optional[str] = None
    description: Optional[str] = None
    description_it: Optional[str] = None
    node_type: str
    x: int
    y: int
    icon: Optional[str] = None
    is_starting_location: bool
    children: List['MapNodeResponse'] = Field(default_factory=list)

    @field_validator('children', mode='before')
    @classmethod
    def validate_children(cls, v):
        if v is None:
            return []
        return v

    class Config:
        from_attributes = True

class MapCharacterPosition(BaseModel):
    character_id: str
    name: str
    location_id: str
    location_name: str

class MapEdgeResponse(BaseModel):
    id: str
    story_id: str
    from_node_id: str
    to_node_id: str
    travel_description: Optional[str] = None
    bidirectional: bool

    class Config:
        from_attributes = True

class MapResponse(BaseModel):
    nodes: List[MapNodeResponse]
    edges: List[MapEdgeResponse]
    characters: List[MapCharacterPosition] = []

class MoveRequest(BaseModel):
    character_id: str
    target_node_id: str
