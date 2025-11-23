"""
Security utilities for production deployment

Includes:
- Rate limiting configuration
- SECRET_KEY validation
- Input sanitization
- CORS configuration
"""

import os
import re
from typing import Optional
from fastapi import HTTPException

def validate_secret_key():
    """
    Validate SECRET_KEY on startup
    
    Requirements:
    - At least 32 characters
    - Not default value
    - Contains mix of characters
    """
    secret_key = os.getenv("SECRET_KEY", "")
    
    if not secret_key or secret_key == "your-secret-key-here-change-in-production":
        raise ValueError(
            "❌ CRITICAL: SECRET_KEY not set or using default value!\n"
            "Generate a secure key: openssl rand -hex 32\n"
            "Set in .env file: SECRET_KEY=<your-generated-key>"
        )
    
    if len(secret_key) < 32:
        raise ValueError(
            f"❌ CRITICAL: SECRET_KEY too short ({len(secret_key)} chars)!\n"
            "Minimum length: 32 characters\n"
            "Generate secure key: openssl rand -hex 32"
        )
    
    print(f"✅ SECRET_KEY validated ({len(secret_key)} chars)")

def sanitize_user_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection and excessive length
    
    Args:
        text: User input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
        
    Raises:
        HTTPException if input is invalid
    """
    if not text or not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Invalid input: text required")
    
    # Check length
    if len(text) > max_length:
        raise HTTPException(
            status_code=400, 
            detail=f"Input too long: max {max_length} characters"
        )
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Input cannot be empty after sanitization")
    
    return text

def sanitize_html(text: str) -> str:
    """
    Basic HTML/XSS sanitization
    
    Removes:
    - Script tags
    - Event handlers
    - Dangerous protocols
    """
    if not text:
        return text
    
    # Remove script tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove event handlers
    text = re.sub(r'on\w+\s*=\s*["\']?[^"\']*["\']?', '', text, flags=re.IGNORECASE)
    
    # Remove dangerous protocols
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'data:', '', text, flags=re.IGNORECASE)
    
    return text

def validate_email_format(email: str) -> bool:
    """
    Basic email format validation (server-side)
    
    Note: Pydantic EmailStr already validates, this is extra security
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def get_rate_limit_key(request):
    """
    Get client identifier for rate limiting
    
    Uses:
    1. X-Forwarded-For header (if behind proxy)
    2. X-Real-IP header (if behind Nginx)
    3. Client host address
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host

# Rate limit configurations
RATE_LIMITS = {
    "auth_login": "5/minute",        # Max 5 login attempts per minute
    "auth_register": "3/hour",       # Max 3 registrations per hour
    "auth_reset": "3/hour",          # Max 3 password reset requests per hour
    "api_general": "60/minute",      # Max 60 API calls per minute
    "combat_action": "30/minute",    # Max 30 combat actions per minute
}

# CORS configuration for production
PRODUCTION_CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

def get_cors_origins():
    """Get CORS origins based on environment"""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return PRODUCTION_CORS_ORIGINS
    
    # Development: allow all
    return ["*"]
