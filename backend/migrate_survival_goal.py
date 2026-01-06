from sqlalchemy import create_engine, text
import os
import time

# Try to get DB URL from env, otherwise default to the one likely used in container
# If running from host, user might need to export DATABASE_URL with localhost
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://collabook:collabook_pass@db:5432/collabook_db")

def migrate():
    print(f"Connecting to database at {DATABASE_URL}...")
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
    except Exception as e:
        print(f"Initial connection failed: {e}")
        print("Retrying with localhost...")
        # Fallback for host execution if 'db' is not resolvable
        try:
            localhost_url = DATABASE_URL.replace("@db:", "@localhost:")
            engine = create_engine(localhost_url)
            conn = engine.connect()
            print(f"Connected using {localhost_url}")
        except Exception as e2:
            print(f"Connection failed: {e2}")
            return

    try:
        with conn:
            # Add survival_goal_days column
            try:
                conn.execute(text("ALTER TABLE stories ADD COLUMN survival_goal_days INTEGER DEFAULT 10"))
                print("Added survival_goal_days column.")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("survival_goal_days column already exists.")
                else:
                    print(f"Error adding survival_goal_days: {e}")
                    raise e
            
            conn.commit()
            print("Migration completed successfully.")

    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
