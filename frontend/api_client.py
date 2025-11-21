import streamlit as st
import requests
import os
from typing import Optional

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

class CollabookAPI:
    """API client for Collabook backend"""
    
    @staticmethod
    def create_user(name: str, profession: str, description: str, avatar_description: str) -> dict:
        """Create a new user"""
        response = requests.post(f"{BACKEND_URL}/users/", json={
            "name": name,
            "profession": profession,
            "description": description,
            "avatar_description": avatar_description
        })
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_user(user_id: str) -> dict:
        """Get user by ID"""
        response = requests.get(f"{BACKEND_URL}/users/{user_id}")
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def create_story(title: str, world_description: str, genre: str, metadata: dict = None) -> dict:
        """Create a new story"""
        response = requests.post(f"{BACKEND_URL}/stories/", json={
            "title": title,
            "world_description": world_description,
            "genre": genre,
            "metadata": metadata or {}
        })
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def list_stories() -> list:
        """List all stories"""
        response = requests.get(f"{BACKEND_URL}/stories/")
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_story(story_id: str) -> dict:
        """Get story by ID"""
        response = requests.get(f"{BACKEND_URL}/stories/{story_id}")
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def join_story(story_id: str, user_id: str) -> dict:
        """Join an existing story"""
        response = requests.post(f"{BACKEND_URL}/stories/{story_id}/join?user_id={user_id}", json={
            "story_id": story_id
        })
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def interact(character_id: str, user_action: str) -> dict:
        """Send a user action and get narration"""
        response = requests.post(f"{BACKEND_URL}/interact/", json={
            "character_id": character_id,
            "user_action": user_action
        })
        response.raise_for_status()
        return response.json()
