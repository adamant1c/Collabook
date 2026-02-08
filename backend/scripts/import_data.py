#!/usr/bin/env python3
import sys
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import Table

# 🔧 Backend root (./backend mounted as /app)
sys.path.append("/app")

from app.core.database import engine, Base
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
    table_name = mapper.local_table.name
    
    imported_count = 0
    skipped_count = 0
    
    # Get primary key column name(s)
    pk_cols = [col.name for col in mapper.primary_key]
    
    for record_data in records:
        # Check if record already exists based on primary key(s)
        if pk_cols:
            filter_kwargs = {col: record_data.get(col) for col in pk_cols if col in record_data}
            if filter_kwargs:
                exists = session.query(model).filter_by(**filter_kwargs).first()
                if exists:
                    skipped_count += 1
                    continue
        
        # Convert values to proper types
        processed_data = {}
        for key, value in record_data.items():
            if key in columns:
                column_type = columns[key].type
                processed_data[key] = deserialize_value(value, column_type)
        
        # Special case for blog_post: ensure author exists
        if table_name == "blog_post" and "author_id" in processed_data:
            author_id = processed_data["author_id"]
            # Check if this author exists in auth_user
            from sqlalchemy import text
            author_exists = session.execute(text("SELECT 1 FROM auth_user WHERE id = :id"), {"id": author_id}).first()
            if not author_exists:
                # Fallback to id 1 if it exists, otherwise skip
                first_user = session.execute(text("SELECT id FROM auth_user LIMIT 1")).first()
                if first_user:
                    print(f"⚠️  Post '{processed_data.get('title')}' refers to non-existent author {author_id}. Mapping to {first_user[0]}")
                    processed_data["author_id"] = first_user[0]
                else:
                    print(f"❌ Skipping post '{processed_data.get('title')}': No users found in auth_user table.")
                    continue

        # Create instance and add to session
        instance = model(**processed_data)
        session.add(instance)
        imported_count += 1
    
    session.commit()
    msg = f"✅ {model.__name__}: {imported_count} records imported"
    if skipped_count:
        msg += f" ({skipped_count} already existed)"
    print(msg + f" from {path.name}")
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
            # Reflect Django and blog tables from database
            try:
                class AuthUser(Base):
                    __table__ = Table("auth_user", Base.metadata, autoload_with=engine)
                class Site(Base):
                    __table__ = Table("django_site", Base.metadata, autoload_with=engine)
                class SocialApp(Base):
                    __table__ = Table("socialaccount_socialapp", Base.metadata, autoload_with=engine)
                class SocialAccount(Base):
                    __table__ = Table("socialaccount_socialaccount", Base.metadata, autoload_with=engine)
                class SocialToken(Base):
                    __table__ = Table("socialaccount_socialtoken", Base.metadata, autoload_with=engine)
                class EmailAddress(Base):
                    __table__ = Table("account_emailaddress", Base.metadata, autoload_with=engine)
                class Category(Base):
                    __table__ = Table("blog_category", Base.metadata, autoload_with=engine)
                class Post(Base):
                    __table__ = Table("blog_post", Base.metadata, autoload_with=engine)
                has_django_tables = True
            except Exception as e:
                print(f"⚠️  Could not reflect Django/blog tables: {e}")
                has_django_tables = False
            
            # Import in order respecting foreign key constraints
            total = 0
            
            # Users first (no dependencies)
            total += import_table(session, User, "users.json")
            
            if has_django_tables:
                # Site and Auth data first
                total += import_table(session, Site, "django_sites.json")
                total += import_table(session, AuthUser, "auth_users.json")
                total += import_table(session, EmailAddress, "email_addresses.json")
                
                # Social Auth data
                total += import_table(session, SocialApp, "social_apps.json")
                total += import_table(session, SocialAccount, "social_accounts.json")
                total += import_table(session, SocialToken, "social_tokens.json")
                
                # Blog data
                total += import_table(session, Category, "blog_categories.json")
                total += import_table(session, Post, "blog_posts.json")
            
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
