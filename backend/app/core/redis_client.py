import redis
import os
import json

class RedisClient:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.client = redis.from_url(redis_url, decode_responses=True)
    
    def get_story_context(self, story_id: str) -> dict:
        """Get cached story context"""
        data = self.client.get(f"story:{story_id}:context")
        return json.loads(data) if data else None
    
    def set_story_context(self, story_id: str, context: dict, ttl: int = 3600):
        """Cache story context for 1 hour by default"""
        self.client.setex(
            f"story:{story_id}:context",
            ttl,
            json.dumps(context)
        )
    
    def get_user_session(self, user_id: str) -> dict:
        """Get user session data"""
        data = self.client.get(f"user:{user_id}:session")
        return json.loads(data) if data else None
    
    def set_user_session(self, user_id: str, session_data: dict, ttl: int = 7200):
        """Cache user session for 2 hours by default"""
        self.client.setex(
            f"user:{user_id}:session",
            ttl,
            json.dumps(session_data)
        )
    
    def get_active_characters(self, story_id: str) -> list:
        """Get list of active character IDs in a story"""
        data = self.client.get(f"story:{story_id}:active_chars")
        return json.loads(data) if data else []
    
    def add_active_character(self, story_id: str, character_id: str):
        """Add a character to active list"""
        chars = self.get_active_characters(story_id)
        if character_id not in chars:
            chars.append(character_id)
            self.client.set(f"story:{story_id}:active_chars", json.dumps(chars))

redis_client = RedisClient()
