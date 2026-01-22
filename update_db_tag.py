import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
db_url = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost:5432/collabook")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Remove [DB] tag from Echoes of the Past
    cur.execute("""
        UPDATE stories 
        SET world_description_it = REPLACE(world_description_it, ' [DB]', '')
        WHERE title = 'Echoes of the Past';
    """)
    
    conn.commit()
    print(f"Reverted {cur.rowcount} row(s).")
        
    cur.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
