from app.models.db_models import User, Character, Story, Turn, NPC, Enemy
from app.core.context_optimizer import create_compact_context
from datetime import datetime
import json

def verify_context():
    # Mock data
    user = User(name="TestHero", profession="Warrior", level=5, hp=80, max_hp=100)
    story = Story(title="Epic Kingdom", genre="Fantasy", current_state="At the gates")
    
    # Mock NPCs
    npc1 = NPC(name="Old Sage", description="A wise old man with a long beard.")
    npc2 = NPC(name="Innkeeper", description="Friendly host of the Sleeping Dragon.")
    story.npcs = [npc1, npc2]
    
    # Mock Enemies
    enemy1 = Enemy(name="Goblin", level=2)
    enemy2 = Enemy(name="Orc Chief", level=8)
    story.enemies = [enemy1, enemy2]
    
    character = Character(id="char-123")
    recent_turns = [
        Turn(user_action="I walk to the gate", narration="The guards look at you suspiciously.", turn_number=1)
    ]
    
    context = create_compact_context(
        user=user,
        character=character,
        story=story,
        recent_turns=recent_turns,
        active_quests=[]
    )
    
    print("Generated Context Structure:")
    print(json.dumps(context, indent=2))
    
    assert "entities" in context
    assert "npcs" in context["entities"]
    assert "enemies" in context["entities"]
    assert len(context["entities"]["npcs"]) == 2
    assert len(context["entities"]["enemies"]) == 2
    
    print("\n✅ Verification successful! NPCs and Enemies are correctly included in the LLM context.")

if __name__ == "__main__":
    verify_context()
