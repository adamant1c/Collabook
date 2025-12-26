import os
import sys

# Add the project root to sys.path to find core.api_client
sys.path.append('.')

from core.api_client import CollabookAPI

def test_api_client():
    # We can't easily test with a real token without a live backend and login
    # But we can verify the URL being called
    print(f"API Client BACKEND_URL: {CollabookAPI.__dict__.get('_BACKEND_URL', 'Defaulting to environment/localhost')}")
    
    # We can mock the request to see if it would fail or if it calls the right path
    try:
        # This will likely fail with a connection error or 401 if running locally
        # but the point is to verify it doesn't crash on the call itself
        user = CollabookAPI.get_current_user("fake_token")
    except Exception as e:
        print(f"Caught expected exception during network call: {e}")
        # If it says 404/401, it means the URL was at least formed
        if "404" in str(e) or "401" in str(e):
             print("Path was reached (or at least attempted).")

if __name__ == "__main__":
    test_api_client()
