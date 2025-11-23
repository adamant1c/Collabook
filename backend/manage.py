#!/usr/bin/env python3
"""
Collabook Management CLI
"""
import click
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.db_models import User, UserRole, Story
from app.core.security import hash_password
from datetime import datetime

@click.group()
def cli():
    """Collabook Management CLI"""
    pass

@cli.command()
@click.option('--username', prompt=True, help='Admin username')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--name', prompt=True, help='Display name')
def create_admin(username, password, email, name):
    """Create a new admin user"""
    db = SessionLocal()
    
    try:
        # Check if username exists
        if db.query(User).filter(User.username == username).first():
            click.echo(click.style(f"Error: Username '{username}' already exists", fg='red'))
            return
        
        # Check if email exists
        if db.query(User).filter(User.email == email).first():
            click.echo(click.style(f"Error: Email '{email}' already exists", fg='red'))
            return
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            name=name,
            profession="Administrator",
            description="System administrator",
        )
        
        db.add(admin)
        db.commit()
        
        click.echo(click.style(f"\n✓ Admin user '{username}' created successfully!", fg='green'))
        click.echo(f"  Email: {email}")
        click.echo(f"  Name: {name}")
        click.echo(f"  Role: {admin.role.value}")
        
    except Exception as e:
        db.rollback()
        click.echo(click.style(f"Error creating admin: {str(e)}", fg='red'))
    finally:
        db.close()

@cli.command()
def list_users():
    """List all users"""
    db = SessionLocal()
    
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        if not users:
            click.echo("No users found")
            return
        
        click.echo(f"\nTotal users: {len(users)}\n")
        click.echo(f"{'ID':<12} {'Username':<20} {'Email':<30} {'Role':<10} {'Active':<8} {'Created'}")
        click.echo("-" * 110)
        
        for user in users:
            active = "Yes" if user.is_active else "No"
            created = user.created_at.strftime("%Y-%m-%d")
            role_color = 'yellow' if user.role == UserRole.ADMIN else 'cyan'
            
            click.echo(
                f"{user.id[:8]:<12} "
                f"{user.username:<20} "
                f"{user.email:<30} "
                f"{click.style(user.role.value:<10, fg=role_color)} "
                f"{active:<8} "
                f"{created}"
            )
    
    finally:
        db.close()

@cli.command()
@click.option('--username', prompt=True, help='Username to deactivate')
def deactivate_user(username):
    """Deactivate a user account"""
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            click.echo(click.style(f"Error: User '{username}' not found", fg='red'))
            return
        
        if not user.is_active:
            click.echo(click.style(f"User '{username}' is already inactive", fg='yellow'))
            return
        
        user.is_active = False
        db.commit()
        
        click.echo(click.style(f"✓ User '{username}' deactivated", fg='green'))
    
    except Exception as e:
        db.rollback()
        click.echo(click.style(f"Error: {str(e)}", fg='red'))
    finally:
        db.close()

@cli.command()
def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        click.echo(click.style("✓ Database tables created successfully", fg='green'))
    except Exception as e:
        click.echo(click.style(f"Error initializing database: {str(e)}", fg='red'))

@cli.command()
def seed_worlds():
    """Create the 3 default worlds"""
    db = SessionLocal()
    
    try:
        # Check if defaults already exist
        existing = db.query(Story).filter(Story.is_default == True).count()
        if existing > 0:
            click.echo(click.style(f"Default worlds already exist ({existing} found)", fg='yellow'))
            return
        
        # Historical World
        historical = Story(
            title="Echoes of the Past",
            world_description="A historically-inspired world set in medieval Europe during the height of the Renaissance. "
                            "Great kingdoms rise and fall, knights defend their honor, and scholars unlock ancient secrets. "
                            "Navigate political intrigue, participate in grand tournaments, or explore forgotten ruins.",
            genre="Historical Adventure",
            is_default=True,
            current_state="The kingdom prepares for the annual Tournament of Champions...",
            world_metadata={
                "theme": "historical",
                "time_period": "medieval_renaissance",
                "magic_level": "low",
                "technology_level": "medieval",
                "danger_level": "medium"
            }
        )
        
        # Fantasy World
        fantasy = Story(
            title="Realm of Eternal Magic",
            world_description="A high-fantasy realm where magic flows through every living thing. "
                           "Ancient dragons soar the skies, elven kingdoms hide in enchanted forests, "
                           "and dwarven cities delve deep into mystical mountains. Dark forces stir in forgotten places, "
                           "and heroes are called to face legendary quests.",
            genre="Epic Fantasy",
            is_default=True,
            current_state="The Council of Mages senses a disturbance in the magical ley lines...",
            world_metadata={
                "theme": "fantasy",
                "magic_level": "very_high",
                "races": ["human", "elf", "dwarf", "halfling", "orc"],
                "danger_level": "high",
                "has_dragons": True
            }
        )
        
        # Sci-Fi World
        scifi = Story(
            title="Horizon Beyond Stars",
            world_description="The year is 2347. Humanity has colonized the solar system and made first contact with alien civilizations. "
                           "Advanced AI, cybernetic augmentations, and faster-than-light travel are commonplace. "
                           "Navigate space politics, explore alien worlds, uncover corporate conspiracies, "
                           "or fight in the ongoing conflict between Earth Alliance and the Outer Colonies.",
            genre="Science Fiction",
            is_default=True,
            current_state="Your ship approaches the neutral trading station orbiting Jupiter...",
            world_metadata={
                "theme": "scifi",
                "time_period": "far_future",
                "technology_level": "advanced",
                "has_aliens": True,
                "has_ai": True,
                "danger_level": "high"
            }
        )
        
        db.add(historical)
        db.add(fantasy)
        db.add(scifi)
        db.commit()
        
        click.echo(click.style("\n✓ Default worlds created successfully!", fg='green'))
        click.echo("\n  1. Echoes of the Past (Historical)")
        click.echo("  2. Realm of Eternal Magic (Fantasy)")
        click.echo("  3. Horizon Beyond Stars (Sci-Fi)")
        
    except Exception as e:
        db.rollback()
        click.echo(click.style(f"Error creating worlds: {str(e)}", fg='red'))
    finally:
        db.close()

if __name__ == '__main__':
    cli()
