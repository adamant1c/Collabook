from app.core.database import SessionLocal
from app.models.db_models import Character, User, Story

db = SessionLocal()
story_id = "e094b6e5-1f0a-4ddf-888d-19e74eae4dd4"

print(f"Checking characters for story: {story_id}")
characters = db.query(Character).filter(Character.story_id == story_id).all()

for char in characters:
    user = db.query(User).filter(User.id == char.user_id).first()
    print(f"Found character: {char.id} for user: {user.username} ({user.id})")

if not characters:
    print("No characters found for this story.")
