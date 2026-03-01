#!/usr/bin/env python3
import sys
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import Table, text

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

def deserialize_value(value, column_type):
    """Convert string values back to proper types"""
    if value is None:
        return None
    
    if "DateTime" in str(column_type) or "TIMESTAMP" in str(column_type):
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except:
                return None
        return value
    
    return value

def import_table(session, model, filename, user_map=None):
    """Import data from JSON file into database table"""
    path = EXPORT_DIR / filename
    
    if not path.exists():
        print(f"⚠️  Skipping {model.__name__ if hasattr(model, '__name__') else model}: {path.name} not found")
        return 0
    
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
    
    if not records:
        print(f"ℹ️  {model.__name__ if hasattr(model, '__name__') else model}: 0 records in {path.name}")
        return 0
    
    from sqlalchemy.inspection import inspect
    try:
        mapper = inspect(model)
        columns = {col.key: col for col in mapper.columns}
        table_name = mapper.local_table.name
        pk_cols = [col.name for col in mapper.primary_key]
    except Exception:
        # Fallback for plain classes used for reflection
        table_name = getattr(model, "__tablename__", None)
        if not table_name:
             print(f"⚠️  Skipping {model}: No __tablename__ defined")
             return 0
        
        metadata = Base.metadata
        try:
            table = Table(table_name, metadata, autoload_with=engine)
            columns = {col.name: col for col in table.columns}
            pk_cols = [col.name for col in table.primary_key]
        except Exception as e:
            print(f"⚠️  Skipping {model}: Table '{table_name}' lookup failed ({e})")
            return 0
    
    imported_count = 0
    skipped_count = 0
    
def import_record(session, model, table_name, record_data, columns, pk_cols, user_map):
    """Processes and imports a single record"""
    imported_count = 0
    skipped_count = 0
    
    try:
        # Special User ID mapping for foreign keys
        if user_map:
            if table_name == "characters" and "user_id" in record_data:
                old_id = record_data["user_id"]
                if old_id in user_map: record_data["user_id"] = user_map[old_id]
            if table_name == "stories" and "created_by" in record_data:
                old_id = record_data["created_by"]
                if old_id in user_map: record_data["created_by"] = user_map[old_id]

        # 1. Handle existing records to avoid UniqueViolation
        if pk_cols:
            filter_kwargs = {col: record_data.get(col) for col in pk_cols if col in record_data}
            if filter_kwargs:
                # Optimized existence check for both declarative and reflected models
                if hasattr(model, "id") and hasattr(session, "query"): # Declarative
                    exists = session.query(model).filter_by(**filter_kwargs).first()
                else: # Reflected / Plain class
                    table = Table(table_name, Base.metadata, autoload_with=engine)
                    from sqlalchemy import select
                    stmt = select(table).filter_by(**filter_kwargs)
                    exists = session.execute(stmt).first()
                
                if exists:
                    skipped_count += 1
                    return 0, 1

        # 2. Process and insert data
        processed_data = {}
        for key, value in record_data.items():
            if key in columns:
                column_type = columns[key].type
                processed_data[key] = deserialize_value(value, column_type)
        
        if hasattr(model, "id"): # Declarative model
            instance = model(**processed_data)
            session.add(instance)
        else: # Table reflection / plain class
            from sqlalchemy import insert
            table = Table(table_name, Base.metadata, autoload_with=engine)
            stmt = insert(table).values(**processed_data)
            session.execute(stmt)
            
        imported_count += 1
    except Exception as e:
        session.rollback()
        print(f"❌ ERROR: Failed to import record in {table_name}: {e}")
        # We don't abort the whole table for one record, but return 0
        return 0, 0

    return imported_count, skipped_count

