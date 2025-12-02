import requests
import sys

BASE_URL = "http://localhost:8000"

def reproduce_404():
    # 1. Login/Register to get token
    auth_data = {
        "username": "debug_user_404",
        "password": "password123"
    }
    
    # Try login first
    response = requests.post(f"{BASE_URL}/auth/login", data=auth_data)
    if response.status_code != 200:
        # Register if login fails
        reg_data = {
            "username": "debug_user_404",
            "email": "debug404@test.com",
            "password": "password123",
            "name": "Debug User"
        }
        requests.post(f"{BASE_URL}/auth/register", json=reg_data)
        response = requests.post(f"{BASE_URL}/auth/login", data=auth_data)
    
    token = response.json()["access_token"]
    print(f"Got token: {token[:10]}...")
    
    # 2. Call interact with INVALID character ID
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "character_id": "00000000-0000-0000-0000-000000000000",
        "user_action": "Test action"
    }
    
    print("\nSending request with INVALID character ID...")
    response = requests.post(f"{BASE_URL}/interact", headers=headers, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

if __name__ == "__main__":
    reproduce_404()
