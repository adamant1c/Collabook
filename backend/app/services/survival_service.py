"""
Survival Service – Day counter, survival stats, and death checks.

Extracts the survival-related logic that was previously inlined in the
interactions endpoint.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.survival import update_survival_stats, apply_starvation_death
from app.models.db_models import Character, Story, User, Turn
from app.models.schemas import InteractionResponse


@dataclass
class SurvivalResult:
    """Outcome of survival processing for a single turn."""

    quest_hint: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    critical: bool = False
    hp_drain: int = 0
    early_return: Optional[InteractionResponse] = None


def process_survival_turn(
    character: Character,
    current_user: User,
    story: Story,
    db_turn: Turn,
    turn_number: int,
    db: Session,
    existing_quest_hint: Optional[str] = None,
) -> SurvivalResult:
    """
    Run all survival logic for one interaction turn.

    This includes:
    - Updating hunger / thirst / fatigue
    - Day counter and survival-mode win condition
    - HP drain from low survival stats
    - Starvation / dehydration death

    Returns a SurvivalResult.  If ``early_return`` is set, the caller
    should return it directly as the endpoint response.
    """
    result = SurvivalResult(quest_hint=existing_quest_hint)

    # --- Update survival stats ---
    survival_data = update_survival_stats(character, turns_elapsed=1)
    result.warnings = survival_data.get("warnings", [])
    result.critical = survival_data.get("critical", False)
    result.hp_drain = survival_data["penalties"]["hp_drain"]

    # --- Day counter ---
    today = datetime.utcnow().date()
    if character.last_played_date is None or character.last_played_date.date() != today:
        character.days_survived += 1
        character.last_played_date = datetime.utcnow()

        goal = story.survival_goal_days if hasattr(story, "survival_goal_days") else 10

        # Win condition
        if character.days_survived >= goal:
            db.commit()
            db.refresh(db_turn)
            result.early_return = InteractionResponse(
                turn_id=db_turn.id,
                narration=(
                    f"CONGRATULATIONS! You have survived {goal} days! "
                    "You have won the Survival Mode!"
                ),
                turn_number=turn_number,
                quest_hint="SURVIVAL COMPLETED!",
                player_stats=_player_stats(current_user, character),
            )
            return result

        # Day notification
        day_msg = f"Day {character.days_survived}/{goal}"
        if character.days_survived == 1:
            day_msg = f"Day 1/{goal}. Survive!"

        result.quest_hint = (
            f"{result.quest_hint} | {day_msg}" if result.quest_hint else day_msg
        )

    # --- HP drain ---
    if result.hp_drain > 0:
        current_user.hp = max(0, current_user.hp - result.hp_drain)

    # --- Starvation / dehydration death ---
    death_result = apply_starvation_death(character, current_user, db)
    if death_result.get("permanent_death"):
        db.commit()
        db.refresh(db_turn)
        result.early_return = InteractionResponse(
            turn_id=db_turn.id,
            narration=death_result["message"],
            turn_number=turn_number,
            critical_warning=True,
            player_stats=_player_stats(current_user, character),
        )

    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _player_stats(user: User, character: Character) -> dict:
    return {
        "hp": user.hp,
        "max_hp": user.max_hp,
        "xp": user.xp,
        "level": user.level,
        "gold": character.gold,
    }
