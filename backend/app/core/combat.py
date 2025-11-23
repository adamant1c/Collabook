"""
Combat System - D&D-inspired mechanics with dice rolls

Features:
- Dice rolling (1d20, 1d8, etc.)
- Initiative system (DEX-based)
- Attack/Magic/Defend/Flee actions
- Enemy AI
- Loot and XP rewards
"""

import random
from typing import Dict, Any, Tuple, Optional
from app.models.db_models import User, Enemy

# ==================== DICE ROLLING ====================

def roll_dice(num_dice: int = 1, sides: int = 20) -> int:
    """Roll dice (e.g., roll_dice(1, 20) = 1d20, roll_dice(2, 6) = 2d6)"""
    return sum(random.randint(1, sides) for _ in range(num_dice))

def roll_with_advantage() -> int:
    """Roll 2d20, take highest"""
    return max(roll_dice(1, 20), roll_dice(1, 20))

def roll_with_disadvantage() -> int:
    """Roll 2d20, take lowest"""
    return min(roll_dice(1, 20), roll_dice(1, 20))

# ==================== MODIFIERS ====================

def stat_modifier(stat_value: int) -> int:
    """Calculate D&D-style modifier from stat (10 = 0, 12 = +1, 8 = -1)"""
    return (stat_value - 10) // 2

# ==================== INITIATIVE ====================

def calculate_initiative(dexterity: int) -> int:
    """Roll initiative: 1d20 + DEX modifier"""
    return roll_dice(1, 20) + stat_modifier(dexterity)

# ==================== ATTACK CALCULATIONS ====================

