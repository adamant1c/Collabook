from sqlalchemy import create_engine, text
import os

# Use db host since we are running inside the container
DATABASE_URL = "postgresql://collabook:collabook_pass@db:5432/collabook_db"

def migrate():
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Add days_survived column
            try:
                conn.execute(text("ALTER TABLE characters ADD COLUMN days_survived INTEGER DEFAULT 0"))
                print("Added days_survived column.")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("days_survived column already exists.")
                else:
                    print(f"Error adding days_survived: {e}")

            # Add last_played_date column
            try:
                conn.execute(text("ALTER TABLE characters ADD COLUMN last_played_date TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL"))
                print("Added last_played_date column.")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("last_played_date column already exists.")
                else:
                    print(f"Error adding last_played_date: {e}")
            
            conn.commit()
            print("Migration completed successfully.")

    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
