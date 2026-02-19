from typing import Generator
from app.core.llm_client import llm_client, LLMClient
from app.core.redis_client import redis_client, RedisClient

def get_llm_client() -> LLMClient:
    """Dependency provider for the LLM Client singleton"""
    return llm_client

def get_redis_client() -> RedisClient:
    """Dependency provider for the Redis Client singleton"""
    return redis_client
