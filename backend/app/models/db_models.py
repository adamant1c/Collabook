from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid
import enum

def generate_uuid():
    return str(uuid.uuid4())

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PLAYER = "player"

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

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    world_description = Column(Text, nullable=False)
    genre = Column(String, nullable=True)
    current_state = Column(Text, nullable=True)
    world_metadata = Column(JSON, nullable=True)
    
    # World management
    is_default = Column(Boolean, default=False)  # True for 3 predefined worlds
    created_by = Column(String, ForeignKey("users.id"), nullable=True)  # NULL for defaults
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    characters = relationship("Character", back_populates="story", cascade="all, delete-orphan")
    turns = relationship("Turn", back_populates="story", cascade="all, delete-orphan")

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    insertion_point = Column(Text, nullable=True)
    status = Column(String, default="active")  # active, inactive, dead
    
    # Survival stats (Phase 5)
    hunger = Column(Integer, default=100)
    thirst = Column(Integer, default=100)
    fatigue = Column(Integer, default=0)
    
    # Death tracking
    deaths = Column(Integer, default=0)
    can_resurrect = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="characters")
    story = relationship("Story", back_populates="characters")
    turns = relationship("Turn", back_populates="character", cascade="all, delete-orphan")

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
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    story = relationship("Story", back_populates="turns")
    character = relationship("Character", back_populates="turns")
