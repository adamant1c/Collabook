import random
from typing import Dict, Tuple, Optional

class GameRules:
    """
    Backend-Authoritative Rules Engine
    Based on simplified D&D 5e mechanics.
    """
    
    # Experience Table (Level 1-20)
    XP_TABLE = {
        1: 0,
        2: 300,
        3: 900,
        4: 2700,
        5: 6500,
        6: 14000,
        # ... extending as needed
    }

    @staticmethod
    def get_level_from_xp(xp: int) -> int:
        """Calculate level based on total XP"""
        level = 1
        for lvl, required_xp in GameRules.XP_TABLE.items():
            if xp >= required_xp:
                level = lvl
            else:
                break
        return level

    @staticmethod
    def roll_d20() -> int:
        return random.randint(1, 20)

    @staticmethod
    def roll_damage(dice_count: int, dice_sides: int, modifier: int = 0) -> int:
        total = sum(random.randint(1, dice_sides) for _ in range(dice_count))
        return total + modifier

    @staticmethod
    def calculate_hit(attacker_attack_bonus: int, defender_ac: int) -> Dict:
        """
        Calculate if an attack hits.
        Returns detailed result for narration.
        """
        roll = GameRules.roll_d20()
        total = roll + attacker_attack_bonus
        
        is_crit = (roll == 20)
        is_fail = (roll == 1)
        
        # Hit logic
        if is_crit:
            is_hit = True
        elif is_fail:
            is_hit = False
        else:
            is_hit = (total >= defender_ac)
            
        return {
            "roll": roll,
            "bonus": attacker_attack_bonus,
            "total": total,
            "is_hit": is_hit,
            "is_crit": is_crit,
            "is_fail": is_fail
        }

    @staticmethod
    def resolve_combat_round(player_stats: Dict, enemy_stats: Dict, action_type: str = "attack") -> Dict:
        """
        Resolve one round of combat (Player Action + Enemy Reaction).
        Currently supports simple melee exchange.
        """
        results = {
            "player_action": action_type,
            "player_hit": None,
            "player_dmg": 0,
            "enemy_hit": None,
            "enemy_dmg": 0,
            "log": []
        }
        
        # 1. Player Turn
        if action_type == "attack":
            hit_result = GameRules.calculate_hit(player_stats['attack_bonus'], enemy_stats['ac'])
            results['player_hit'] = hit_result
            
            if hit_result['is_hit']:
                # Basic damage calculation (e.g. 1d8 + STR mod)
                # Assuming simple fixed dmg dice for now or passing it in stats
                dmg = GameRules.roll_damage(1, 8, player_stats.get('dmg_bonus', 0))
                if hit_result['is_crit']:
                    dmg += GameRules.roll_damage(1, 8, 0) # Crit adds extra die
                
                results['player_dmg'] = dmg
                results['log'].append(f"Player rolled {hit_result['roll']} (+{hit_result['bonus']}) vs AC {enemy_stats['ac']}. HIT! Dealt {dmg} damage.")
            else:
                results['log'].append(f"Player rolled {hit_result['roll']} (+{hit_result['bonus']}) vs AC {enemy_stats['ac']}. MISS.")

        # 2. Enemy Turn (if still alive logic should be handled by caller, but we calculate potential output)
        # Enemy attacks back
        enemy_hit = GameRules.calculate_hit(enemy_stats['attack_bonus'], player_stats['ac'])
        results['enemy_hit'] = enemy_hit
        
        if enemy_hit['is_hit']:
             dmg = GameRules.roll_damage(1, 6, enemy_stats.get('dmg_bonus', 0)) # Assuming 1d6 for generic enemy
             if enemy_hit['is_crit']:
                 dmg += GameRules.roll_damage(1, 6, 0)
             
             results['enemy_dmg'] = dmg
             results['log'].append(f"Enemy attacked! Rolled {enemy_hit['roll']}. HIT! Dealt {dmg} damage.")
        else:
             results['log'].append(f"Enemy attacked! Rolled {enemy_hit['roll']}. MISS.")
             
        return results

class EnemyTemplates:
    """Predefined stats for standard enemies"""
    
    TEMPLATES = {
        "calabrone": {
            "name": "Calabrone Gigante",
            "hp": 20,
            "ac": 12,
            "attack_bonus": 4,
            "xp_reward": 50,
            "level": 1
        },
        "goblin": {
            "name": "Goblin",
            "hp": 15,
            "ac": 11,
            "attack_bonus": 3,
            "xp_reward": 25,
            "level": 1
        },
        "orco": {
            "name": "Orco",
            "hp": 40,
            "ac": 14,
            "attack_bonus": 6,
            "xp_reward": 100,
            "level": 3
        },
        "drago": {
            "name": "Drago Giovane",
            "hp": 150,
            "ac": 17,
            "attack_bonus": 9,
            "xp_reward": 1000,
            "level": 8
        }
    }
    
    @staticmethod
    def get_template(name_query: str) -> Optional[Dict]:
        """Fuzzy match enemy name to template"""
        name_query = name_query.lower()
        for key, template in EnemyTemplates.TEMPLATES.items():
            if key in name_query:
                return template.copy()
        # Fallback generic enemy
        return {
            "name": "Unknown Enemy",
            "hp": 10,
            "ac": 10,
            "attack_bonus": 1,
            "xp_reward": 10,
            "level": 1
        }
