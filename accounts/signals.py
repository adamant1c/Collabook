from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.conf import settings
import jwt
import datetime

@receiver(user_logged_in)
def generate_jwt_for_backend(sender, user, request, **kwargs):
    """
    On login (including Google OAuth), generate a JWT token for session.
    The backend now uses the unified accounts_user table.
    """
    # Generate JWT Token
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
            
        # Store in Session
        request.session['token'] = token
        request.session['username'] = user.username
        
    except Exception as e:
        print(f"ERROR: Failed to generate token: {str(e)}")
