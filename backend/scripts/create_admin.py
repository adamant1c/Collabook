"""
Create admin superuser for FastAPI backend
"""
import sys
from pathlib import Path

# Add parent directory to path to allow importing app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.db_models import User, UserRole
from app.core.security import hash_password

def create_superuser(username: str, email: str, password: str):
    """Create an admin user"""
    db: Session = SessionLocal()
    
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"⚠️  User '{username}' already exists, skipping creation")
            return
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            name="Administrator",
            profession="System Admin",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Admin user '{username}' created successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Role: {admin_user.role}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    # Default credentials for development
    create_superuser(
        username="adm1n",
        email="adm1n@example.com",
        password="adm1n1"
    )
