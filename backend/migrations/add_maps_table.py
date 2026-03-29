import os
import sys

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

def run_migration():
    print("Running Map Entity migration...")
    with engine.begin() as conn:
        print("Creating 'maps' table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS maps (
                id VARCHAR(36) PRIMARY KEY,
                story_id VARCHAR(36) NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
                name VARCHAR(200) NOT NULL,
                name_it VARCHAR(200),
                description TEXT,
                description_it TEXT,
                image_url VARCHAR(500),
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
            );
        """))
        
        print("Adding 'map_id' column to 'map_nodes'...")
        try:
            conn.execute(text("ALTER TABLE map_nodes ADD COLUMN map_id VARCHAR(36) REFERENCES maps(id) ON DELETE CASCADE;"))
            print("Successfully added map_nodes.map_id")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("Column map_nodes.map_id already exists.")
            else:
                print(f"Error adding map_nodes.map_id: {e}")
                
        print("Adding 'map_id' column to 'map_edges'...")
        try:
            conn.execute(text("ALTER TABLE map_edges ADD COLUMN map_id VARCHAR(36) REFERENCES maps(id) ON DELETE CASCADE;"))
            print("Successfully added map_edges.map_id")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("Column map_edges.map_id already exists.")
            else:
                print(f"Error adding map_edges.map_id: {e}")

if __name__ == "__main__":
    try:
        run_migration()
        print("✓ Migration complete!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
