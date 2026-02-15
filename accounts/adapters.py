from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from core.api_client import CollabookAPI
import logging
import asyncio

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
                    # ALLAUTH ADAPTER MUST BE SYNC, so we bridge to async here.
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # We are likely in an async view or existing loop (though allauth is sync).
                            # If we are here, it's tricky. But Adapter is usually called from Sync stack in Standard Django.
                            # However, if we are running in Uvicorn, there IS a loop.
                            # BUT, allauth calls this adapter synchronously.
                            # 'asyncio.run' fails if a loop is running.
                            # 'loop.run_until_complete' fails if the loop is already running.
                            # Best safety: Use a separate thread to run the async call if we are stuck.
                            # OR, we might be safe if we are in a sync thread worker? No, we are in async worker.
                            # Wait, if we use `sync_to_async` on the view, we are in async context.
                            # But Allauth views are SYNC (standard Django).
                            # If Allauth views are Sync, they run in a thread. So `asyncio.run` SHOULD work
                            # unless we are in the main thread with a running loop (Uvicorn).
                            
                            # Actually, `asgiref.sync.async_to_sync` is the Django standard way!
                            from asgiref.sync import async_to_sync
                            user_data = async_to_sync(CollabookAPI.get_current_user)(token)
                        else:
                            user_data = asyncio.run(CollabookAPI.get_current_user(token))
                    except RuntimeError:
                        # Fallback for complex loop situations
                        from asgiref.sync import async_to_sync
                        user_data = async_to_sync(CollabookAPI.get_current_user)(token)

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
