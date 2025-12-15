import os
from sqlalchemy import create_engine, inspect, text

# Get database URL from environment or use default
# Try to fix missing password in env var
env_url = os.getenv("DATABASE_URL", "")
if "collabook:@db" in env_url:
    DATABASE_URL = env_url.replace("collabook:@db", "collabook:collabook_pass@db")
    print(f"Fixed DATABASE_URL: {DATABASE_URL}")
else:
    DATABASE_URL = env_url or "postgresql://collabook:collabook_pass@db:5432/collabook_db"

def verify_columns():
    print(f"Connecting to database: {DATABASE_URL.split('@')[-1]}") # Hide password
    engine = create_engine(DATABASE_URL)
    
    inspector = inspect(engine)
    columns = inspector.get_columns('characters')
    
    print("\nColumns in 'characters' table:")
    found_days = False
    found_date = False
    
    for col in columns:
        print(f"- {col['name']} ({col['type']})")
        if col['name'] == 'days_survived':
            found_days = True
        if col['name'] == 'last_played_date':
            found_date = True
            
    print("-" * 30)
    if found_days:
        print("✅ 'days_survived' FOUND")
    else:
        print("❌ 'days_survived' MISSING")
        
    if found_date:
        print("✅ 'last_played_date' FOUND")
    else:
        print("❌ 'last_played_date' MISSING")

if __name__ == "__main__":
    verify_columns()
