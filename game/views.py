from django.views.generic import TemplateView
from .models import Character, Story

class RulesView(TemplateView):
    template_name = 'game/rules.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Default goal
        goal = 10
        
        # Try to get user's active story goal
        if self.request.user.is_authenticated:
            try:
                # Use request.user directly (it now has RPG stats and character relationship)
                character = Character.objects.filter(user=self.request.user, status='active').order_by('-created_at').first()
                if character:
                    goal = character.story.survival_goal_days
            except Exception:
                pass
                
        context['survival_goal'] = goal
        return context
