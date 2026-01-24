
import sys
import os
import uuid
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models.db_models import User, Story, Character, Turn, UserRole
from app.models.schemas import InteractionRequest

# Ensure tables exist (they should, but just in case)
Base.metadata.create_all(bind=engine)

def verify_win_condition_fix():
    db = SessionLocal()
    try:
        # 1. Setup: Create a test user, story, and character
        username = f"verify_win_{uuid.uuid4().hex[:6]}"
        user = User(
            username=username,
            email=f"{username}@test.com",
            password_hash="fakehash",
            name="Verify User",
            role=UserRole.PLAYER,
            hp=100,
            max_hp=100
        )
        db.add(user)
        db.flush()

        story = Story(
            title="Win Test Story",
            world_description="A world to test winning",
            survival_goal_days=2
        )
        db.add(story)
        db.flush()

        # Character who is 1 day away from winning
        character = Character(
            user_id=user.id,
            story_id=story.id,
            days_survived=1,
            last_played_date=datetime.utcnow() - timedelta(days=1)
        )
        db.add(character)
        db.commit()
        db.refresh(character)

        print(f"✅ Setup complete. Character ID: {character.id}, Days survived: {character.days_survived}")

        # 2. Simulate interaction that triggers win condition
        from fastapi.testclient import TestClient
        from unittest.mock import AsyncMock, MagicMock
        import sys
        
        # Mock the entire llm_client module and its instance
        mock_llm_module = MagicMock()
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value="CONGRATULATIONS! You have survived!")
        mock_llm_module.llm_client = mock_llm_client
        sys.modules['app.core.llm_client'] = mock_llm_module

        # Mock Redis client
        mock_redis_module = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_client.get_active_characters.return_value = []
        mock_redis_module.redis_client = mock_redis_client
        sys.modules['app.core.redis_client'] = mock_redis_module

        from app.main import app
        from app.api.auth import get_current_user

        # Mock auth to return our test user
        app.dependency_overrides[get_current_user] = lambda: user

        client = TestClient(app)
        
        print("🚀 Sending interaction request to trigger win condition...")
        response = client.post("/interact", json={
            "character_id": character.id,
            "user_action": "I survive another day!"
        })

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response: {data}")
            assert "turn_id" in data
            assert data["turn_id"] is not None
            assert "CONGRATULATIONS" in data["narration"]
            print("✨ SUCCESS: turn_id is populated in the win condition response!")
            
            # 3. Verify turn is actually saved in DB
            turn = db.query(Turn).filter(Turn.id == data["turn_id"]).first()
            assert turn is not None
            assert turn.character_id == character.id
            print(f"✨ SUCCESS: Turn {turn.id} was correctly persisted in the database!")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            raise Exception("Failed to trigger win condition")

    finally:
        db.close()
        # Clear overrides
        from app.api.auth import get_current_user
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]

if __name__ == "__main__":
    verify_win_condition_fix()
