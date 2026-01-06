from django.views.generic import TemplateView
from .models import Character, Story, BackendUser

class RulesView(TemplateView):
    template_name = 'game/rules.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Default goal
        goal = 10
        
        # Try to get user's active story goal
        if self.request.user.is_authenticated:
            # Note: self.request.user is the Django user, but we link to BackendUser via username or we need to find the character directly
            # The backend/frontend auth mapping is a bit complex in this hybrid setup.
            # Assuming django user username matches backend user username
            try:
                backend_user = BackendUser.objects.filter(username=self.request.user.username).first()
                if backend_user:
                    # Get most recent active character
                    character = Character.objects.filter(user=backend_user, status='active').order_by('-created_at').first()
                    if character:
                        goal = character.story.survival_goal_days
            except Exception:
                pass
                
        context['survival_goal'] = goal
        return context