def import_table(session, model, filename, user_map=None, truncate=False):
    """Import data from JSON file into database table"""
    path = EXPORT_DIR / filename
    
    if not path.exists():
        print(f"⚠️  Skipping {model.__name__ if hasattr(model, '__name__') else model}: {path.name} not found")
        return 0
    
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
    
    if not records:
        print(f"ℹ️  {model.__name__ if hasattr(model, '__name__') else model}: 0 records in {path.name}")
        return 0
    
    from sqlalchemy.inspection import inspect
    try:
        mapper = inspect(model)
        columns = {col.key: col for col in mapper.columns}
        table_name = mapper.local_table.name
        pk_cols = [col.name for col in mapper.primary_key]
    except Exception:
        table_name = getattr(model, "__tablename__", None)
        if not table_name: return 0
        
        try:
            table = Table(table_name, Base.metadata, autoload_with=engine)
            columns = {col.name: col for col in table.columns}
            pk_cols = [col.name for col in table.primary_key]
        except Exception as e:
            print(f"⚠️  Skipping {model}: Table '{table_name}' lookup failed ({e})")
            return 0
    
    if truncate:
        print(f"🧹 Truncating {table_name} before import...")
        session.execute(text(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE'))

    imported_count = 0
    skipped_count = 0
    
    for record_data in records:
        imp, skp = import_record(session, model, table_name, record_data, columns, pk_cols, user_map)
        imported_count += imp
        skipped_count += skp
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"❌ ERROR: Failed to commit table {table_name}: {e}")
        return 0

    msg = f"✅ {table_name}: {imported_count} records imported"
    if skipped_count:
        msg += f" ({skipped_count} already existed)"
    print(msg + f" from {path.name}")
    return imported_count

def migrate_users(session):
    """
    Unified User Migration: Matches and merges Backend users into Django accounts_user.
    """
    print("👤 Migrating Users to unified table...")
    
    auth_users_path = EXPORT_DIR / "auth_users.json"
    backend_users_path = EXPORT_DIR / "users.json"
    
    if not auth_users_path.exists() or not backend_users_path.exists():
        print("❌ ERROR: Missing user export files.")
        return {}

    with open(auth_users_path, "r") as f: auth_records = json.load(f)
    with open(backend_users_path, "r") as f: backend_records = json.load(f)

    # 1. Create existing Django users from auth_users.json
    for rec in auth_records:
        if not session.query(User).filter_by(username=rec["username"]).first():
            u = User(
                username=rec["username"],
                email=rec["email"],
                password=rec["password"],
                first_name=rec.get("first_name", ""),
                last_name=rec.get("last_name", ""),
                is_staff=rec.get("is_staff", False),
                is_superuser=rec.get("is_superuser", False),
                is_active=rec.get("is_active", True),
                date_joined=deserialize_value(rec.get("date_joined"), User.date_joined.type),
                last_login=deserialize_value(rec.get("last_login"), User.last_login.type)
            )
            session.add(u)
    session.commit()

    # 2. Create maps for matching
    all_users = session.query(User).all()
    email_map = {u.email.lower(): u.id for u in all_users if u.email}
    username_map = {u.username.lower(): u.id for u in all_users}
    
    user_map = {} # { old_uuid: new_integer_id }
    
    # 3. Process Backend users
    for b_rec in backend_records:
        email = (b_rec.get("email") or "").lower()
        username = (b_rec.get("username") or "").lower()
        old_id = b_rec["id"]
        
        new_id = email_map.get(email) or username_map.get(username)
        
        if not new_id:
            # Create a placeholder Auth user for this backend user to preserve data
            print(f"  🆕 Creating missing Auth user for backend: {username or email}")
            u = User(
                username=b_rec.get("username") or f"user_{str(old_id)[:8]}",
                email=b_rec.get("email", ""),
                password="!", # Unusable password
                first_name="",
                last_name="",
                role=b_rec.get("role", "PLAYER"),
                is_active=True,
                date_joined=datetime.utcnow()
            )
            session.add(u)
            session.flush()
            new_id = u.id
            # Update maps to avoid duplicates if same user appears twice? (shouldn't happen)
            if u.email: email_map[u.email.lower()] = new_id
            username_map[u.username.lower()] = new_id

        user_map[old_id] = new_id
        
        # Update RPG stats
        u = session.get(User, new_id)
        if u:
            u.role = b_rec.get("role", "PLAYER")
            u.name = b_rec.get("name")
            u.profession = b_rec.get("profession")
            u.description = b_rec.get("description")
            u.avatar_description = b_rec.get("avatar_description")
            u.hp = b_rec.get("hp", 100)
            u.max_hp = b_rec.get("max_hp", 100)
            u.strength = b_rec.get("strength", 0)
            u.magic = b_rec.get("magic", 0)
            u.dexterity = b_rec.get("dexterity", 0)
            u.defense = b_rec.get("defense", 0)
            u.xp = b_rec.get("xp", 0)
            u.level = b_rec.get("level", 1)
            print(f"  ✅ Linked and updated: {u.username}")

    session.commit()
    return user_map

def main():
    print("📥 Importing unified database from JSON exports...")
    
    try:
        wait_for_db()
    except Exception as e:
        print(f"❌ Aborting import: {e}")
        sys.exit(1)

    # Ensure all Backend tables exist (stories, characters, etc.)
    Base.metadata.create_all(bind=engine)
    print(f"📂 Reading from: {EXPORT_DIR}")
    print()
    
    if not EXPORT_DIR.exists():
        print(f"❌ ERROR: Export directory not found: {EXPORT_DIR}")
        sys.exit(1)
    
    try:
        with Session(engine) as session:
            # 1. Migrate Users and get the UUID -> INT mapping
            user_map = migrate_users(session)
            total = len(user_map)
            
            # Reflect other Django tables
            try:
                class Site: __tablename__ = "django_site"
                class SocialApp: __tablename__ = "socialaccount_socialapp"
                class SocialAccount: __tablename__ = "socialaccount_socialaccount"
                class SocialToken: __tablename__ = "socialaccount_socialtoken"
                class EmailAddress: __tablename__ = "account_emailaddress"
                class Category: __tablename__ = "blog_category"
                class Post:     __tablename__ = "blog_post"
                
                total += import_table(session, Site, "django_sites.json", truncate=True)
                total += import_table(session, EmailAddress, "email_addresses.json")
                total += import_table(session, SocialApp, "social_apps.json")
                total += import_table(session, SocialAccount, "social_accounts.json")
                total += import_table(session, SocialToken, "social_tokens.json")
                total += import_table(session, Category, "blog_categories.json")
                total += import_table(session, Post, "blog_posts.json")
            except Exception as e:
                print(f"⚠️  Could not import some Django/blog tables: {e}")

            # 2. Import Game data with mapping
            total += import_table(session, Story, "stories.json", user_map)
            total += import_table(session, Character, "characters.json", user_map)
            total += import_table(session, Turn, "turns.json")
            total += import_table(session, Quest, "quests.json")
            total += import_table(session, PlayerQuest, "player_quests.json")
            total += import_table(session, Enemy, "enemies.json")
            total += import_table(session, NPC, "npcs.json")
            total += import_table(session, Item, "items.json")
            total += import_table(session, Inventory, "inventory.json")
            total += import_table(session, Map, "maps.json")
            total += import_table(session, MapNode, "map_nodes.json")
            total += import_table(session, MapEdge, "map_edges.json")
            
            print()
            print(f"🎉 Unified Import completed successfully! Total records processed: {total}")
            
    except Exception as e:
        print(f"\n❌ ERROR during import: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
