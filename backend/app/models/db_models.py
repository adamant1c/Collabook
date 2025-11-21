from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    profession = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    avatar_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    characters = relationship("Character", back_populates="user")

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    world_description = Column(Text, nullable=False)
    genre = Column(String, nullable=True)
    current_state = Column(Text, nullable=True)  # Summary of current plot
    metadata = Column(JSON, nullable=True)  # Additional world rules, settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    characters = relationship("Character", back_populates="story")
    turns = relationship("Turn", back_populates="story")

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    insertion_point = Column(Text, nullable=True)  # Where character was inserted
    status = Column(String, default="active")  # active, inactive, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="characters")
    story = relationship("Story", back_populates="characters")
    turns = relationship("Turn", back_populates="character")

class Turn(Base):
    __tablename__ = "turns"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    user_action = Column(Text, nullable=False)  # What the user chose to do
    narration = Column(Text, nullable=False)  # LLM response
    turn_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    story = relationship("Story", back_populates="turns")
    character = relationship("Character", back_populates="turns")
