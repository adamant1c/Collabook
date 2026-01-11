"""
Migration: Move current_state from stories to characters

This migration adds current_state to the characters table and removes it from stories.
"""

import psycopg2
import os
from urllib.parse import urlparse

def migrate():
    # Parse DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return False
    
    url = urlparse(database_url)
    
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        database=url.path[1:]  # Remove leading /
    )
    
    try:
        cur = conn.cursor()
        
        print("Step 1: Adding current_state to characters table...")
        cur.execute("""
            ALTER TABLE characters 
            ADD COLUMN IF NOT EXISTS current_state TEXT;
        """)
        
        print("Step 2: Migrating existing data (if any)...")
        # Check if stories.current_state column still exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='stories' AND column_name='current_state';
        """)
        if cur.fetchone():
            # Column exists, migrate data
            cur.execute("""
                UPDATE characters c
                SET current_state = s.current_state
                FROM stories s
                WHERE c.story_id = s.id 
                AND s.current_state IS NOT NULL
                AND c.current_state IS NULL;
            """)
            print("   - Migrated existing data from stories to characters")
        else:
            print("   - Column already removed, skipping data migration")
        
        print("Step 3: Dropping current_state from stories table...")
        cur.execute("""
            ALTER TABLE stories 
            DROP COLUMN IF EXISTS current_state;
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
