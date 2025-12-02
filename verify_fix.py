import requests
import sys
import uuid

BASE_URL = "http://localhost:8000"

def verify_fix():
    print("1. Authenticating...")
    # Unique user for this run
    unique_id = str(uuid.uuid4())[:8]
    username = f"verify_{unique_id}"
    
    # Register
    reg_data = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "password123",
        "name": "Verify User"
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    if resp.status_code != 201:
        print(f"Registration failed: {resp.text}")
        return
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get User ID
    resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    user_id = resp.json()["id"]
    print(f"User ID: {user_id}")
    
    print("\n2. Joining a story...")
    # List stories
    resp = requests.get(f"{BASE_URL}/stories/", headers=headers)
    stories = resp.json()
    if not stories:
        print("No stories found!")
        return
    
    story_id = stories[0]["id"]
    print(f"Joining story: {stories[0]['title']} ({story_id})")
    
    # Join story
    resp = requests.post(f"{BASE_URL}/stories/{story_id}/join", headers=headers, json={})
    if resp.status_code != 200:
        print(f"Join failed: {resp.text}")
        return
    
    character = resp.json()
    character_id = character["id"]
    print(f"Character ID: {character_id}")
    
    if character_id == user_id:
        print("WARNING: Character ID matches User ID (unexpected but possible if UUIDs collide? No.)")
    else:
        print("Confirmed: Character ID is different from User ID.")
        
    print("\n3. Simulating BUG (Using User ID for interact)...")
    data_bug = {
        "character_id": user_id,  # <--- The BUG
        "user_action": "Look around"
    }
    resp = requests.post(f"{BASE_URL}/interact", headers=headers, json=data_bug)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 404:
        print("SUCCESS: Confirmed that using User ID returns 404 (as expected).")
    else:
        print(f"FAILURE: Expected 404, got {resp.status_code}")
        
    print("\n4. Simulating FIX (Using Character ID for interact)...")
    data_fix = {
        "character_id": character_id,  # <--- The FIX
        "user_action": "Look around"
    }
    resp = requests.post(f"{BASE_URL}/interact", headers=headers, json=data_fix)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        print("SUCCESS: Confirmed that using Character ID returns 200.")
        print(f"Narration: {resp.json().get('narration')[:50]}...")
    else:
        print(f"FAILURE: Expected 200, got {resp.status_code}")
        print(f"Response: {resp.text}")

if __name__ == "__main__":
    verify_fix()
