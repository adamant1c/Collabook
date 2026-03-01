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
from app.models.db_models import User, UserRole, Story, Quest, QuestType, Map, MapNode, MapEdge, NPC, Enemy, EnemyType
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
        
        # HISTORICAL ENEMIES (14th C)
        enemies.append(Enemy(
            story_id=historical.id,
            name="English Longbowman",
            description="A skilled archer from across the channel.",
            enemy_type=EnemyType.COMMON,
            level=1, hp=15, max_hp=15, attack=8, defense=5,
            xp_reward=25, gold_min=5, gold_max=15,
            image_url="english_longbowman.png" # Placeholder if not gen'd
        ))
        
        enemies.append(Enemy(
            story_id=historical.id,
            name="French Knight",
            description="A formidable noble in heavy plate armor.",
            enemy_type=EnemyType.ELITE,
            level=3, hp=40, max_hp=40, attack=16, defense=14,
            xp_reward=120, gold_min=30, gold_max=60,
            image_url="french_knight_enemy.png"
        ))
        
        enemies.append(Enemy(
            story_id=historical.id,
            name="Tournament Champion",
            description="The reigning champion of the King's tournament.",
            enemy_type=EnemyType.BOSS,
            level=5, hp=70, max_hp=70, attack=22, defense=18,
            xp_reward=350, gold_min=100, gold_max=250,
            image_url="tournament_champion.png"
        ))
        
        # FANTASY ENEMIES
        enemies.append(Enemy(
            story_id=fantasy.id,
            name="Goblin Scout",
            description="A small, cunning creature from the dark forest.",
            enemy_type=EnemyType.COMMON,
            level=1, hp=12, max_hp=12, attack=6, defense=4,
            xp_reward=20, gold_min=3, gold_max=10,
            image_url="goblin.png"
        ))
        
        enemies.append(Enemy(
            story_id=fantasy.id,
            name="Dark Mage",
            description="A corrupted wizard wielding forbidden magic.",
            enemy_type=EnemyType.ELITE,
            level=4, hp=40, max_hp=40, attack=18, defense=10,
            xp_reward=150, gold_min=30, gold_max=75,
            image_url="dark_mage.png"
        ))
        
        enemies.append(Enemy(
            story_id=fantasy.id,
            name="Ancient Dragon",
            description="A legendary beast of immense power.",
            enemy_type=EnemyType.BOSS,
            level=10, hp=120, max_hp=120, attack=35, defense=25,
            xp_reward=1200, gold_min=500, gold_max=1200,
            image_url="ancient_dragon.png"
        ))
        
        # SCI-FI ENEMIES
        enemies.append(Enemy(
            story_id=scifi.id,
            name="Security Drone",
            description="An automated patrol unit armed with lasers.",
            enemy_type=EnemyType.COMMON,
            level=2, hp=20, max_hp=20, attack=10, defense=8,
            xp_reward=30, gold_min=10, gold_max=20,
            image_url="security_drone.png"
        ))
        
        enemies.append(Enemy(
            story_id=scifi.id,
            name="Alien Mercenary",
            description="A battle-hardened warrior from the outer colonies.",
            enemy_type=EnemyType.ELITE,
            level=5, hp=55, max_hp=55, attack=22, defense=16,
            xp_reward=250, gold_min=60, gold_max=180,
            image_url="alien_mercenary.png"
        ))
        
        enemies.append(Enemy(
            story_id=scifi.id,
            name="AI Warlord",
            description="A rogue AI controlling an army of machines.",
            enemy_type=EnemyType.BOSS,
            level=8, hp=90, max_hp=90, attack=28, defense=20,
            xp_reward=700, gold_min=350, gold_max=700,
            image_url="ai_warlord.png"
        ))
        
        # Add all enemies
        for enemy in enemies:
            db.add(enemy)
        
        db.commit()
        
        click.echo(click.style("\n✓ Default enemies created successfully!", fg='green'))
        click.echo(f"\n  {len(enemies)} enemies added with thematic images:")
        click.echo("  - Echoes of the Past: English Longbowman, French Knight, Tournament Champion")
        click.echo("  - Realm of Eternal Magic: Goblin, Dark Mage, Ancient Dragon")
        click.echo("  - Horizon Beyond Stars: Security Drone, Alien Mercenary, AI Warlord")
        
    except Exception as e:
        db.rollback()
        click.echo(click.style(f"Error creating enemies: {str(e)}", fg='red'))
    finally:
        db.close()

