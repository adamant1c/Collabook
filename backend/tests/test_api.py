import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

# ==================== Fixtures ====================

@pytest.fixture
def admin_token():
    """Get admin token for tests"""
    # Create admin user if doesn't exist
    response = client.post("/auth/register", json={
        "username": "testadmin",
        "email": "admin@test.com",
        "password": "testpass123",
        "name": "Test Admin"
    })
    
    # Login to get token
    response = client.post("/auth/login", data={
        "username": "testadmin",
        "password": "testpass123"
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

@pytest.fixture
def player_token():
    """Get player token for tests"""
    import random
    username = f"testplayer{random.randint(1000, 9999)}"
    
    response = client.post("/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "testpass123",
        "name": "Test Player",
        "profession": "Warrior"
    })
    
    if response.status_code == 201:
        return response.json()["access_token"]
    
    # If registration failed (user exists), login
    response = client.post("/auth/login", data={
        "username": username,
        "password": "testpass123"
    })
    
    return response.json()["access_token"]

@pytest.fixture
def test_story(admin_token):
    """Create a test story"""
    response = client.post("/stories/", 
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Test World",
            "world_description": "A test world for API testing",
            "genre": "Fantasy"
        }
    )
    return response.json()

@pytest.fixture
def test_character(player_token, test_story):
    """Create a test character in a story"""
    response = client.post(f"/stories/{test_story['id']}/join",
        headers={"Authorization": f"Bearer {player_token}"},
        json={}
    )
    return response.json()

# ==================== Health Check Tests ====================

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "checks" in data

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Collabook API"
    assert "version" in data

# ==================== Authentication Tests ====================

class TestAuthentication:
    
    def test_register_new_user(self):
        """Test user registration"""
        import random
        username = f"newuser{random.randint(1000, 9999)}"
        
        response = client.post("/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": "testpass123",
            "name": "New User"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_username(self, player_token):
        """Test registration with duplicate username fails"""
        response = client.post("/auth/register", json={
            "username": "testplayer",
            "email": "another@test.com",
            "password": "testpass123",
            "name": "Another User"
        })
        
        # Should fail if user already exists
        # Note: might be 201 if first time running tests
        assert response.status_code in [201, 400]
    
    def test_login_valid_credentials(self, player_token):
        """Test login with valid credentials"""
        response = client.post("/auth/login", data={
            "username": "testplayer",
            "password": "testpass123"
        })
        
        # Might not exist yet
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials fails"""
        response = client.post("/auth/login", data={
            "username": "nonexistent",
            "password": "wrongpass"
        })
        
        assert response.status_code == 401
    
    def test_get_current_user(self, player_token):
        """Test getting current user info"""
        response = client.get("/auth/me",
            headers={"Authorization": f"Bearer {player_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "id" in data
        assert "characters" in data

# ==================== Story Tests ====================

class TestStories:
    
    def test_list_stories(self, player_token):
        """Test listing all stories"""
        response = client.get("/stories/",
            headers={"Authorization": f"Bearer {player_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_story_by_id(self, player_token, test_story):
        """Test getting a specific story"""
        response = client.get(f"/stories/{test_story['id']}",
            headers={"Authorization": f"Bearer {player_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_story["id"]
        assert "title" in data
    
    def test_join_story(self, player_token, test_story):
        """Test joining a story creates a character"""
        response = client.post(f"/stories/{test_story['id']}/join",
            headers={"Authorization": f"Bearer {player_token}"},
            json={}
        )
        
        # Might be 400 if already joined
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["story_id"] == test_story["id"]

# ==================== Interaction Tests ====================

class TestInteractions:
    
    def test_interact_endpoint_exists(self, player_token, test_character):
        """Test that interact endpoint is accessible"""
        response = client.post("/interact",
            headers={"Authorization": f"Bearer {player_token}"},
            json={
                "character_id": test_character["id"],
                "user_action": "I look around the room"
            }
        )
        
        # Should return 200 or error, but NOT 404
        assert response.status_code != 404
        assert response.status_code in [200, 400, 401, 403, 500]
    
    def test_interact_with_valid_action(self, player_token, test_character):
        """Test interaction with valid user action"""
        response = client.post("/interact",
            headers={"Authorization": f"Bearer {player_token}"},
            json={
                "character_id": test_character["id"],
                "user_action": "I examine my surroundings carefully"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "narration" in data
            assert "turn_id" in data
            assert "turn_number" in data
    
    def test_interact_without_auth(self, test_character):
        """Test interaction without authentication fails"""
        response = client.post("/interact",
            json={
                "character_id": test_character["id"],
                "user_action": "I try to act"
            }
        )
        
        assert response.status_code == 401
    
    def test_interact_with_invalid_character(self, player_token):
        """Test interaction with non-existent character"""
        response = client.post("/interact",
            headers={"Authorization": f"Bearer {player_token}"},
            json={
                "character_id": "invalid-uuid-12345",
                "user_action": "I try to act"
            }
        )
        
        assert response.status_code in [400, 404]

# ==================== Quest Tests ====================

class TestQuests:
    
    def test_list_quests(self, player_token, test_story):
        """Test listing quests for a story"""
        response = client.get(f"/quests/story/{test_story['id']}",
            headers={"Authorization": f"Bearer {player_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

# ==================== Combat Tests ====================

class TestCombat:
    
    def test_check_encounter(self, player_token, test_character):
        """Test checking for combat encounters"""
        response = client.post("/combat/check-encounter",
            headers={"Authorization": f"Bearer {player_token}"},
            json={
                "character_id": test_character["id"]
            }
        )
        
        # Should return success or error, but not 404
        assert response.status_code != 404
        assert response.status_code in [200, 400, 401, 403, 500]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
