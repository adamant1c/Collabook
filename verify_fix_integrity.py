import os
import django
import uuid

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collabook_frontend.settings')
django.setup()

from django.contrib.auth import get_user_model
from game.models import Character, Turn, Story

def verify_fix():
    print("Starting verification of character deletion fix...")
    
    User = get_user_model()
    try:
        user = User.objects.get(id=1)
        story = Story.objects.get(id='766c04b8-b181-4d82-86ab-c43601ea98aa')
    except (User.DoesNotExist, Story.DoesNotExist) as e:
        print(f"Error: Required test data (User 1 or Story) not found: {e}")
        return

    # Create a test character
    char_id = str(uuid.uuid4())
    character = Character.objects.create(
        id=char_id,
        user=user,
        story=story,
        status='active'
    )
    print(f"Created test character: {char_id}")

    # Create a test turn
    turn_id = str(uuid.uuid4())
    turn = Turn.objects.create(
        id=turn_id,
        story=story,
        character=character,
        user_action="Test action",
        narration="Test narration",
        turn_number=1
    )
    print(f"Created test turn: {turn_id}")

    # Try to delete the character
    print("Attempting to delete character...")
    try:
        character.delete()
        print("Character deleted successfully!")
    except Exception as e:
        print(f"FAILED to delete character: {e}")
        return

    # Verify turn is also gone
    turn_exists = Turn.objects.filter(id=turn_id).exists()
    if not turn_exists:
        print("SUCCESS: Associated turn was also deleted automatically (CASCADE).")
    else:
        print("FAILURE: Associated turn still exists!")

if __name__ == "__main__":
    verify_fix()
