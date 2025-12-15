import os
from sqlalchemy import create_engine, text

# Get database URL from environment or use default
# Try to fix missing password in env var
env_url = os.getenv("DATABASE_URL", "")
if "collabook:@db" in env_url:
    DATABASE_URL = env_url.replace("collabook:@db", "collabook:collabook_pass@db")
    print(f"Fixed DATABASE_URL: {DATABASE_URL}")
else:
    DATABASE_URL = env_url or "postgresql://collabook:collabook_pass@db:5432/collabook_db"

def migrate_db():
    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    # Add days_survived
    with engine.connect() as connection:
        print("Checking/Adding 'days_survived' column...")
        try:
            connection.execute(text("ALTER TABLE characters ADD COLUMN days_survived INTEGER DEFAULT 0"))
            connection.commit()
            print("Added 'days_survived' column.")
        except Exception as e:
            if "already exists" in str(e):
                print("'days_survived' column already exists.")
            else:
                print(f"Error adding 'days_survived': {e}")
                connection.rollback()

    # Add last_played_date
    with engine.connect() as connection:
        print("Checking/Adding 'last_played_date' column...")
        try:
            connection.execute(text("ALTER TABLE characters ADD COLUMN last_played_date TIMESTAMP"))
            connection.commit()
            print("Added 'last_played_date' column.")
        except Exception as e:
            if "already exists" in str(e):
                print("'last_played_date' column already exists.")
            else:
                print(f"Error adding 'last_played_date': {e}")
                connection.rollback()
        
    print("Migration complete.")

if __name__ == "__main__":
    migrate_db()
