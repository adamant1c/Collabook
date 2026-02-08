#!/usr/bin/env python3
import sys
from sqlalchemy import text
from sqlalchemy.orm import Session

# 🔧 Backend root (./backend mounted as /app)
sys.path.append("/app")

from app.core.database import engine

def sync_sequences():
    print("🔄 Synchronizing database sequences...")
    
    with Session(engine) as session:
        # Get all tables in the public schema
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE';
        """))
        
        tables = [row[0] for row in result]
        
        for table in tables:
            try:
                # Check if 'id' column exists first to avoid unnecessary errors
                col_check = session.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = 'id'
                """)).fetchone()
                
                if not col_check:
                    continue

                # Reset the sequence for the 'id' column
                # pg_get_serial_sequence returns the name of the sequence for a column
                session.execute(text(f"""
                    SELECT setval(pg_get_serial_sequence('"{table}"', 'id'), 
                           COALESCE(MAX(id), 0) + 1, false) 
                    FROM "{table}";
                """))
                print(f"  ✅ {table}: Sequence updated")
            except Exception:
                # Some tables might have 'id' but no sequence (e.g. manual IDs not serial)
                session.rollback()
                continue
        
        session.commit()
        print("\n🚀 All sequences synchronized successfully!")

if __name__ == "__main__":
    sync_sequences()
