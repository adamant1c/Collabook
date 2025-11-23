"""
Phase 5: Survival Mechanics

Automatically manages hunger, thirst, and fatigue based on character actions.
Applies stat penalties when survival needs are low.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from app.models.db_models import Character, Item, Inventory, User

def update_survival_stats(character: Character, turns_elapsed: int = 1) -> dict:
    """
    Update survival stats after turns and return penalties
    
    Args:
        character: Character object
        turns_elapsed: Number of turns since last update
        
    Returns:
        dict with penalties and status messages
    """
    # Deplete hunger and thirst, increase fatigue
    character.hunger = max(0, character.hunger - (5 * turns_elapsed))
    character.thirst = max(0, character.thirst - (8 * turns_elapsed))
    character.fatigue = min(100, character.fatigue + (3 * turns_elapsed))
    
    penalties = get_survival_penalties(character)
    
    return {
        "penalties": penalties,
        "warnings": get_survival_warnings(character),
        "critical": is_critical_condition(character)
    }

def get_survival_penalties(character: Character) -> dict:
    """
    Calculate stat modifiers based on survival stats
    
    Returns:
        dict with stat penalties and flags
    """
    penalties = {
        "strength": 0,
        "magic": 0,
        "dexterity": 0,
        "defense": 0,
        "hp_drain": 0,
        "combat_disabled": False
    }
    
    # Hunger penalties
    if character.hunger < 30:
        penalties["strength"] -= 2
        penalties["defense"] -= 1
    if character.hunger < 10:
        penalties["strength"] -= 5
        penalties["defense"] -= 3
        penalties["hp_drain"] += 2  # Lose HP each turn
    
    # Thirst penalties (more severe)
    if character.thirst < 40:
        penalties["dexterity"] -= 3
    if character.thirst < 15:
        penalties["dexterity"] -= 7
        penalties["magic"] -= 3
        penalties["hp_drain"] += 3
    
    # Fatigue penalties
    if character.fatigue > 70:
        penalties["strength"] -= 2
        penalties["dexterity"] -= 2
    if character.fatigue > 90:
        penalties["strength"] -= 5
        penalties["dexterity"] -= 5
        penalties["magic"] -= 3
        penalties["combat_disabled"] = True  # Cannot fight
    
    return penalties

def get_survival_warnings(character: Character) -> list:
    """Get user-friendly warning messages"""
    warnings = []
    
    if character.hunger < 10:
        warnings.append("⚠️ You are starving! Eat food immediately!")
    elif character.hunger < 30:
        warnings.append("🍖 You are hungry")
    
    if character.thirst < 15:
        warnings.append("⚠️ You are severely dehydrated! Drink water now!")
    elif character.thirst < 40:
        warnings.append("💧 You are thirsty")
    
    if character.fatigue > 90:
        warnings.append("⚠️ You are exhausted! You must rest!")
    elif character.fatigue > 70:
        warnings.append("😴 You are tired")
    
    return warnings

def is_critical_condition(character: Character) -> bool:
    """Check if character is in life-threatening condition"""
    return (character.hunger == 0 or 
            character.thirst == 0 or 
            character.fatigue >= 100)

def consume_item(character: Character, item: Item, db: Session) -> dict:
    """
    Use a consumable item
    
    Returns:
        dict with success status and effects
    """
    if not item.is_consumable:
        return {"success": False, "message": "This item cannot be consumed"}
    
    # Apply effects
    character.hunger = min(100, character.hunger + item.hunger_restore)
    character.thirst = min(100, character.thirst + item.thirst_restore)
    character.fatigue = max(0, character.fatigue - item.fatigue_restore)
    character.user.hp = min(character.user.max_hp, character.user.hp + item.hp_restore)
    
    db.commit()
    
    effects = []
    if item.hunger_restore > 0:
        effects.append(f"+{item.hunger_restore} hunger")
    if item.thirst_restore > 0:
        effects.append(f"+{item.thirst_restore} thirst")
    if item.fatigue_restore > 0:
        effects.append(f"-{item.fatigue_restore} fatigue")
    if item.hp_restore > 0:
        effects.append(f"+{item.hp_restore} HP")
    
    return {
        "success": True,
        "message": f"You consumed {item.name}",
        "effects": effects
    }

def rest_action(character: Character, hours: int = 8) -> dict:
    """
    Character rests to reduce fatigue
    
    Args:
        character: Character object
        hours: Hours of rest (default 8 for full sleep)
        
    Returns:
        dict with rest results
    """
    # Reduce fatigue (10 per hour)
    fatigue_reduction = min(hours * 10, character.fatigue)
    character.fatigue = max(0, character.fatigue - fatigue_reduction)
    
    # Resting increases hunger and thirst
    character.hunger = max(0, character.hunger - (hours * 2))
    character.thirst = max(0, character.thirst - (hours * 3))
    
    return {
        "fatigue_reduced": fatigue_reduction,
        "hours_rested": hours,
        "message": f"You rested for {hours} hours. Fatigue reduced by {fatigue_reduction}.",
        "warning": "You feel hungry and thirsty after resting" if (character.hunger < 50 or character.thirst < 50) else None
    }

def apply_starvation_death(character: Character, user: User, db: Session) -> bool:
    """
    Check if character dies from lack of survival needs
    
    Returns:
        True if character died, False otherwise
    """
    # Death from starvation/dehydration
    if character.hunger == 0 or character.thirst == 0:
        character.deaths += 1
        
        if character.can_resurrect:
            # First death from starvation - resurrect
            character.can_resurrect = False
            user.hp = user.max_hp // 2
            user.xp = max(0, user.xp - 100)
            character.hunger = 50
            character.thirst = 50
            character.fatigue = 30
            db.commit()
            
            return {
                "died": True,
                "resurrected": True,
                "message": "You died from starvation/dehydration but were resurrected!",
                "penalty": "Lost 100 XP, HP halved. Survival stats partially restored."
            }
        else:
            # Permanent death
            character.status = "dead"
            db.commit()
            
            return {
                "died": True,
                "permanent_death": True,
                "message": "You have permanently died from lack of food and water..."
            }
    
    return {"died": False}
