"""
Combat Service – Consolidated inline combat resolution.

Handles combat that occurs within the story narration flow
(as opposed to the standalone /combat/ random-encounter endpoints).
"""

from sqlalchemy.orm import Session
from app.core.game_rules import GameRules, EnemyTemplates
from app.models.db_models import Character, User, Enemy, Story


def resolve_inline_combat(
    character: Character,
    current_user: User,
    user_action: str,
    db: Session,
) -> dict:
    """
    Resolve one round of inline combat (story-flow combat).

    Returns:
        dict with keys:
            - directive_prompt: str  (system directive for the LLM)
            - combat_active: bool
            - combat_data: dict | None  (raw round results)
    """
    if not character.combat_state:
        return {"directive_prompt": "", "combat_active": False, "combat_data": None}

    enemy_id = character.combat_state.get("enemy_id")
    current_enemy = db.query(Enemy).filter(Enemy.id == enemy_id).first()

    if not current_enemy:
        # Enemy record missing – clear stale state
        character.combat_state = None
        return {"directive_prompt": "", "combat_active": False, "combat_data": None}

    # ---------- Prepare stats for GameRules ----------
    p_stats = {
        "ac": (current_user.defense or 5) + 10,
        "attack_bonus": (current_user.strength or 5) // 2,
        "dmg_bonus": (current_user.strength or 5) // 3,
    }
    e_stats = {
        "ac": current_enemy.ac,
        "hp": character.combat_state.get("enemy_hp"),
        "attack_bonus": current_enemy.attack_bonus,
        "dmg_bonus": 2,
    }

    # ---------- Determine action type ----------
    action_lower = user_action.lower()
    if "fuga" in action_lower or "flee" in action_lower:
        combat_action = "flee"
    elif any(kw in action_lower for kw in ("pozione", "potion", "cura")):
        combat_action = "heal"
    else:
        combat_action = "attack"

    # ---------- Resolve round ----------
    combat_data = GameRules.resolve_combat_round(p_stats, e_stats, combat_action)

    # Apply damage to enemy
    if combat_data["player_dmg"] > 0:
        character.combat_state["enemy_hp"] = max(
            0, character.combat_state["enemy_hp"] - combat_data["player_dmg"]
        )

    # Apply damage to player
    if combat_data["enemy_dmg"] > 0:
        current_user.hp = max(0, current_user.hp - combat_data["enemy_dmg"])

    # ---------- Determine outcome ----------
    directive_prompt = ""
    combat_active = True

    if character.combat_state["enemy_hp"] <= 0:
        # --- Victory ---
        reward_msg = (
            f"Enemy defeated! +{current_enemy.xp_reward} XP, "
            f"+{current_enemy.gold_min} Gold."
        )
        current_user.xp += current_enemy.xp_reward
        character.gold += current_enemy.gold_min
        character.combat_state = None
        combat_active = False
        directive_prompt = (
            f"SYSTEM DIRECTIVE: Enemy defeated. Details: {reward_msg}. "
            "Narrate the victory and loot."
        )

        # Level-up check
        new_level = GameRules.get_level_from_xp(current_user.xp)
        if new_level > current_user.level:
            current_user.level = new_level
            current_user.max_hp += 10
            current_user.hp = current_user.max_hp  # Full heal
            directive_prompt += f" LEVEL UP TO {new_level}!"

    elif current_user.hp <= 0:
        # --- Player death ---
        character.status = "dead"
        character.combat_state = None
        combat_active = False
        directive_prompt = (
            "SYSTEM DIRECTIVE: Player died in combat. Narrate the tragic end."
        )

    else:
        # --- Combat ongoing ---
        round_log = "; ".join(combat_data["log"])
        directive_prompt = (
            f"SYSTEM DIRECTIVE: Combat ongoing. Result: {round_log}. "
            f"Status: Player {current_user.hp}/{current_user.max_hp} HP, "
            f"Enemy {character.combat_state['enemy_hp']}/{current_enemy.max_hp}. "
            "Narrate this round."
        )

    db.flush()

    return {
        "directive_prompt": directive_prompt,
        "combat_active": combat_active,
        "combat_data": combat_data,
    }


def start_combat_from_event(
    character: Character,
    story: Story,
    enemy_name: str,
    turn_number: int,
    db: Session,
) -> bool:
    """
    Create a new enemy and initialise combat_state on the character.

    Called when the LLM returns event == "start_combat".

    Returns:
        True (combat is now active).
    """
    template = EnemyTemplates.get_template(enemy_name)
    new_enemy = Enemy(
        story_id=story.id,
        name=template["name"],
        hp=template["hp"],
        max_hp=template["hp"],
        ac=template["ac"],
        attack_bonus=template["attack_bonus"],
        xp_reward=template["xp_reward"],
        level=template["level"],
        image_url=template.get("image_url"),
        damage_dice="1d6",
        attack=0,
        defense=0,
    )
    db.add(new_enemy)
    db.flush()

    character.combat_state = {
        "enemy_id": new_enemy.id,
        "enemy_hp": new_enemy.hp,
        "start_turn": turn_number,
    }
    return True
