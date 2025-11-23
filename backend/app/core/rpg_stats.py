import random
from app.models.db_models import User

def initialize_character_stats(user: User) -> None:
    """Initialize character stats with random values (1-10)
    
    Stats:
    - HP (Health Points): 1-10 initial, max 200
    - STR (Strength): 1-10, max 200
    - MP (Magic Points): 1-10, max 200
    - DEX (Dexterity): 1-10, max 200
    - DEF (Defense): 1-10, max 200
    
    All stats start random to make each character unique!
    """
    
    # Random initial stats (1-10)
    user.hp = random.randint(1, 10)
    user.max_hp = 200  # Maximum HP possible
    user.strength = random.randint(1, 10)
    user.magic = random.randint(1, 10)
    user.dexterity = random.randint(1, 10)
    user.defense = random.randint(1, 10)
    
    # Starting values
    user.xp = 0
    user.level = 1

def calculate_level_from_xp(xp: int) -> int:
    """Calculate level based on XP
    
    Level progression (inspired by D&D):
    Level 1: 0 XP
    Level 2: 100 XP
    Level 3: 300 XP
    Level 4: 600 XP
    Level 5: 1000 XP
    Level 6: 1500 XP
    Level 7: 2100 XP
    Level 8: 2800 XP
    Level 9: 3600 XP
    Level 10: 4500 XP
    Level 11+: +1000 XP per level
    """
    if xp < 100:
        return 1
    elif xp < 300:
        return 2
    elif xp < 600:
        return 3
    elif xp < 1000:
        return 4
    elif xp < 1500:
        return 5
    elif xp < 2100:
        return 6
    elif xp < 2800:
        return 7
    elif xp < 3600:
        return 8
    elif xp < 4500:
        return 9
    else:
        # Level 10+: +1000 XP per level
        return 10 + (xp - 4500) // 1000

def xp_needed_for_next_level(current_level: int) -> int:
    """Calculate XP needed to reach next level"""
    level_thresholds = {
        1: 100,
        2: 300,
        3: 600,
        4: 1000,
        5: 1500,
        6: 2100,
        7: 2800,
        8: 3600,
        9: 4500,
    }
    
    if current_level in level_thresholds:
        return level_thresholds[current_level]
    else:
        # Level 10+
        return 4500 + (current_level - 9) * 1000

def award_xp(user: User, xp_amount: int) -> dict:
    """Award XP to user and handle level up
    
    Returns:
        dict with level_up info if leveled up, else empty dict
    """
    old_level = user.level
    user.xp += xp_amount
    new_level = calculate_level_from_xp(user.xp)
    
    level_up_info = {}
    
    if new_level > old_level:
        # LEVEL UP!
        user.level = new_level
        levels_gained = new_level - old_level
        
        # Stat increases per level (2-5 points random per stat)
        for _ in range(levels_gained):
            user.hp = min(user.hp + random.randint(2, 5), user.max_hp)
            user.strength = min(user.strength + random.randint(2, 5), 200)
            user.magic = min(user.magic + random.randint(2, 5), 200)
            user.dexterity = min(user.dexterity + random.randint(2, 5), 200)
            user.defense = min(user.defense + random.randint(2, 5), 200)
            
            # Increase max HP on level up
            user.max_hp = min(user.max_hp + random.randint(5, 10), 200)
            # Heal to full on level up
            user.hp = user.max_hp
        
        level_up_info = {
            "leveled_up": True,
            "new_level": new_level,
            "levels_gained": levels_gained,
            "message": f"🎉 LEVEL UP! You are now level {new_level}!"
        }
    
    return level_up_info
