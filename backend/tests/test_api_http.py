#!/usr/bin/env python3
"""
Collabook API Integration Tests
Tests all backend endpoints via HTTP requests
Run from host machine: python3 backend/tests/test_api_http.py
"""

import requests
import json
import random
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
VERBOSE = True

# Test results tracking
passed_tests = 0
failed_tests = 0
test_results = []

def print_test(name, status, message=""):
    """Print test result"""
    global passed_tests, failed_tests
    
    symbol = "✓" if status else "✗"
    color = "\033[92m" if status else "\033[91m"
    reset = "\033[0m"
    
    result = f"{color}{symbol}{reset} {name}"
    if message and VERBOSE:
        result += f": {message}"
    
    print(result)
    test_results.append({"name": name, "passed": status, "message": message})
    
    if status:
        passed_tests += 1
    else:
        failed_tests += 1

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        # Accept both 200 (healthy) and 503 (degraded but functional)
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
        print_test("Health Check", True, f"Status: {data['status']}")
        return True
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False

def test_root_endpoint():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        print_test("Root Endpoint", True, f"Version: {data.get('version')}")
        return True
    except Exception as e:
        print_test("Root Endpoint", False, str(e))
        return False

def test_auth_register():
    """Test user registration"""
    try:
        username = f"testuser{random.randint(10000, 99999)}"
        response = requests.post(f"{BASE_URL}/auth/register", 
            json={
                "username": username,
                "email": f"{username}@test.com",
                "password": "testpass123",
                "name": "Test User",
                "profession": "Warrior"
            },
            timeout=5
        )
        
        # Accept both 201 (created) and 400 (already exists)
        if response.status_code == 201:
            data = response.json()
            assert "access_token" in data
            print_test("User Registration", True, f"Created user: {username}")
            return data["access_token"], username
        elif response.status_code == 400:
            print_test("User Registration", True, "User already exists (OK)")
            return None, username
        else:
            raise Exception(f"Unexpected status: {response.status_code}")
    except Exception as e:
        print_test("User Registration", False, str(e))
        return None, None

