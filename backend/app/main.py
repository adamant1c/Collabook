from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from app.core.database import engine, Base, SessionLocal
from app.core.security_utils import validate_secret_key, get_cors_origins
from app.core.content_filter import validate_content_filter_config
from app.api import users, stories, interactions, auth, quests, combat, items

# Validate SECRET_KEY on startup (QA recommendation)
validate_secret_key()

# Validate content filter (Phase 6)
validate_content_filter_config()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Collabook API", 
    version="2.1.0",
    description="Collaborative RPG Platform with optimized LLM integration"
)

# Rate limiter setup (QA recommendation: prevent brute force)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),  # Locked down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)  # Auth first!
app.include_router(users.router)
app.include_router(stories.router)
app.include_router(interactions.router)
app.include_router(quests.router)  # Phase 3: Quests
app.include_router(combat.router)  # Phase 4: Combat
app.include_router(items.router)

@app.get("/")
async def root():
    return {
        "message": "Collabook API",
        "version": "2.1.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint (QA recommendation)
    """
    health_status = {
        "status": "healthy",
        "version": "2.1.0",
        "checks": {}
    }

    # Check database - FIX: usa text()
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # ← AGGIUNGI text() qui !!!
        db.close()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"

    # Check Redis (opzionale, non rompe il tutto)
    try:
        from app.core.redis_client import redis_client
        redis_client.redis.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception:
        health_status["checks"]["redis"] = "not configured or unavailable"

    # Return 503 if degraded
    if health_status["status"] == "degraded":
        return JSONResponse(status_code=503, content=health_status)

    return health_status
