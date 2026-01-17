from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.conf import settings
import jwt
import datetime
import uuid
from game.models import BackendUser
# from core.rpg_stats import initialize_character_stats_simple

@receiver(user_logged_in)
def sync_user_with_backend(sender, user, request, **kwargs):
    """
    On login (including Google OAuth), ensure user exists in BackendUser table
    and generate a JWT token for session.
    """
    print(f"DEBUG: Signal triggered for user {user.username}")
    
    # 1. Check/Create Backend User
    try:
        backend_user, created = BackendUser.objects.get_or_create(
            username=user.username,
            defaults={
                'id': str(uuid.uuid4()),
                'email': user.email,
                'password_hash': 'oauth_user', # Placeholder
                'role': 'PLAYER',
                'name': user.first_name or user.username,
                'is_active': True,
                'created_at': datetime.datetime.utcnow(),
            }
        )
        
        if created:
            print(f"DEBUG: Created new BackendUser for {user.username}")
            # Initialize basic stats if needed (using a simplified version or raw SQL if model is unmanaged)
            # Since BackendUser is unmanaged, we can't save directly if we modify fields that aren't defaults?
            # Actually unmanaged = False means Django won't create the table, but ORM works if table exists.
            # We need to set default stats.
            backend_user.hp = 100
            backend_user.max_hp = 100
            backend_user.level = 1
            backend_user.save()
            
    except Exception as e:
        print(f"ERROR: Failed to sync BackendUser: {str(e)}")
        # If we can't sync, we shouldn't proceed? Or just log?
        return

    # 2. Generate JWT Token
    # Must match the algorithm and secret of the Backend
    secret_key = settings.SECRET_KEY
    algorithm = "HS256"
    
    payload = {
        "sub": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    
    try:
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        # Ensure token is string
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            
        # 3. Store in Session
        request.session['token'] = token
        request.session['username'] = user.username
        print(f"DEBUG: Token generated and stored in session for {user.username}")
        
    except Exception as e:
        print(f"ERROR: Failed to generate token: {str(e)}")
