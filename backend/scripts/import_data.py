#!/usr/bin/env python3
import sys
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

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

def deserialize_value(value, column_type):
    """Convert string values back to proper types"""
    if value is None:
        return None
    
    # Handle datetime fields
    if "DateTime" in str(column_type) or "TIMESTAMP" in str(column_type):
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except:
                return None
        return value
    
    return value

def import_table(session, model, filename):
    """Import data from JSON file into database table"""
    path = EXPORT_DIR / filename
    
    if not path.exists():
        print(f"⚠️  Skipping {model.__name__}: {path.name} not found")
        return 0
    
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
    
    if not records:
        print(f"ℹ️  {model.__name__}: 0 records in {path.name}")
        return 0
    
    # Get column information from the model
    from sqlalchemy.inspection import inspect
    mapper = inspect(model)
    columns = {col.key: col for col in mapper.columns}
    
    imported_count = 0
    for record_data in records:
        # Convert values to proper types
        processed_data = {}
        for key, value in record_data.items():
            if key in columns:
                column_type = columns[key].type
                processed_data[key] = deserialize_value(value, column_type)
        
        # Create instance and add to session
        instance = model(**processed_data)
        session.add(instance)
        imported_count += 1
    
    session.commit()
    print(f"✅ {model.__name__}: {imported_count} records imported from {path.name}")
    return imported_count

def main():
    print("📥 Importing database from JSON exports...")
    print(f"📂 Reading from: {EXPORT_DIR}")
    print()
    
    if not EXPORT_DIR.exists():
        print(f"❌ ERROR: Export directory not found: {EXPORT_DIR}")
        sys.exit(1)
    
    try:
        with Session(engine) as session:
            # Import in order respecting foreign key constraints
            total = 0
            
            # Users first (no dependencies)
            total += import_table(session, User, "users.json")
            
            # Stories depend on Users (and possibly Characters, but we'll handle that)
            total += import_table(session, Story, "stories.json")
            
            # Characters depend on Users AND Stories
            total += import_table(session, Character, "characters.json")
            
            # Turns depend on Stories
            total += import_table(session, Turn, "turns.json")
            
            # Quests (no dependencies on user data)
            total += import_table(session, Quest, "quests.json")
            
            # PlayerQuests depend on Characters and Quests
            total += import_table(session, PlayerQuest, "player_quests.json")
            
            # Game entities (no dependencies on user data)
            total += import_table(session, Enemy, "enemies.json")
            total += import_table(session, NPC, "npcs.json")
            total += import_table(session, Item, "items.json")
            
            # Inventory depends on Characters and Items
            total += import_table(session, Inventory, "inventory.json")
            
            print()
            print(f"🎉 Import completed successfully! Total records: {total}")
            
    except Exception as e:
        print(f"\n❌ ERROR during import: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