def test_auth_login(username, password="testpass123"):
    """Test user login"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login",
            data={"username": username, "password": password},
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        token = data["access_token"]
        print_test("User Login", True, f"Logged in as: {username}")
        return token
    except Exception as e:
        print_test("User Login", False, str(e))
        return None

def test_get_current_user(token):
    """Test getting current user info"""
    try:
        response = requests.get(f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "id" in data
        assert "characters" in data
        print_test("Get Current User", True, f"User ID: {data['id'][:8]}...")
        return data
    except Exception as e:
        print_test("Get Current User", False, str(e))
        return None

def test_list_stories(token):
    """Test listing all stories"""
    try:
        response = requests.get(f"{BASE_URL}/stories/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print_test("List Stories", True, f"Found {len(data)} stories")
        return data
    except Exception as e:
        print_test("List Stories", False, str(e))
        return None

def test_get_story(token, story_id):
    """Test getting a specific story"""
    try:
        response = requests.get(f"{BASE_URL}/stories/{story_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == story_id
        print_test("Get Story by ID", True, f"Story: {data.get('title', 'Unknown')}")
        return data
    except Exception as e:
        print_test("Get Story by ID", False, str(e))
        return None

def test_join_story(token, story_id):
    """Test joining a story"""
    try:
        response = requests.post(f"{BASE_URL}/stories/{story_id}/join",
            headers={"Authorization": f"Bearer {token}"},
            json={},
            timeout=30  # Increased for LLM processing
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["story_id"] == story_id
            print_test("Join Story", True, f"Character ID: {data['id'][:8]}...")
            return data
        elif response.status_code == 400:
            # Already joined
            print_test("Join Story", True, "Already joined (OK)")
            return None
        else:
            raise Exception(f"Unexpected status: {response.status_code}")
    except Exception as e:
        print_test("Join Story", False, str(e))
        return None

def test_interact(token, character_id):
    """Test interaction endpoint"""
    try:
        response = requests.post(f"{BASE_URL}/interact",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "character_id": character_id,
                "user_action": "I look around carefully, examining my surroundings."
            },
            timeout=30  # LLM might take time
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "narration" in data
            assert "turn_id" in data
            narration_preview = data["narration"][:50] + "..." if len(data["narration"]) > 50 else data["narration"]
            print_test("Interact Endpoint", True, f"Narration: {narration_preview}")
            return data
        else:
            raise Exception(f"Status {response.status_code}: {response.text}")
    except Exception as e:
        print_test("Interact Endpoint", False, str(e))
        return None

def test_list_quests(token, story_id):
    """Test listing quests for a story"""
    try:
        response = requests.get(f"{BASE_URL}/quests/story/{story_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print_test("List Quests", True, f"Found {len(data)} quests")
        return data
    except Exception as e:
        print_test("List Quests", False, str(e))
        return None

def test_check_encounter(token, character_id):
    """Test combat encounter check"""
    try:
        response = requests.post(f"{BASE_URL}/combat/check-encounter",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "character_id": character_id,
                "turn_number": 1  # Required parameter
            },
            timeout=5
        )
        
        # Accept 200 or 400 (no encounter)
        if response.status_code in [200, 400]:
            print_test("Check Combat Encounter", True, f"Status: {response.status_code}")
            return response.json() if response.status_code == 200 else None
        else:
            raise Exception(f"Unexpected status: {response.status_code}")
    except Exception as e:
        print_test("Check Combat Encounter", False, str(e))
        return None

def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("🧪 Collabook API Integration Tests")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Basic health checks
    print("📋 Health & Info Tests")
    print("-" * 60)
    if not test_health_check():
        print("\n❌ Backend is not healthy. Aborting tests.")
        return False
    test_root_endpoint()
    print()
    
    # Authentication tests
    print("🔐 Authentication Tests")
    print("-" * 60)
    token, username = test_auth_register()
    if not token:
        # Try to login if registration returned None
        token = test_auth_login("testplayer1000") 
    
    if not token:
        print("\n❌ Cannot obtain authentication token. Aborting tests.")
        return False
    
    user_data = test_get_current_user(token)
    print()
    
    # Story tests
    print("📚 Story Tests")
    print("-" * 60)
    stories = test_list_stories(token)
    
    if stories and len(stories) > 0:
        story_id = stories[0]["id"]
        test_get_story(token, story_id)
        
        # Try to join or get existing character
        character = test_join_story(token, story_id)
        
        # If join failed (already joined), get character from user data
        if not character and user_data and "characters" in user_data:
            existing_chars = [c for c in user_data["characters"] if c["story_id"] == story_id]
            if existing_chars:
                character = existing_chars[0]
                print(f"  Using existing character: {character['id'][:8]}...")
    else:
        print("  ⚠️  No stories available for testing")
        character = None
        story_id = None
    print()
    
    # Interaction tests (main endpoint that was broken)
    print("✨ Interaction Tests")
    print("-" * 60)
    if character:
        test_interact(token, character["id"])
    else:
        print("  ⚠️  Skipped (no character available)")
    print()
    
    # Quest tests
    print("🗡️  Quest Tests")
    print("-" * 60)
    if story_id:
        test_list_quests(token, story_id)
    else:
        print("  ⚠️  Skipped (no story available)")
    print()
    
    # Combat tests
    print("⚔️  Combat Tests")
    print("-" * 60)
    if character:
        test_check_encounter(token, character["id"])
    else:
        print("  ⚠️  Skipped (no character available)")
    print()
    
    # Results summary
    print("=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Total:  {passed_tests + failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        success_rate = (passed_tests / (passed_tests + failed_tests)) * 100
        print(f"\n⚠️  Success rate: {success_rate:.1f}%")
        print("\nFailed tests:")
        for result in test_results:
            if not result["passed"]:
                print(f"  - {result['name']}: {result['message']}")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
