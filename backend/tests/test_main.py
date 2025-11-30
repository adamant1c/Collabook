"""
Test Suite for Collabook RPG Backend

Run with: pytest backend/tests/
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.db_models import User, Character, Story

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    """Create test user"""
    from app.core.security import hash_password
    
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("password123"),
        name="Test User",
        role="player"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    """Get auth token for test user"""
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    return response.json()["access_token"]

# ==================== Authentication Tests ====================

def test_register_success():
    """Test successful user registration"""
    response = client.post("/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123",
        "name": "New User"
    })
    # Allow 200 or 201
    assert response.status_code in [200, 201]
    data = response.json()
    assert "access_token" in data

def test_register_duplicate_username(test_user):
    """Test registration with duplicate username"""
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "another@example.com",
        "password": "password123",
        "name": "Another User"
    })
    assert response.status_code == 400

def test_login_success(test_user):
    """Test successful login"""
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_wrong_password(test_user):
    """Test login with wrong password"""
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_current_user(auth_token):
    """Test getting current user info"""
    response = client.get("/auth/me", headers={
        "Authorization": f"Bearer {auth_token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

# ==================== Content Filter Tests ====================

def test_content_filter_profanity():
    """Test profanity detection"""
    from app.core.content_filter import validate_user_input
    
    result = validate_user_input("This is fucking inappropriate")
    assert not result["is_valid"]
    assert "profanity" in [v.value for v in result["violations"].keys()]

def test_content_filter_clean_input():
    """Test clean input passes"""
    from app.core.content_filter import validate_user_input
    
    result = validate_user_input("I explore the ancient castle")
    assert result["is_valid"]
    assert len(result["violations"]) == 0

def test_content_filter_violence():
    """Test violence filtering"""
    from app.core.content_filter import validate_user_input, FilterLevel
    
    result = validate_user_input("I eviscerate the monster", FilterLevel.STRICT)
    assert not result["is_valid"]

def test_content_sanitization():
    """Test LLM output sanitization"""
    from app.core.content_filter import sanitize_llm_output
    
    text = "The hero attacks with fucking fury"
    sanitized, modified = sanitize_llm_output(text)
    assert modified
    assert "[FILTERED]" in sanitized

# ==================== Combat Tests ====================

def test_dice_roll():
    """Test dice rolling"""
    from app.core.combat import roll_dice
    
    for _ in range(100):
        result = roll_dice(1, 20)
        assert 1 <= result <= 20

def test_calculate_modifier():
    """Test stat modifier calculation"""
    from app.core.combat import stat_modifier
    
    assert stat_modifier(10) == 0
    assert stat_modifier(14) == 2
    assert stat_modifier(18) == 4
    assert stat_modifier(6) == -2

# ==================== Survival Tests ====================

def test_survival_penalties():
    """Test survival stat penalties"""
    from app.core.survival import get_survival_penalties
    from app.models.db_models import Character
    
    char = Character(hunger=20, thirst=30, fatigue=80)
    penalties = get_survival_penalties(char)
    
    assert penalties["strength"] < 0
    assert penalties["dexterity"] < 0

def test_survival_update():
    """Test survival stats update"""
    from app.core.survival import update_survival_stats
    from app.models.db_models import Character
    
    char = Character(hunger=100, thirst=100, fatigue=0)
    update_survival_stats(char, turns_elapsed=1)
    
    assert char.hunger == 95  # -5
    assert char.thirst == 92  # -8
    assert char.fatigue == 3  # +3

# ==================== Localization Tests ====================

def test_translation_en():
    """Test English translation"""
    from frontend.localization import t, Language
    
    assert t("welcome", Language.EN) == "Welcome to Collabook RPG!"
    assert t("hunger", Language.EN) == "Hunger"

def test_translation_it():
    """Test Italian translation"""
    from frontend.localization import t, Language
    
    assert t("welcome", Language.IT) == "Benvenuto a Collabook RPG!"
    assert t("hunger", Language.IT) == "Fame"

def test_translation_fallback():
    """Test fallback for missing key"""
    from frontend.localization import t
    
    result = t("nonexistent_key")
    assert "[nonexistent_key]" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
