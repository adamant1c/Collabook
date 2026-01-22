from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid
import enum

def generate_uuid():
    return str(uuid.uuid4())

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    PLAYER = "PLAYER"

class QuestType(str, enum.Enum):
    MAIN = "MAIN"
    SIDE = "SIDE"

class QuestStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class EnemyType(str, enum.Enum):
    COMMON = "COMMON"
    ELITE = "ELITE"
    BOSS = "BOSS"

class ItemType(str, enum.Enum):
    FOOD = "FOOD"
    WATER = "WATER"
    POTION = "POTION"
    MISC = "MISC"

class User(Base):
    __tablename__ = "users"
    
    # Authentication
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.PLAYER, nullable=False)
    
    # Character Info
    name = Column(String, nullable=False)  # Character display name
    profession = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    avatar_description = Column(Text, nullable=True)
    
    # RPG Stats (Phase 2 - initialized to 0 for now)
    hp = Column(Integer, default=0)
    max_hp = Column(Integer, default=200)
    strength = Column(Integer, default=0)
    magic = Column(Integer, default=0)
    dexterity = Column(Integer, default=0)
    defense = Column(Integer, default=0)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    
    # Account Management
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # Relationships
    characters = relationship("Character", back_populates="user", cascade="all, delete-orphan")

    @property
    def joined_stories(self):
        return [char.story_id for char in self.characters]

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    world_description = Column(Text, nullable=False)
    genre = Column(String, nullable=True)
    
    # Localization (Italian)
    title_it = Column(String, nullable=True)
    world_description_it = Column(Text, nullable=True)
    genre_it = Column(String, nullable=True)
    
    world_metadata = Column(JSON, nullable=True)
    survival_goal_days = Column(Integer, default=10) # Survival Mode Goal
    
    # World management
    is_default = Column(Boolean, default=False)  # True for 3 predefined worlds
    created_by = Column(String, ForeignKey("users.id"), nullable=True)  # NULL for defaults
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    characters = relationship("Character", back_populates="story", cascade="all, delete-orphan")
    turns = relationship("Turn", back_populates="story", cascade="all, delete-orphan")
    quests = relationship("Quest", back_populates="story", cascade="all, delete-orphan")
    enemies = relationship("Enemy", back_populates="story", cascade="all, delete-orphan")
    npcs = relationship("NPC", back_populates="story", cascade="all, delete-orphan")

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    insertion_point = Column(Text, nullable=True)
    status = Column(String, default="active")  # active, inactive, dead
    
    # Game state summary (moved from Story)
    current_state = Column(Text, nullable=True)
    
    # Survival stats (Phase 5)
    hunger = Column(Integer, default=100)
    thirst = Column(Integer, default=100)
    fatigue = Column(Integer, default=0)
    
    # Survival Mode (New)
    days_survived = Column(Integer, default=0)
    last_played_date = Column(DateTime, nullable=True)
    
    # Death tracking (Phase 4 - Combat)
    deaths = Column(Integer, default=0)
    can_resurrect = Column(Boolean, default=True)
    
    # Currency (Phase 3)
    gold = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="characters")
    story = relationship("Story", back_populates="characters")
    turns = relationship("Turn", back_populates="character", cascade="all, delete-orphan")
    player_quests = relationship("PlayerQuest", back_populates="character", cascade="all, delete-orphan")

class Turn(Base):
    __tablename__ = "turns"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    user_action = Column(Text, nullable=False)
    narration = Column(Text, nullable=False)
    turn_number = Column(Integer, nullable=False)
    
    # Combat tracking (Phase 4)
    was_combat = Column(Boolean, default=False)
    combat_result = Column(JSON, nullable=True)  # Store combat details
    combat_enemy_id = Column(String, ForeignKey("enemies.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    story = relationship("Story", back_populates="turns")
    character = relationship("Character", back_populates="turns")
    combat_enemy = relationship("Enemy")

class Quest(Base):
    __tablename__ = "quests"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    
    # Quest info
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    quest_type = Column(SQLEnum(QuestType), nullable=False)
    
    # Objectives (JSON list of objectives)
    # Example: [{"id": "obj1", "description": "Find the ancient tome", "completed": false}]
    objectives = Column(JSON, nullable=False, default=list)
    
    # Rewards
    xp_reward = Column(Integer, default=0)
    gold_reward = Column(Integer, default=0)
    item_rewards = Column(JSON, nullable=True, default=list)  # Phase 3B - Inventory
    
    # Quest giver NPC
    quest_giver = Column(String, nullable=True)
    quest_giver_description = Column(Text, nullable=True)
    
    # Requirements
    is_repeatable = Column(Boolean, default=False)
    required_level = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    story = relationship("Story", back_populates="quests")
    player_quests = relationship("PlayerQuest", back_populates="quest", cascade="all, delete-orphan")

class PlayerQuest(Base):
    __tablename__ = "player_quests"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    quest_id = Column(String, ForeignKey("quests.id"), nullable=False)
    
    status = Column(SQLEnum(QuestStatus), default=QuestStatus.NOT_STARTED)
    
    # Progress tracking
    objectives_completed = Column(JSON, default=list)  # List of completed objective IDs
    progress_notes = Column(Text, nullable=True)  # LLM-generated notes about progress
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    character = relationship("Character", back_populates="player_quests")
    quest = relationship("Quest", back_populates="player_quests")

class Enemy(Base):
    __tablename__ = "enemies"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    
    # Enemy info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    enemy_type = Column(SQLEnum(EnemyType), default=EnemyType.COMMON)
    
    # Combat stats
    level = Column(Integer, default=1)
    hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)  # For display
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    
    # Loot rewards
    xp_reward = Column(Integer, default=0)
    gold_min = Column(Integer, default=0)
    gold_max = Column(Integer, default=0)
    loot_table = Column(JSON, nullable=True, default=list)  # Future: item drops
    image_url = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    story = relationship("Story", back_populates="enemies")

class NPC(Base):
    """Non-Player Characters that are not enemies but context for DM"""
    __tablename__ = "npcs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    story = relationship("Story", back_populates="npcs")

class Item(Base):
    """Items for survival mechanics (food, water, potions)"""
    __tablename__ = "items"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    item_type = Column(SQLEnum(ItemType), default=ItemType.MISC)
    description = Column(Text, nullable=True)
    
    # Restoration effects
    hunger_restore = Column(Integer, default=0)  # How much hunger it restores
    thirst_restore = Column(Integer, default=0)  # How much thirst it restores
    fatigue_restore = Column(Integer, default=0)  # How much fatigue it reduces
    hp_restore = Column(Integer, default=0)       # HP healing
    
    # Properties
    gold_cost = Column(Integer, default=0)
    is_consumable = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    inventory_items = relationship("Inventory", back_populates="item", cascade="all, delete-orphan")

class Inventory(Base):
    """Character inventory for items"""
    __tablename__ = "inventory"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    item_id = Column(String, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    character = relationship("Character")
    item = relationship("Item", back_populates="inventory_items")
