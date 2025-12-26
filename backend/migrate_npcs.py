from sqlalchemy import create_engine, text
import os
import uuid

# Try localhost first if running on host, fall back to db for container
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://collabook:collabook_pass@localhost:5432/collabook_db")

def migrate():
    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Add image_url column to enemies
            print("Checking/Adding 'image_url' to 'enemies' table...")
            try:
                conn.execute(text("ALTER TABLE enemies ADD COLUMN image_url TEXT"))
                conn.commit()
                print("Added 'image_url' column to 'enemies'.")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("'image_url' column already exists in 'enemies'.")
                else:
                    print(f"Error adding 'image_url' to 'enemies': {e}")

            # Create npcs table
            print("Checking/Creating 'npcs' table...")
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS npcs (
                        id VARCHAR(36) PRIMARY KEY,
                        story_id VARCHAR(36) NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        image_url TEXT,
                        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                print("Successfully created 'npcs' table (or it already existed).")
            except Exception as e:
                print(f"Error creating 'npcs' table: {e}")
            
            print("Migration completed successfully.")

    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
