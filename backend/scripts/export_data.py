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

from app.core.database import engine, Base, wait_for_db
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
    Map,
    MapNode,
    MapEdge
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
    table_name = getattr(model, "__tablename__", None)
    if not table_name:
        print(f"⚠️  Skipping {model}: No __tablename__ defined")
        return

    metadata = MetaData()
    try:
        table = Table(table_name, metadata, autoload_with=engine)
    except Exception as e:
        print(f"⚠️  Skipping {model}: Table '{table_name}' lookup failed ({e})")
        return

    # Select all columns from the reflected table
    stmt = select(table)
    try:
        result = session.execute(stmt)
    except Exception as e:
        print(f"❌ ERROR: Failed to execute select on {table_name}: {e}")
        return
    
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

    print(f"✅ {table_name}: {len(output)} records → {path.name}")


def main():
    print("📤 Exporting database...")
    
    try:
        wait_for_db()
    except Exception as e:
        print(f"❌ Aborting export: {e}")
        sys.exit(1)

    # Define plain classes for reflection of Django tables (avoid Mapper exceptions)
    class AuthUser: __tablename__ = "auth_user"
    class Site: __tablename__ = "django_site"
    class SocialApp: __tablename__ = "socialaccount_socialapp"
    class SocialAccount: __tablename__ = "socialaccount_socialaccount"
    class SocialToken: __tablename__ = "socialaccount_socialtoken"
    class EmailAddress: __tablename__ = "account_emailaddress"
    class Category: __tablename__ = "blog_category"
    class Post:     __tablename__ = "blog_post"

    with Session(engine) as session:
        # Core Game Tables
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
        export_table(session, Map, "maps.json")
        export_table(session, MapNode, "map_nodes.json")
        export_table(session, MapEdge, "map_edges.json")
        
        # Django / Auth / Blog Tables
        export_table(session, AuthUser, "auth_users.json")
        export_table(session, Site, "django_sites.json")
        export_table(session, SocialApp, "social_apps.json")
        export_table(session, SocialAccount, "social_accounts.json")
        export_table(session, SocialToken, "social_tokens.json")
        export_table(session, EmailAddress, "email_addresses.json")
        export_table(session, Category, "blog_categories.json")
        export_table(session, Post, "blog_posts.json")

    print("🎉 Export completed successfully")


if __name__ == "__main__":
    main()

