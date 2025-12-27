from sqlalchemy import (
    Column, String, Text, Integer, DateTime,
    ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime
from app.core.database import Base
import uuid
import enum

# -------------------------------------------------
# Utilities
# -------------------------------------------------

def generate_uuid():
    return str(uuid.uuid4())

# -------------------------------------------------
# ENUM DEFINITIONS (Python)
# -------------------------------------------------

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

# -------------------------------------------------
# ENUM DEFINITIONS (PostgreSQL)
# ⚠️ create_type=False = Alembic gestirà la creazione
# -------------------------------------------------

user_role_enum = ENUM(UserRole, name="userrole", create_type=False)
quest_type_enum = ENUM(QuestType, name="questtype", create_type=False)
quest_status_enum = ENUM(QuestStatus, name="queststatus", create_type=False)
enemy_type_enum = ENUM(EnemyType, name="enemytype", create_type=False)
item_type_enum = ENUM(ItemType, name="itemtype", create_type=False)

# -------------------------------------------------
# MODELS
# -------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(user_role_enum, default=UserRole.PLAYER, nullable=False)

    name = Column(String, nullable=False)
    profession = Column(String)
    description = Column(Text)
    avatar_description = Column(Text)

    hp = Column(Integer, default=0)
    max_hp = Column(Integer, default=200)
    strength = Column(Integer, default=0)
    magic = Column(Integer, default=0)
    dexterity = Column(Integer, default=0)
    defense = Column(Integer, default=0)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    reset_token = Column(String)
    reset_token_expires = Column(DateTime)

    characters = relationship(
        "Character", back_populates="user", cascade="all, delete-orphan"
    )

class Story(Base):
    __tablename__ = "stories"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    world_description = Column(Text, nullable=False)
    genre = Column(String)
    current_state = Column(Text)
    world_metadata = Column(JSON)

    is_default = Column(Boolean, default=False)
    created_by = Column(String, ForeignKey("users.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    characters = relationship("Character", back_populates="story", cascade="all, delete-orphan")
    quests = relationship("Quest", back_populates="story", cascade="all, delete-orphan")
    enemies = relationship("Enemy", back_populates="story", cascade="all, delete-orphan")
    npcs = relationship("NPC", back_populates="story", cascade="all, delete-orphan")

class Character(Base):
    __tablename__ = "characters"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)

    insertion_point = Column(Text)
    status = Column(String, default="active")

    hunger = Column(Integer, default=100)
    thirst = Column(Integer, default=100)
    fatigue = Column(Integer, default=0)

    days_survived = Column(Integer, default=0)
    last_played_date = Column(DateTime)

    deaths = Column(Integer, default=0)
    can_resurrect = Column(Boolean, default=True)
    gold = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="characters")
    story = relationship("Story", back_populates="characters")
    inventory = relationship("Inventory", cascade="all, delete-orphan")

class Turn(Base):
    __tablename__ = "turns"

    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)

    user_action = Column(Text, nullable=False)
    narration = Column(Text, nullable=False)
    turn_number = Column(Integer, nullable=False)

    # Combat tracking
    was_combat = Column(Boolean, default=False)
    combat_result = Column(JSON)
    combat_enemy_id = Column(String, ForeignKey("enemies.id"))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    story = relationship("Story", back_populates="turns")
    character = relationship("Character", back_populates="turns")
    combat_enemy = relationship("Enemy")


class Quest(Base):
    __tablename__ = "quests"

    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    quest_type = Column(quest_type_enum, nullable=False)

    objectives = Column(JSON, default=list)

    xp_reward = Column(Integer, default=0)
    gold_reward = Column(Integer, default=0)
    item_rewards = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)

    story = relationship("Story", back_populates="quests")

class PlayerQuest(Base):
    __tablename__ = "player_quests"

    id = Column(String, primary_key=True, default=generate_uuid)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    quest_id = Column(String, ForeignKey("quests.id"), nullable=False)

    # ⚠️ ENUM PostgreSQL corretto
    status = Column(
        quest_status_enum,
        default=QuestStatus.NOT_STARTED,
        nullable=False
    )

    # Progress tracking
    objectives_completed = Column(JSON, default=list)
    progress_notes = Column(Text)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    character = relationship("Character", back_populates="player_quests")
    quest = relationship("Quest", back_populates="player_quests")


# -------------------- Enemy --------------------

class Enemy(Base):
    __tablename__ = "enemies"

    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text)
    enemy_type = Column(enemy_type_enum, default=EnemyType.COMMON)

    level = Column(Integer, default=1)
    hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)

    xp_reward = Column(Integer, default=0)
    gold_min = Column(Integer, default=0)
    gold_max = Column(Integer, default=0)
    loot_table = Column(JSON, default=list)
    image_url = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    story = relationship("Story", back_populates="enemies")

# -------------------- NPC --------------------

class NPC(Base):
    __tablename__ = "npcs"

    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text)
    image_url = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    story = relationship("Story", back_populates="npcs")

# -------------------- Item --------------------

class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    item_type = Column(item_type_enum, default=ItemType.MISC)
    description = Column(Text)

    hunger_restore = Column(Integer, default=0)
    thirst_restore = Column(Integer, default=0)
    fatigue_restore = Column(Integer, default=0)
    hp_restore = Column(Integer, default=0)

    gold_cost = Column(Integer, default=0)
    is_consumable = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    inventory_items = relationship(
        "Inventory", back_populates="item", cascade="all, delete-orphan"
    )

# -------------------- Inventory --------------------

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String, primary_key=True, default=generate_uuid)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    item_id = Column(String, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=1)

    created_at = Column(DateTime, default=datetime.utcnow)

    character = relationship("Character")
    item = relationship("Item", back_populates="inventory_items")
