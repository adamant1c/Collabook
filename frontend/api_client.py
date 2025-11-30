import requests
import os
from typing import Optional

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

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
            return data["access_token"]
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    detail = e.response.json().get("detail")
                    if detail:
                        raise Exception(detail)
                except:
                    pass
            raise e
    
    @staticmethod
    def login(username: str, password: str) -> str:
        """Login and get access token"""
        response = requests.post(f"{BACKEND_URL}/auth/login",
                               data={"username": username, "password": password})
        response.raise_for_status()
        data = response.json()
        return data["access_token"]
    
    @staticmethod
    def get_current_user(token: str) -> dict:
        """Get current user information"""
        response = requests.get(f"{BACKEND_URL}/auth/me",
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
    
    # ==================== Stories ====================
    
    @staticmethod
    def list_stories(token: str) -> list:
        """List all available stories"""
        response = requests.get(f"{BACKEND_URL}/stories/",
                              headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.json()
    
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
    def join_story(story_id: str, token: str) -> dict:
        """Join an existing story"""
        response = requests.post(f"{BACKEND_URL}/stories/{story_id}/join",
                               headers={"Authorization": f"Bearer {token}"},
                               json={"story_id": story_id})
        response.raise_for_status()
        return response.json()
    
    # ==================== Interactions ====================
    
    @staticmethod
    def interact(character_id: str, user_action: str, token: str) -> dict:
        """Send a user action and get narration"""
        response = requests.post(f"{BACKEND_URL}/interact/",
                               headers={"Authorization": f"Bearer {token}"},
                               json={
                                   "character_id": character_id,
                                   "user_action": user_action
                               })
        response.raise_for_status()
        return response.json()
