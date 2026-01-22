
import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path to import app modules if needed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate():
    url = os.getenv("DATABASE_URL")
    if not url:
        # Fallback to default local docker development url if not set
        print("DATABASE_URL not set, trying default development URLs...")
        # Dictionary of potential URLs to try
        urls = [
            "postgresql://collabook:collabook_pass@localhost:5432/collabook_db", # Host mapping
            "postgresql://collabook:collabook_pass@db:5432/collabook_db",        # Docker internal
            "sqlite:///./collabook.db",                                         # SQLite fallback
            "sqlite:///../collabook.db"
        ]
        
        for try_url in urls:
            try:
                print(f"Trying {try_url}...")
                engine = create_engine(try_url)
                with engine.connect() as conn:
                    # Simple check
                    conn.execute(text("SELECT 1"))
                url = try_url
                print(f"Connected to {url}")
                break
            except Exception as e:
                pass
        
        if not url:
            print("Could not connect to any database.")
            sys.exit(1)
    else:
        engine = create_engine(url)

    print(f"Using database: {url}")
    
    columns = [
        ("title_it", "VARCHAR"),
        ("world_description_it", "TEXT"),
        ("genre_it", "VARCHAR")
    ]
    
    with engine.connect() as conn:
        for col_name, col_type in columns:
            try:
                print(f"Adding column {col_name}...")
                conn.execute(text(f"ALTER TABLE stories ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"✓ Added {col_name}")
            except Exception as e:
                # Check for duplicate column error
                msg = str(e).lower()
                if "duplicate" in msg or "exists" in msg:
                     print(f"Column {col_name} already exists.")
                else:
                    print(f"Error adding {col_name}: {e}")
                    # If sqlite, maybe it failed? SQLite supports ADD COLUMN.

if __name__ == "__main__":
    migrate()
