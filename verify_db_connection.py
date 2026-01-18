import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collabook_frontend.settings')
django.setup()

from game.models import BackendUser

try:
    count = BackendUser.objects.count()
    print(f"SUCCESS: Connected to PostgreSQL.")
    print(f"BackendUser count: {count}")
    
    users = BackendUser.objects.all()[:5]
    if count > 0:
        print("Sample users found:")
        for u in users:
            print(f" - {u.username} (Role: {u.role})")
    else:
        print("No users found (table is empty, but connection worked).")
        
except Exception as e:
    print(f"FAILURE: Could not query BackendUser. Error: {e}")
