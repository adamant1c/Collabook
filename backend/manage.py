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
from app.models.db_models import User, UserRole, Story, Quest, QuestType
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
            role_display = click.style(user.role.value, fg=role_color)
            
            click.echo(
                f"{user.id[:8]:<12} "
                f"{user.username:<20} "
                f"{user.email:<30} "
                f"{role_display:<10} "
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
                            "Navigate political intrigue,  participate in grand tournaments, or explore forgotten ruins.",
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
        db.refresh(historical)
        db.refresh(fantasy)
        db.refresh(scifi)
        
        click.echo(click.style("\n✓ Default worlds created successfully!", fg='green'))
        click.echo("\n  1. Echoes of the Past (Historical)")
        click.echo("  2. Realm of Eternal Magic (Fantasy)")
        click.echo("  3. Horizon Beyond Stars (Sci-Fi)")
        
        # Store IDs for quest seeding
        db.close()
        
    except Exception as e:
        db.rollback()
        click.echo(click.style(f"Error creating worlds: {str(e)}", fg='red'))
    finally:
        db.close()

@cli.command()
def seed_quests():
    """Create default quests for the 3 worlds"""
    db = SessionLocal()
    
    try:
        # Get worlds
        historical = db.query(Story).filter(Story.title == "Echoes of the Past").first()
        fantasy = db.query(Story).filter(Story.title == "Realm of Eternal Magic").first()
        scifi = db.query(Story).filter(Story.title == "Horizon Beyond Stars").first()
        
        if not all([historical, fantasy, scifi]):
            click.echo(click.style("Error: Default worlds not found. Run 'seed-worlds' first!", fg='red'))
            return
        
        quests_to_add = []
        
        # HISTORICAL QUESTS
        quests_to_add.append(Quest(
            story_id=historical.id,
            title="The King's Tournament",
            description="Prove your worth in the Grand Tournament",
            quest_type=QuestType.MAIN,
            objectives=[
                {"id": "train", "description": "Train with the Master-at-Arms"},
                {"id": "qualify", "description": "Win 3 practice duels"},
                {"id": "champion", "description": "Defeat the reigning champion"}
            ],
            xp_reward=500,
            gold_reward=1000,
            quest_giver="King Harold III",
            required_level=1
        ))
        
        quests_to_add.append(Quest(
            story_id=historical.id,
            title="Lost Heirloom",
            description="Find the merchant's stolen family ring",
            quest_type=QuestType.SIDE,
            objectives=[
                {"id": "investigate", "description": "Question witnesses in the market"},
                {"id": "hideout", "description": "Find the thieves' hideout"},
                {"id": "recover", "description": "Recover the stolen ring"}
            ],
            xp_reward=100,
            gold_reward=200,
            quest_giver="Merchant Giovanni",
            required_level=1
        ))
        
        # FANTASY QUESTS
        quests_to_add.append(Quest(
            story_id=fantasy.id,
            title="The Arcane Disturbance",
            description="Investigate the disruption in magical ley lines",
            quest_type=QuestType.MAIN,
            objectives=[
                {"id": "investigate", "description": "Speak with the Council of Mages"},
                {"id": "locate", "description": "Find the source of the disturbance"},
                {"id": "restore", "description": "Restore balance to the ley lines"}
            ],
            xp_reward=500,
            gold_reward=800,
            quest_giver="Archmage Elendril",
            required_level=1
        ))
        
        quests_to_add.append(Quest(
            story_id=fantasy.id,
            title="Dragon's Hoard",
            description="Retrieve a magical artifact from an ancient dragon",
            quest_type=QuestType.SIDE,
            objectives=[
                {"id": "locate", "description": "Find the dragon's lair"},
                {"id": "negotiate", "description": "Negotiate or battle for the artifact"}
            ],
            xp_reward=200,
            gold_reward=500,
            quest_giver="Sage Thorin",
            required_level=3
        ))
        
        # SCI-FI QUESTS
        quests_to_add.append(Quest(
            story_id=scifi.id,
            title="The Jupiter Conspiracy",
            description="Uncover a corporate plot at the trading station",
            quest_type=QuestType.MAIN,
            objectives=[
                {"id": "dock", "description": "Dock at the trading station"},
                {"id": "gather_intel", "description": "Gather intelligence on suspicious activity"},
                {"id": "expose", "description": "Expose the conspiracy"}
            ],
            xp_reward=500,
            gold_reward=1500,
            quest_giver="Station Commander Chen",
            required_level=1
        ))
        
        quests_to_add.append(Quest(
            story_id=scifi.id,
            title="Smuggler's Run",
            description="Transport illegal cargo past Alliance patrols",
            quest_type=QuestType.SIDE,
            objectives=[
                {"id": "acquire", "description": "Acquire the contraband"},
                {"id": "evade", "description": "Evade Alliance patrols"},
                {"id": "deliver", "description": "Deliver to the buyer"}
            ],
            xp_reward=150,
            gold_reward=400,
            quest_giver="Smuggler Kane",
            required_level=2
        ))
        
        # Add all quests
        for quest in quests_to_add:
            db.add(quest)
        
        db.commit()
        
        click.echo(click.style("\n✓ Default quests created successfully!", fg='green'))
        click.echo(f"\n  {len(quests_to_add)} quests added:")
        click.echo("  - Echoes of the Past: 2 quests (1 main, 1 side)")
        click.echo("  - Realm of Eternal Magic: 2 quests (1 main, 1 side)")
        click.echo("  - Horizon Beyond Stars: 2 quests (1 main, 1 side)")
        
    except Exception as e:
        db.rollback()
        click.echo(click.style(f"Error creating quests: {str(e)}", fg='red'))
    finally:
        db.close()

@cli.command()
def seed_enemies():
    """Create default enemies for the 3 worlds"""
    db = SessionLocal()
    
    try:
        from app.models.db_models import Enemy, EnemyType
        
        # Get worlds
        historical = db.query(Story).filter(Story.title == "Echoes of the Past").first()
        fantasy = db.query(Story).filter(Story.title == "Realm of Eternal Magic").first()
        scifi = db.query(Story).filter(Story.title == "Horizon Beyond Stars").first()
        
        if not all([historical, fantasy, scifi]):
            click.echo(click.style("Error: Default worlds not found. Run 'seed-worlds' first!", fg='red'))
            return
        
        enemies = []
        
        # HISTORICAL ENEMIES
        enemies.append(Enemy(
            story_id=historical.id,
            name="Bandit",
            description="A desperate outlaw seeking easy prey",
            enemy_type=EnemyType.COMMON,
            level=1, hp=15, max_hp=15, attack=8, defense=5,
            xp_reward=25, gold_min=5, gold_max=15
        ))
        
        enemies.append(Enemy(
            story_id=historical.id,
            name="Guard Captain",
            description="A well-trained soldier in service to the king",
            enemy_type=EnemyType.ELITE,
            level=3, hp=35, max_hp=35, attack=15, defense=12,
            xp_reward=100, gold_min=25, gold_max=50
        ))
        
        enemies.append(Enemy(
            story_id=historical.id,
            name="Tournament Champion",
            description="The reigning champion, undefeated for years",
            enemy_type=EnemyType.BOSS,
            level=5, hp=60, max_hp=60, attack=20, defense=15,
            xp_reward=300, gold_min=100, gold_max=200
        ))
        
        # FANTASY ENEMIES
        enemies.append(Enemy(
            story_id=fantasy.id,
            name="Goblin Scout",
            description="A small, cunning creature from the dark forest",
            enemy_type=EnemyType.COMMON,
            level=1, hp=12, max_hp=12, attack=6, defense=4,
            xp_reward=20, gold_min=3, gold_max=10
        ))
        
        enemies.append(Enemy(
            story_id=fantasy.id,
            name="Dark Mage",
            description="A corrupted wizard wielding forbidden magic",
            enemy_type=EnemyType.ELITE,
            level=4, hp=40, max_hp=40, attack=18, defense=10,
            xp_reward=150, gold_min=30, gold_max=75
        ))
        
        enemies.append(Enemy(
            story_id=fantasy.id,
            name="Ancient Dragon",
            description="A legendary beast of immense power",
            enemy_type=EnemyType.BOSS,
            level=10, hp=100, max_hp=100, attack=30, defense=20,
            xp_reward=1000, gold_min=500, gold_max=1000
        ))
        
        # SCI-FI ENEMIES
        enemies.append(Enemy(
            story_id=scifi.id,
            name="Security Drone",
            description="An automated patrol unit armed with lasers",
            enemy_type=EnemyType.COMMON,
            level=2, hp=20, max_hp=20, attack=10, defense=8,
            xp_reward=30, gold_min=10, gold_max=20
        ))
        
        enemies.append(Enemy(
            story_id=scifi.id,
            name="Alien Mercenary",
            description="A battle-hardened warrior from the outer colonies",
            enemy_type=EnemyType.ELITE,
            level=5, hp=50, max_hp=50, attack=20, defense=15,
            xp_reward=200, gold_min=50, gold_max=150
        ))
        
        enemies.append(Enemy(
            story_id=scifi.id,
            name="AI Warlord",
            description="A rogue AI controlling an army of machines",
            enemy_type=EnemyType.BOSS,
            level=8, hp=80, max_hp=80, attack=25, defense=18,
            xp_reward=600, gold_min=300, gold_max=600
        ))
        
        # Add all enemies
        for enemy in enemies:
            db.add(enemy)
        
        db.commit()
        
        click.echo(click.style("\n✓ Default enemies created successfully!", fg='green'))
        click.echo(f"\n  {len(enemies)} enemies added:")
        click.echo("  - Echoes of the Past: 3 enemies (1 common, 1 elite, 1 boss)")
        click.echo("  - Realm of Eternal Magic: 3 enemies (1 common, 1 elite, 1 boss)")
        click.echo("  - Horizon Beyond Stars: 3 enemies (1 common, 1 elite, 1 boss)")
        
    except Exception as e:
        db.rollback()
        click.echo(click.style(f"Error creating enemies: {str(e)}", fg='red'))
    finally:
        db.close()

@cli.command()
def seed_items():
    """Create default consumable items for survival mechanics"""
    from app.models.db_models import Item, ItemType
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Check if items already exist
        existing = db.query(Item).count()
        if existing > 0:
            click.echo(click.style(f"⚠ Items already exist ({existing} items). Use --force to recreate.", fg='yellow'))
            if not click.confirm("Delete existing items and recreate?"):
                return
            db.query(Item).delete()
        
        items = []
        
        # Food items
        items.append(Item(
            name="Bread",
            item_type=ItemType.FOOD,
            description="Simple bread loaf. Fills you up.",
            hunger_restore=20,
            gold_cost=5
        ))
        
        items.append(Item(
            name="Cooked Meat",
            item_type=ItemType.FOOD,
            description="Freshly cooked meat. Satisfying and nutritious.",
            hunger_restore=40,
            gold_cost=15
        ))
        
        items.append(Item(
            name="Royal Feast",
            item_type=ItemType.FOOD,
            description="Luxurious multi-course meal. Completely satiates hunger.",
            hunger_restore=80,
            gold_cost=50
        ))
        
        # Water items
        items.append(Item(
            name="Water Flask",
            item_type=ItemType.WATER,
            description="Clean drinking water. Essential for survival.",
            thirst_restore=30,
            gold_cost=3
        ))
        
        items.append(Item(
            name="Wine",
            item_type=ItemType.WATER,
            description="Fine wine. Quenches thirst and relaxes you.",
            thirst_restore=25,
            fatigue_restore=5,
            gold_cost=10
        ))
        
        items.append(Item(
            name="Elixir of Vitality",
            item_type=ItemType.WATER,
            description="Magical elixir. Completely refreshes you.",
            thirst_restore=50,
            fatigue_restore=10,
            gold_cost=30
        ))
        
        # Potions
        items.append(Item(
            name="Health Potion",
            item_type=ItemType.POTION,
            description="Restores health immediately.",
            hp_restore=30,
            gold_cost=50
        ))
        
        items.append(Item(
            name="Energy Tonic",
            item_type=ItemType.POTION,
            description="Reduces fatigue and increases alertness.",
            fatigue_restore=50,
            gold_cost=40
        ))
        
        items.append(Item(
            name="Stamina Brew",
            item_type=ItemType.POTION,
            description="Comprehensive restoration. Expensive but effective.",
            hunger_restore=30,
            thirst_restore=30,
            fatigue_restore=30,
            hp_restore=20,
            gold_cost=100
        ))
        
        # Add all items
        for item in items:
            db.add(item)
        
        db.commit()
        
        click.echo(click.style("\n✓ Default items created successfully!", fg='green'))
        click.echo(f"\n  {len(items)} items added:")
        click.echo("  - Food: Bread, Cooked Meat, Royal Feast")
        click.echo("  - Water: Water Flask, Wine, Elixir of Vitality")
        click.echo("  - Potions: Health Potion, Energy Tonic, Stamina Brew")
        click.echo("\n💡 Players can use items to restore hunger, thirst, and fatigue!")
        
    except Exception as e:
        db.rollback()
        click.echo(click.style(f"Error creating items: {str(e)}", fg='red'))
    finally:
        db.close()

if __name__ == '__main__':
    cli()
