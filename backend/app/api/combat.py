from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import random
from datetime import datetime

from app.core.database import get_db
from app.core.combat import (
    should_trigger_encounter, simulate_combat_round, 
    attempt_flee, calculate_loot
)
from app.core.rpg_stats import award_xp
from app.api.auth import get_current_user
from app.models.db_models import User, Enemy, Character, Turn, EnemyType
from app.models.schemas import CombatActionRequest, CombatResult

router = APIRouter(prefix="/combat", tags=["combat"])

# In-memory combat sessions (in production, use Redis)
active_combats = {}

@router.post("/check-encounter")
async def check_encounter(
    character_id: str,
    turn_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if random encounter should trigger (Opzione B)
    Called after each turn
    """
    
    # Verify character ownership
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")
    
    # Check if already in combat
    if character_id in active_combats:
        return {"encounter": False, "message": "Already in combat"}
    
    # Random encounter check (15-30% chance)
    if should_trigger_encounter(turn_number, current_user.level):
        # Select appropriate enemy (level ± 2)
        enemies = db.query(Enemy).filter(
            Enemy.story_id == character.story_id,
            Enemy.level >= current_user.level - 2,
            Enemy.level <= current_user.level + 2
        ).all()
        
        if not enemies:
            return {"encounter": False, "message": "No enemies available"}
        
        # Select random enemy
        enemy_template = random.choice(enemies)
        
        # Create enemy instance (fresh HP)
        enemy_instance = Enemy(
            story_id=enemy_template.story_id,
            name=enemy_template.name,
            description=enemy_template.description,
            enemy_type=enemy_template.enemy_type,
            level=enemy_template.level,
            hp=enemy_template.max_hp,  # Full HP
            max_hp=enemy_template.max_hp,
            attack=enemy_template.attack,
            defense=enemy_template.defense,
            xp_reward=enemy_template.xp_reward,
            gold_min=enemy_template.gold_min,
            gold_max=enemy_template.gold_max
        )
        
        # Store in active combats
        active_combats[character_id] = {
            "enemy": enemy_instance,
            "round": 0
        }
        
        return {
            "encounter": True,
            "enemy": {
                "name": enemy_instance.name,
                "description": enemy_instance.description or f"A {enemy_instance.enemy_type.value} enemy",
                "level": enemy_instance.level,
                "hp": enemy_instance.hp,
                "max_hp": enemy_instance.max_hp,
                "type": enemy_instance.enemy_type.value
            },
            "message": f"⚔️ A wild {enemy_instance.name} appears!"
        }
    
    return {"encounter": False}

@router.post("/action", response_model=CombatResult)
async def combat_action(
    character_id: str,
    action: str,  # "attack", "magic", "defend", "flee"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute combat action"""
    
    # Verify character ownership
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")
    
    # Check active combat
    if character_id not in active_combats:
        raise HTTPException(status_code=400, detail="No active combat")
    
    combat_session = active_combats[character_id]
    enemy = combat_session["enemy"]
    combat_session["round"] += 1
    
    # Handle flee attempt
    if action == "flee":
        success, message = attempt_flee(current_user)
        
        if success:
            # Remove from active combats
            del active_combats[character_id]
            
            return CombatResult(
                success=True,
                fled=True,
                message=message,
                combat_log=[message]
            )
        else:
            # Failed flee, enemy gets free attack
            from app.core.combat import enemy_attack
            hit, damage, desc = enemy_attack(enemy, current_user, False)
            if hit:
                current_user.hp -= damage
                db.commit()
            
            return CombatResult(
                success=False,
                fled=False,
                message=message,
                combat_log=[message, desc],
                player_hp=current_user.hp,
                enemy_hp=enemy.hp
            )
    
    # Validate action
    if action not in ["attack", "magic", "defend"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Simulate combat round
    result = simulate_combat_round(current_user, enemy, action)
    
    # Handle victory
    if result["player_victory"]:
        # Calculate loot
        loot = calculate_loot(enemy)
        
        # Award XP
        level_up_info = award_xp(current_user, loot["xp"])
        
        # Award gold
        character.gold += loot["gold"]
        
        # Save turn
        turn = Turn(
            story_id=character.story_id,
            character_id=character.id,
            user_action=f"Combat: {action}",
            narration="\n".join(result["combat_log"]),
            turn_number=db.query(Turn).filter(Turn.character_id == character.id).count() + 1,
            was_combat=True,
            combat_result=result
        )
        db.add(turn)
        db.commit()
        
        # Remove from active combats
        del active_combats[character_id]
        
        return CombatResult(
            success=True,
            victory=True,
            message=f"Victory! Defeated {enemy.name}",
            combat_log=result["combat_log"],
            xp_gained=loot["xp"],
            gold_gained=loot["gold"],
            level_up=level_up_info.get("leveled_up", False),
            new_level=level_up_info.get("new_level") if level_up_info else None
        )
    
    # Handle defeat
    if result["player_defeat"]:
        # Increment death counter
        character.deaths += 1
        
        # Check resurrection
        if character.can_resurrect:
            # First death: resurrect with penalty
            character.can_resurrect = False
            current_user.hp = current_user.max_hp // 2
            current_user.xp = max(0, current_user.xp - 50)
            
            db.commit()
            
            # Remove from combat
            del active_combats[character_id]
            
            return CombatResult(
                success=False,
                defeat=True,
                resurrected=True,
                message="You were defeated but resurrected!",
                combat_log=result["combat_log"] + ["💫 You wake up with reduced HP and lost XP..."],
                penalty="Lost 50 XP, HP halved to 50%"
            )
        else:
            # Second death: permanent
            character.status = "dead"
            db.commit()
            
            del active_combats[character_id]
            
            return CombatResult(
                success=False,
                defeat=True,
                permanent_death=True,
                message="Permanent death. Your character is lost.",
                combat_log=result["combat_log"] + ["💀 Your vision fades to black..."]
            )
    
    # Combat continues
    db.commit()
    
    return CombatResult(
        success=True,
        combat_continues=True,
        message=f"Round {combat_session['round']}",
        combat_log=result["combat_log"],
        player_hp=result["player_hp_after"],
        player_max_hp=current_user.max_hp,
        enemy_hp=result["enemy_hp_after"],
        enemy_max_hp=enemy.max_hp
    )

@router.get("/status")
async def get_combat_status(
    character_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get current combat status"""
    
    if character_id not in active_combats:
        return {"in_combat": False}
    
    combat = active_combats[character_id]
    enemy = combat["enemy"]
    
    return {
        "in_combat": True,
        "round": combat["round"],
        "enemy": {
            "name": enemy.name,
            "hp": enemy.hp,
            "max_hp": enemy.max_hp,
            "level": enemy.level
        }
    }