@cli.command()
def seed_npcs():
    """Create thematic NPCs for the 3 worlds"""
    db = SessionLocal()
    
    try:
        # Get worlds
        historical = db.query(Story).filter(Story.title == "Echoes of the Past").first()
        fantasy = db.query(Story).filter(Story.title == "Realm of Eternal Magic").first()
        scifi = db.query(Story).filter(Story.title == "Horizon Beyond Stars").first()
        
        if not all([historical, fantasy, scifi]):
            click.echo(click.style("Error: Default worlds not found. Run 'seed-worlds' first!", fg='red'))
            return
            
        # Clear existing NPCs to prevent duplicates
        db.query(NPC).delete()
        
        npcs = []
        
        # HISTORICAL NPCs (14th C)
        npcs.append(NPC(
            story_id=historical.id,
            name="King Edward III",
            description="Regal King of England, determined to reclaim his French lands.",
            image_url="king_george.png" # Existing regal image
        ))
        
        npcs.append(NPC(
            story_id=historical.id,
            name="Philippe VI",
            description="The Valois King of France, defending his crown with chivalry.",
            image_url="guard_captain.png" 
        ))
        
        # FANTASY NPCs
        npcs.append(NPC(
            story_id=fantasy.id,
            name="Archmage Elendril",
            description="Wise elder of the Arcane Citadel, watcher of the ley lines.",
            image_url="archmage_elendril.jpg"
        ))
        
        npcs.append(NPC(
            story_id=fantasy.id,
            name="Thalia the Woodsman",
            description="A survival expert living deep within the Silken Woods.",
            image_url="gentle_witch.png"
        ))
        
        # SCI-FI NPCs
        npcs.append(NPC(
            story_id=scifi.id,
            name="Commander Chen",
            description="Leader of the Jupiter Orbital Garrison, uncompromising and loyal.",
            image_url="ai_warlord.png" 
        ))
        
        npcs.append(NPC(
            story_id=scifi.id,
            name="Smuggler Kane",
            description="A resourceful pilot who knows every backway in the Outer Rim.",
            image_url="alien_mercenary.png"
        ))
        
        # Add all npcs
        for npc in npcs:
            db.add(npc)
        
        db.commit()
        
        click.echo(click.style("\n✓ Default NPCs created successfully!", fg='green'))
        click.echo(f"\n  {len(npcs)} NPCs added:")
        click.echo("  - Historical: King Edward III, Philippe VI")
        click.echo("  - Fantasy: Archmage Elendril, Thalia")
        click.echo("  - Sci-Fi: Commander Chen, Smuggler Kane")
        
    except Exception as e:
        db.rollback()
        click.echo(click.style(f"Error creating NPCs: {str(e)}", fg='red'))
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

