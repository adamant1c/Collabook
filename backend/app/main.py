from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import users, stories, interactions, auth, quests, combat

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Collabook API", version="2.1.0")  # Phase 4

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
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

@app.get("/")
async def root():
    return {"message": "Welcome to Collabook API", "version": "1.0.0"}
