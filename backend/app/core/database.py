import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def wait_for_db(max_retries=5, delay=5):
    """Wait for database to be ready with retries."""
    print(f"Connecting to database at {DATABASE_URL.split('@')[-1]}...")
    for i in range(max_retries):
        try:
            # Try to connect and execute a simple query
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✅ Database connection established.")
                return True
        except OperationalError as e:
            if i < max_retries - 1:
                print(f"⚠️  Database not ready (attempt {i+1}/{max_retries}): {e}")
                print(f"   Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"❌ ERROR: Could not connect to database after {max_retries} attempts.")
                raise e
    return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
