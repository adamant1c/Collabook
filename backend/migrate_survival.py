import sqlite3
import os

# Path to the database file
DB_PATH = "../test.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database file {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Add days_survived column
        try:
            cursor.execute("ALTER TABLE characters ADD COLUMN days_survived INTEGER DEFAULT 0")
            print("Added days_survived column.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("days_survived column already exists.")
            else:
                raise e

        # Add last_played_date column
        try:
            cursor.execute("ALTER TABLE characters ADD COLUMN last_played_date DATETIME DEFAULT NULL")
            print("Added last_played_date column.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("last_played_date column already exists.")
            else:
                raise e

        conn.commit()
        print("Migration completed successfully.")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
