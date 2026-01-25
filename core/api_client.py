import requests
import os
from typing import Optional
from django.utils.translation import gettext as _

# Use environment variable or default to localhost
# In Docker, this should be http://backend:8000
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Translation mapping for backend API error messages
# These messages are returned by the FastAPI backend in English
# and need to be translated based on the user's Django language preference
API_ERROR_MESSAGES = {
    # Auth errors
    "Username already registered": "Username already registered",
    "Email already registered": "Email already registered",
    "Invalid email format": "Invalid email format",
    "Incorrect username or password": "Incorrect username or password",
    "Please verify your email before logging in. Check your inbox for the verification link.": "Please verify your email before logging in. Check your inbox for the verification link.",
    "Invalid or expired reset token": "Invalid or expired reset token",
    "Reset token has expired": "Reset token has expired",
    "Invalid verification token": "Invalid verification token",
    "Verification token has expired": "Verification token has expired",
    "Inactive user": "Inactive user",
    "Admin access required": "Admin access required",
    "Could not validate credentials": "Could not validate credentials",
    # Story/Character errors
    "Story not found": "Story not found",
    "Character not found": "Character not found",
    "Not your character": "Not your character",
    "You already have a character in this story": "You already have a character in this story",
    # Quest errors
    "Quest not found": "Quest not found",
    "Quest already accepted": "Quest already accepted",
    "Quest not accepted": "Quest not accepted",
    "Quest already completed": "Quest already completed",
    # Combat errors
    "No active combat": "No active combat",
    "Invalid action": "Invalid action",
    # Item errors
    "Item not found": "Item not found",
    "Item not found in inventory": "Item not found in inventory",
    "Not authorized": "Not authorized",
    "Hours must be between 1 and 24": "Hours must be between 1 and 24",
    # User errors
    "User not found": "User not found",
}

def translate_api_error(error_message: str) -> str:
    """
    Translate an API error message using Django's translation system.
    If the message is in our known list, translate it; otherwise return as-is.
    """
    # Check if this is a known error message
    if error_message in API_ERROR_MESSAGES:
        return _(error_message)
    return error_message



class CollabookAPI:
    """API client for Collabook backend"""
    
    # ==================== Authentication ====================
    
    @staticmethod
    def register(username: str, email: str, password: str, name: str,
                profession: Optional[str] = None, description: Optional[str] = None,
                avatar_description: Optional[str] = None) -> str:
        """Register a new player account"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/register", json={
                "username": username,
                "email": email,
                "password": password,
                "name": name,
                "profession": profession,
                "description": description,
                "avatar_description": avatar_description
            })
            response.raise_for_status()
            data = response.json()
            return data["message"]
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    detail = error_data.get("detail", "")
                    if detail:
                        raise Exception(translate_api_error(detail))
                except (ValueError, KeyError):
                    # If JSON parsing fails, use status code
                    pass
            raise Exception(f"{e.response.status_code} Client Error: {e.response.reason}")
    
    @staticmethod
    def login(username: str, password: str) -> str:
        """Login and get access token"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login",
                                   data={"username": username, "password": password})
            response.raise_for_status()
            data = response.json()
            return data["access_token"]
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    detail = error_data.get("detail", "")
                    if detail:
                        raise Exception(translate_api_error(detail))
                except (ValueError, KeyError):
                    pass
            raise Exception(f"{e.response.status_code} Client Error: {e.response.reason}")
    
    @staticmethod
    def get_current_user(token: str) -> dict:
        """Get current user information (including character data)"""
        response = requests.get(f"{BACKEND_URL}/users/me",
                              headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def update_character(token: str, character_id: str, data: dict):
        """Update character (profession, description,  etc.)"""
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.patch(f"{BACKEND_URL}/users/character/{character_id}", headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def request_password_reset(email: str) -> dict:
        """Request a password reset token"""
        response = requests.post(f"{BACKEND_URL}/auth/request-reset", json={
            "email": email
        })
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def reset_password(token: str, new_password: str) -> dict:
        """Reset password using token"""
        response = requests.post(f"{BACKEND_URL}/auth/reset-password", json={
            "token": token,
            "new_password": new_password
        })
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def verify_email(token: str) -> dict:
        """Verify email using token"""
        response = requests.get(f"{BACKEND_URL}/auth/verify-email", params={"token": token})
        response.raise_for_status()
        return response.json()

    # ==================== Stories ====================
    
    @staticmethod
    def list_stories(token: str) -> list:
        """List all available stories"""
        response = requests.get(f"{BACKEND_URL}/stories/",
                              headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.json()

    @staticmethod
    def list_public_stories() -> list:
        """List available worlds and characters (No Auth Required)"""
        try:
            response = requests.get(f"{BACKEND_URL}/stories/public")
            response.raise_for_status()
            return response.json()
        except Exception:
            return []
    
    @staticmethod
    def get_story(story_id: str, token: str) -> dict:
        """Get story by ID"""
        response = requests.get(f"{BACKEND_URL}/stories/{story_id}",
                              headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def create_story_admin(title: str, world_description: str, genre: str, token: str) -> dict:
        """Create a new story world (Admin only)"""
        response = requests.post(f"{BACKEND_URL}/stories/", 
                               headers={"Authorization": f"Bearer {token}"},
                               json={
                                   "title": title,
                                   "world_description": world_description,
                                   "genre": genre
                               })
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def join_story(story_id: str, token: str, language: str = "en") -> dict:
        """Join an existing story"""
        response = requests.post(f"{BACKEND_URL}/stories/{story_id}/join",
                               headers={"Authorization": f"Bearer {token}"},
                               json={"language": language})  # Pass language in body
        response.raise_for_status()
        return response.json()
    
    # ==================== Interactions ====================
    
    @staticmethod
    def interact(character_id: str, user_action: str, token: str, language: str = "en") -> dict:
        """Send a user action and get narration"""
        response = requests.post(f"{BACKEND_URL}/interact",
                               headers={"Authorization": f"Bearer {token}"},
                               json={
                                   "character_id": character_id,
                                   "user_action": user_action,
                                   "language": language
                               })
        response.raise_for_status()
        return response.json()
