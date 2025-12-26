import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collabook_frontend.settings')
django.setup()

from game.models import Enemy

def verify_enemies():
    try:
        enemies = Enemy.objects.all()
        for enemy in enemies:
            print(f"Enemy: {enemy.name}")
            print(f"Loot Table (type: {type(enemy.loot_table)}): {enemy.loot_table}")
        print("\n✅ Successfully retrieved enemies without JSON errors!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_enemies()
