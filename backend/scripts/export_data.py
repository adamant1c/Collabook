#!/usr/bin/env python3
import sys
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, Table, select
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


def export_table(session, model, filename):
    # Use reflection to get the actual columns in the database
    # This matches the DB schema, not the potentially newer code model
    table_name = model.__tablename__
    metadata = MetaData()
    try:
        table = Table(table_name, metadata, autoload_with=engine)
    except Exception as e:
        print(f"⚠️  Skipping {model.__name__}: Table '{table_name}' lookup failed ({e})")
        return

    # Select all columns from the reflected table
    stmt = select(table)
    result = session.execute(stmt)
    
    output = []
    for row in result:
        # row._mapping converts the row to a dict-like object
        row_dict = {}
        for key, val in row._mapping.items():
            row_dict[key] = serialize_value(val)
        output.append(row_dict)

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

