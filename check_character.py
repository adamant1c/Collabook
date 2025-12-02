import sqlite3
import os

db_path = "/home/alessandro/Project/Collabook/test.db"

if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

char_id = "85494ea8-871d-421a-90f9-d8c6099f6762"

print(f"Checking for character {char_id}...")
cursor.execute("SELECT id, name, user_id, story_id FROM characters WHERE id = ?", (char_id,))
row = cursor.fetchone()

if row:
    print(f"Found character: {row}")
else:
    print("Character NOT found.")

# List all characters to see if there are any
print("\nListing all characters:")
cursor.execute("SELECT id, name FROM characters")
rows = cursor.fetchall()
for r in rows:
    print(r)

conn.close()
