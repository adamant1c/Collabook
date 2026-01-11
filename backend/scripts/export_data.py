#!/usr/bin/env python3
import sys
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect

# 🔧 Backend root (./backend mounted as /app)
sys.path.append("/app")

from app.core.database import engine
from app.models.db_models import (
    User,
    Story,
    Character,
    Quest,
    PlayerQuest,
    Enemy,
    NPC,
    Item,
    Inventory,
    Turn,
)

EXPORT_DIR = Path("/app/data/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "value"):  # Enum
        return value.value
    return value


def serialize_model(instance):
    data = {}
    mapper = inspect(instance.__class__)
    for column in mapper.columns:
        value = getattr(instance, column.key)
        data[column.key] = serialize_value(value)
    return data


def export_table(session, model, filename):
    records = session.query(model).all()
    output = [serialize_model(r) for r in records]

    path = EXPORT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ {model.__name__}: {len(output)} records → {path.name}")


def main():
    print("📤 Exporting database...")
    with Session(engine) as session:
        export_table(session, User, "users.json")
        export_table(session, Story, "stories.json")
        export_table(session, Character, "characters.json")
        export_table(session, Quest, "quests.json")
        export_table(session, PlayerQuest, "player_quests.json")
        export_table(session, Enemy, "enemies.json")
        export_table(session, NPC, "npcs.json")
        export_table(session, Item, "items.json")
        export_table(session, Inventory, "inventory.json")
        export_table(session, Turn, "turns.json")

    print("🎉 Export completed successfully")


if __name__ == "__main__":
    main()