@cli.command()
def seed_maps():
    """Create default map nodes and edges for the 3 worlds"""
    db = SessionLocal()
    
    try:
        # Get worlds
        historical = db.query(Story).filter(Story.title == "Echoes of the Past").first()
        fantasy = db.query(Story).filter(Story.title == "Realm of Eternal Magic").first()
        scifi = db.query(Story).filter(Story.title == "Horizon Beyond Stars").first()
        
        if not all([historical, fantasy, scifi]):
            click.echo(click.style("Error: Default worlds not found. Run 'seed-worlds' first!", fg='red'))
            return
            
        # Clear existing maps for these worlds to avoid duplicates
        db.query(MapEdge).filter(MapEdge.story_id.in_([historical.id, fantasy.id, scifi.id])).delete()
        db.query(MapNode).filter(MapNode.story_id.in_([historical.id, fantasy.id, scifi.id])).delete()
        db.query(Map).filter(Map.story_id.in_([historical.id, fantasy.id, scifi.id])).delete()
        db.commit()

        # --- FANTASY MAP ---
        f_map = Map(story_id=fantasy.id, name="Eternal Magic Map", name_it="Mappa di Eternal Magic", description="The world of Eternal Magic.", description_it="Il mondo di Eternal Magic.", image_url="fantasy_map.jpg")
        db.add(f_map)
        db.flush()

        f_nodes = [
            MapNode(story_id=fantasy.id, map_id=f_map.id, name="Sylvan Forest", name_it="Foresta di Sylvan", node_type="region", x=250, y=250, icon="🌲", is_starting_location=True),
            MapNode(story_id=fantasy.id, map_id=f_map.id, name="Iron Mountains", name_it="Montagne di Ferro", node_type="region", x=750, y=250, icon="⛰️"),
            MapNode(story_id=fantasy.id, map_id=f_map.id, name="Crystal Plains", name_it="Piane di Cristallo", node_type="region", x=750, y=750, icon="💎"),
            MapNode(story_id=fantasy.id, map_id=f_map.id, name="Shadow Wastes", name_it="Lande d'Ombra", node_type="region", x=250, y=750, icon="💀"),
            MapNode(story_id=fantasy.id, map_id=f_map.id, name="Arcane Citadel", name_it="Cittadella Arcana", node_type="region", x=500, y=500, icon="🏰")
        ]
        db.add_all(f_nodes)
        db.flush()
        
        f_n = {n.name: n.id for n in f_nodes}
        f_edges = [
            MapEdge(story_id=fantasy.id, map_id=f_map.id, from_node_id=f_n["Sylvan Forest"], to_node_id=f_n["Iron Mountains"]),
            MapEdge(story_id=fantasy.id, map_id=f_map.id, from_node_id=f_n["Iron Mountains"], to_node_id=f_n["Crystal Plains"]),
            MapEdge(story_id=fantasy.id, map_id=f_map.id, from_node_id=f_n["Crystal Plains"], to_node_id=f_n["Shadow Wastes"]),
            MapEdge(story_id=fantasy.id, map_id=f_map.id, from_node_id=f_n["Shadow Wastes"], to_node_id=f_n["Sylvan Forest"]),
            MapEdge(story_id=fantasy.id, map_id=f_map.id, from_node_id=f_n["Arcane Citadel"], to_node_id=f_n["Sylvan Forest"]),
            MapEdge(story_id=fantasy.id, map_id=f_map.id, from_node_id=f_n["Arcane Citadel"], to_node_id=f_n["Iron Mountains"]),
            MapEdge(story_id=fantasy.id, map_id=f_map.id, from_node_id=f_n["Arcane Citadel"], to_node_id=f_n["Crystal Plains"]),
            MapEdge(story_id=fantasy.id, map_id=f_map.id, from_node_id=f_n["Arcane Citadel"], to_node_id=f_n["Shadow Wastes"])
        ]
        db.add_all(f_edges)

        # --- SCI-FI MAP ---
        s_map = Map(story_id=scifi.id, name="Horizon Galaxy Map", name_it="Mappa Galaxy Horizon", description="The star systems of the Frontier.", description_it="I sistemi stellari della Frontiera.", image_url="scifi_map.jpg")
        db.add(s_map)
        db.flush()

        s_nodes = [
            MapNode(story_id=scifi.id, map_id=s_map.id, name="Earth Alliance", name_it="Alleanza Terrestre", node_type="system", x=500, y=500, icon="🌍", is_starting_location=True),
            MapNode(story_id=scifi.id, map_id=s_map.id, name="Mars Colony", name_it="Colonia Marziana", node_type="planet", x=400, y=400, icon="🔴"),
            MapNode(story_id=scifi.id, map_id=s_map.id, name="Jupiter Station", name_it="Stazione di Giove", node_type="station", x=600, y=600, icon="🛰️"),
            MapNode(story_id=scifi.id, map_id=s_map.id, name="Alpha Centauri", name_it="Alpha Centauri", node_type="system", x=800, y=200, icon="✨"),
            MapNode(story_id=scifi.id, map_id=s_map.id, name="Outer Rim", name_it="Bordo Esterno", node_type="region", x=200, y=800, icon="☄️")
        ]
        db.add_all(s_nodes)
        db.flush()
        
        s_n = {n.name: n.id for n in s_nodes}
        s_edges = [
            MapEdge(story_id=scifi.id, map_id=s_map.id, from_node_id=s_n["Earth Alliance"], to_node_id=s_n["Mars Colony"]),
            MapEdge(story_id=scifi.id, map_id=s_map.id, from_node_id=s_n["Earth Alliance"], to_node_id=s_n["Jupiter Station"]),
            MapEdge(story_id=scifi.id, map_id=s_map.id, from_node_id=s_n["Earth Alliance"], to_node_id=s_n["Alpha Centauri"]),
            MapEdge(story_id=scifi.id, map_id=s_map.id, from_node_id=s_n["Jupiter Station"], to_node_id=s_n["Outer Rim"])
        ]
        db.add_all(s_edges)

        # --- HISTORICAL MAP ---
        h_map = Map(story_id=historical.id, name="Kingdoms of the West", name_it="Regni d'Occidente", description="The territories of France and England during the Hundred Years' War.", description_it="I territori di Francia e Inghilterra durante la Guerra dei Cent'anni.", image_url="historical_map.jpg")
        db.add(h_map)
        db.flush()

        h_nodes = [
            MapNode(story_id=historical.id, map_id=h_map.id, name="London", name_it="Londra", node_type="city", x=500, y=200, icon="🏰", is_starting_location=True),
            MapNode(story_id=historical.id, map_id=h_map.id, name="Calais", name_it="Calais", node_type="city", x=500, y=400, icon="⚓"),
            MapNode(story_id=historical.id, map_id=h_map.id, name="Paris", name_it="Parigi", node_type="city", x=550, y=550, icon="⚜️"),
            MapNode(story_id=historical.id, map_id=h_map.id, name="Bordeaux", name_it="Bordeaux", node_type="city", x=200, y=800, icon="🍷")
        ]
        db.add_all(h_nodes)
        db.flush()
        
        h_n = {n.name: n.id for n in h_nodes}
        h_edges = [
            MapEdge(story_id=historical.id, map_id=h_map.id, from_node_id=h_n["London"], to_node_id=h_n["Calais"]),
            MapEdge(story_id=historical.id, map_id=h_map.id, from_node_id=h_n["Calais"], to_node_id=h_n["Paris"]),
            MapEdge(story_id=historical.id, map_id=h_map.id, from_node_id=h_n["Paris"], to_node_id=h_n["Bordeaux"])
        ]
        db.add_all(h_edges)

        db.commit()
        click.echo(click.style("✓ Map data seeded successfully!", fg='green'))
        
    except Exception as e:
        db.rollback()
        click.echo(click.style(f"Error seeding maps: {str(e)}", fg='red'))
    finally:
        db.close()

if __name__ == '__main__':
    cli()
