from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from core.api_client import CollabookAPI
import logging

logger = logging.getLogger(__name__)

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """
        Override the default login redirect URL to check if the user 
        needs to create a character (backend validation).
        """
        # Get the default redirect URL (respects 'next' param, LOGIN_REDIRECT_URL, etc.)
        default_url = super().get_login_redirect_url(request)
        
        if request.user.is_authenticated:
            try:
                # The token is set in request.session by the user_logged_in signal
                token = request.session.get('token')
                if token:
                    # Verify user status with backend
                    user_data = CollabookAPI.get_current_user(token)
                    character = user_data.get('character')
                    
                    # Check if character exists and has a profession (indicating setup is complete)
                    # This logic mirrors accounts/views.py LoginView
                    if character and character.get('profession'):
                        return default_url
                    else:
                        logger.info(f"User {request.user.username} missing character/profession. Redirecting to creation.")
                        return resolve_url('character:create')
                else:
                    logger.warning(f"No token found for user {request.user.username} in session adapter.")
            except Exception as e:
                logger.error(f"Error in MyAccountAdapter checking character status: {e}")
                
        return default_url
