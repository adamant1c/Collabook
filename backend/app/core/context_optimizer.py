"""
Context Optimization for LLM - Minimize Token Usage

This module creates ultra-compact JSON context for the LLM to reduce token costs
while maintaining narrative quality.

Strategy:
1. Send ONLY essential info (no full text fields)
2. Use abbreviations and compact JSON
3. Summarize history instead of sending all turns
4. Send only active quest objectives
"""

from typing import List, Dict, Any
from app.models.db_models import User, Character, Story, Turn, PlayerQuest, QuestStatus

def create_compact_context(
    user: User,
    character: Character,
    story: Story,
    recent_turns: List[Turn],
    active_quests: List[PlayerQuest],
    max_turns: int = 3
) -> Dict[str, Any]:
    """Create ultra-compact context for LLM
    
    Returns JSON-serializable dict with minimal tokens.
    Typical token count: 150-300 tokens (vs 1000+ with full context)
    """
    
    # Character essentials (20-30 tokens)
    char_context = {
        "name": user.name,
        "class": user.profession or "Adventurer",
        "lvl": user.level,
        "hp": f"{user.hp}/{user.max_hp}",
        "stats": {
            "str": user.strength,
            "mag": user.magic,
            "dex": user.dexterity,
            "def": user.defense
        }
    }
    
    # World essentials (30-50 tokens)
    world_context = {
        "world": story.title,
        "genre": story.genre,
        "scene": story.current_state or "Beginning of adventure"
    }
    
    # Recent history summary (50-100 tokens for 3 turns)
    history_summary = []
    for turn in recent_turns[-max_turns:]:
        history_summary.append({
            "action": turn.user_action[:100],  # Max 100 chars
            "result": turn.narration[:150]      # Max 150 chars
        })
    
    # Active quests (30-80 tokens)
    quest_context = []
    for pq in active_quests:
        if pq.status == QuestStatus.IN_PROGRESS:
            quest = pq.quest
            # Only incomplete objectives
            incomplete = [
                obj for obj in quest.objectives 
                if obj.get('id') not in pq.objectives_completed
            ]
            
            quest_context.append({
                "quest": quest.title,
                "type": "MAIN" if quest.quest_type.value == "main" else "SIDE",
                "objectives": [obj.get('description', '')[:80] for obj in incomplete[:2]],  # Max 2 objectives
                "progress": f"{len(pq.objectives_completed)}/{len(quest.objectives)}"
            })
    
    # Compact final context
    context = {
        "char": char_context,
        "world": world_context,
        "history": history_summary,
        "quests": quest_context if quest_context else None
    }
    
    return context

def create_optimized_prompt(
    compact_context: Dict[str, Any],
    user_action: str
) -> str:
    """Create optimized prompt using compact context
    
    Total tokens: ~200-400 (vs 1000-2000 traditional)
    """
    
    import json
    
    # Ultra-compact JSON representation
    context_json = json.dumps(compact_context, separators=(',', ':'))
    
    # Minimal prompt template
    prompt = f"""You are the Dungeon Master.

Context (JSON):
{context_json}

Player: "{user_action}"

Respond in 2-3 paragraphs. If quest objective done, end with: "✨ Quest progress!"
"""
    
    return prompt

def summarize_long_history(turns: List[Turn], max_length: int = 200) -> str:
    """Summarize long turn history into compact string
    
    Used when history > 10 turns to create ultra-compact summary
    """
    
    if len(turns) <= 3:
        return ""
    
    # Extract key events
    key_events = []
    
    for turn in turns:
        # Check for important keywords
        narration_lower = turn.narration.lower()
        
        if any(word in narration_lower for word in ["discovered", "found", "defeated", "met", "arrived"]):
            # Extract first sentence
            first_sentence = turn.narration.split('.')[0]
            if len(first_sentence) < 100:
                key_events.append(first_sentence)
    
    # Join and truncate
    summary = ". ".join(key_events[:3])
    if len(summary) > max_length:
        summary = summary[:max_length] + "..."
    
    return summary

def estimate_token_count(text: str) -> int:
    """Rough estimate of token count (4 chars ≈ 1 token)"""
    return len(text) // 4

# Example usage comparison:
"""
TRADITIONAL APPROACH (BAD - HIGH COST):
-------------------------------------------
Prompt: "You are the Dungeon Master for Realm of Eternal Magic. 
This is a high-fantasy realm where magic flows through every living thing...
[500 words of world description]

Character: Elara the Wise is a level 5 Mage. She is brave and curious, 
seeking ancient knowledge... [200 words of character description]

Current situation: [Full turn history - 10 turns x 100 words each = 1000 words]

Active Quests:
- The Lost Tome: Find the ancient grimoire...
[Full quest descriptions]
"

Total tokens: ~1500-2000 tokens per request
Cost (Gemini): ~$0.0015 per turn
Cost (GPT-4): ~$0.03 per turn


OPTIMIZED APPROACH (GOOD - LOW COST):
-------------------------------------------
Prompt: "You are the Dungeon Master.

Context (JSON):
{"char":{"name":"Elara","class":"Mage","lvl":5,"hp":"45/50","stats":{"str":8,"mag":15,"dex":10,"def":7}},"world":{"world":"Eternal Magic","genre":"Fantasy","scene":"Ancient library ruins"},"history":[{"action":"I search the bookshelf","result":"You find a hidden compartment..."}],"quests":[{"quest":"Lost Tome","type":"MAIN","objectives":["Find grimoire location"],"progress":"1/3"}]}

Player: "I examine the compartment closely"

Respond in 2-3 paragraphs."

Total tokens: ~200-400 tokens per request
Cost (Gemini): ~$0.0002 per turn (87% reduction!)
Cost (GPT-4): ~$0.008 per turn (73% reduction!)


SAVINGS:
- Gemini: $0.0013 saved per turn → $1.30 saved per 1000 turns!
- GPT-4: $0.022 saved per turn → $22 saved per 1000 turns!
"""