def player_attack(player: User, enemy: Enemy) -> Tuple[bool, int, str]:
    """
    Calculate player physical attack
    
    Returns: (hit: bool, damage: int, description: str)
    """
    # Attack roll: 1d20 + STR modifier
    str_mod = stat_modifier(player.strength)
    attack_roll = roll_dice(1, 20)
    total_roll = attack_roll + str_mod
    
    # Enemy AC (Armor Class) = 10 + half defense
    enemy_ac = 10 + (enemy.defense // 2)
    
    # Critical hit on natural 20
    if attack_roll == 20:
        damage = roll_dice(2, 8) + max(str_mod, 0)  # Double dice
        return True, damage, f"CRITICAL HIT! (rolled 20) - {damage} damage!"
    
    # Critical miss on natural 1
    if attack_roll == 1:
        return False, 0, f"CRITICAL MISS! (rolled 1)"
    
    # Normal hit check
    if total_roll >= enemy_ac:
        damage = roll_dice(1, 8) + max(str_mod, 0)
        return True, damage, f"Hit! (rolled {attack_roll}+{str_mod}={total_roll} vs AC {enemy_ac}) - {damage} damage"
    
    return False, 0, f"Miss! (rolled {attack_roll}+{str_mod}={total_roll} vs AC {enemy_ac})"

def player_magic_attack(player: User, enemy: Enemy) -> Tuple[bool, int, str, int]:
    """
    Calculate player magic attack
    
    Returns: (success: bool, damage: int, description: str, mp_cost: int)
    """
    mp_cost = 5
    
    if player.magic < mp_cost:
        return False, 0, "Not enough mana!", 0
    
    # Magic attack: 2d6 + MAGIC modifier (always hits, costs MP)
    magic_mod = stat_modifier(player.magic)
    damage = roll_dice(2, 6) + max(magic_mod, 0)
    
    return True, damage, f"Spell hits! - {damage} magical damage", mp_cost

def enemy_attack(enemy: Enemy, player: User, player_defending: bool = False) -> Tuple[bool, int, str]:
    """
    Calculate enemy attack
    
    Returns: (hit: bool, damage: int, description: str)
    """
    # Enemy attack roll: 1d20 + attack bonus
    attack_bonus = enemy.attack // 10
    attack_roll = roll_dice(1, 20)
    total_roll = attack_roll + attack_bonus
    
    # Player AC
    player_ac = 10 + (player.defense // 2)
    if player_defending:
        player_ac += 2  # +2 AC when defending
    
    if total_roll >= player_ac:
        base_damage = roll_dice(1, 6) + (enemy.attack // 10)
        
        # Reduce damage if defending
        if player_defending:
            base_damage = max(base_damage // 2, 1)
            return True, base_damage, f"{enemy.name} attacks but you block most of it! - {base_damage} damage"
        
        return True, base_damage, f"{enemy.name} hits! - {base_damage} damage"
    
    return False, 0, f"{enemy.name} misses!"

# ==================== COMBAT SIMULATION ====================

def attempt_flee(player: User) -> Tuple[bool, str]:
    """
    Attempt to flee combat
    
    Returns: (success: bool, description: str)
    """
    # Base 50% + DEX bonus
    dex_mod = stat_modifier(player.dexterity)
    flee_chance = 0.5 + (dex_mod * 0.05)
    flee_chance = min(max(flee_chance, 0.1), 0.9)  # Clamp 10-90%
    
    if random.random() < flee_chance:
        return True, f"You successfully escape! (DEX check passed)"
    
    return False, f"Failed to escape! (DEX check failed)"

def simulate_combat_round(
    player: User,
    enemy: Enemy,
    player_action: str  # "attack", "magic", "defend"
) -> Dict[str, Any]:
    """
    Simulate ONE round of combat
    
    Returns complete combat result with logs
    """
    result = {
        "player_action": player_action,
        "player_damage_taken": 0,
        "enemy_damage_taken": 0,
        "player_hp_before": player.hp,
        "enemy_hp_before": enemy.hp,
        "player_hp_after": player.hp,
        "enemy_hp_after": enemy.hp,
        "mp_used": 0,
        "combat_log": [],
        "player_victory": False,
        "player_defeat": False,
        "combat_continues": True
    }
    
    # Initiative
    player_init = calculate_initiative(player.dexterity)
    enemy_init = calculate_initiative(enemy.defense)
    
    player_first = player_init >= enemy_init
    
    result["combat_log"].append(f"⚔️ Round Start - Your HP: {player.hp}/{player.max_hp}, Enemy HP: {enemy.hp}")
    
    # Determine action order
    if player_first:
        result["combat_log"].append(f"You act first! (Initiative: {player_init} vs {enemy_init})")
        
        # Player action
        if player_action == "attack":
            hit, damage, desc = player_attack(player, enemy)
            result["combat_log"].append(desc)
            if hit:
                enemy.hp -= damage
                result["enemy_damage_taken"] = damage
        
        elif player_action == "magic":
            success, damage, desc, mp_cost = player_magic_attack(player, enemy)
            result["combat_log"].append(desc)
            if success:
                player.magic -= mp_cost
                result["mp_used"] = mp_cost
                enemy.hp -= damage
                result["enemy_damage_taken"] = damage
        
        elif player_action == "defend":
            result["combat_log"].append("🛡️ You brace for defense! (+2 AC this round)")
        
        # Check enemy defeat
        if enemy.hp <= 0:
            result["player_victory"] = True
            result["combat_continues"] = False
            result["combat_log"].append(f"\n🎉 Victory! You defeated {enemy.name}!")
            result["enemy_hp_after"] = 0
            result["player_hp_after"] = player.hp
            return result
        
        # Enemy counterattack
        hit, damage, desc = enemy_attack(enemy, player, player_action == "defend")
        result["combat_log"].append(desc)
        if hit:
            player.hp -= damage
            result["player_damage_taken"] = damage
    
    else:
        result["combat_log"].append(f"Enemy acts first! (Initiative: {enemy_init} vs {player_init})")
        
        # Enemy attacks first
        hit, damage, desc = enemy_attack(enemy, player, player_action == "defend")
        result["combat_log"].append(desc)
        if hit:
            player.hp -= damage
            result["player_damage_taken"] = damage
        
        # Check player defeat
        if player.hp <= 0:
            result["player_defeat"] = True
            result["combat_continues"] = False
            result["combat_log"].append("\n💀 You have been defeated!")
            result["player_hp_after"] = 0
            result["enemy_hp_after"] = enemy.hp
            return result
        
        # Player counterattack
        if player_action == "attack":
            hit, damage, desc = player_attack(player, enemy)
            result["combat_log"].append(desc)
            if hit:
                enemy.hp -= damage
                result["enemy_damage_taken"] = damage
        
        elif player_action == "magic":
            success, damage, desc, mp_cost = player_magic_attack(player, enemy)
            result["combat_log"].append(desc)
            if success:
                player.magic -= mp_cost
                result["mp_used"] = mp_cost
                enemy.hp -= damage
                result["enemy_damage_taken"] = damage
        
        elif player_action == "defend":
            result["combat_log"].append("🛡️ You prepare to defend")
        
        # Check enemy defeat after player's turn
        if enemy.hp <= 0:
            result["player_victory"] = True
            result["combat_continues"] = False
            result["combat_log"].append(f"\n🎉 Victory! You defeated {enemy.name}!")
    
    # Final HP check
    if player.hp <= 0:
        result["player_defeat"] = True
        result["combat_continues"] = False
        result["combat_log"].append("\n💀 You have been defeated!")
    
    result["player_hp_after"] = max(player.hp, 0)
    result["enemy_hp_after"] = max(enemy.hp, 0)
    
    return result

# ==================== LOOT CALCULATION ====================

def calculate_loot(enemy: Enemy) -> Dict[str, int]:
    """Calculate loot drop from defeated enemy"""
    gold = random.randint(enemy.gold_min, enemy.gold_max)
    
    return {
        "xp": enemy.xp_reward,
        "gold": gold
    }

# ==================== ENCOUNTER GENERATION ====================

def should_trigger_encounter(turn_number: int, player_level: int) -> bool:
    """
    Determine if random encounter should occur
    
    Opzione B: Random system with probability 15-30% per turn
    """
    # Base 20% chance
    base_chance = 0.20
    
    # Increase chance based on turn number (combat every 5-7 turns on average)
    turn_bonus = min((turn_number % 10) * 0.02, 0.10)
    
    encounter_chance = min(base_chance + turn_bonus, 0.30)
    
    return random.random() < encounter_chance
