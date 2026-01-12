"""
Context processors for Collabook frontend.
Makes certain data available to all templates.
"""

def character_info(request):
    """
    Inject current character survival info into all templates.
    Used to display survival counter in navbar.
    """
    context = {}
    
    if not request.session.get('token') or not request.session.get('character_id'):
        return context
    
    try:
        from game.models import Character, Story
        character = Character.objects.get(id=request.session['character_id'])
        story = character.story
        
        print(f"DEBUG context_processor: days_survived={character.days_survived}, survival_goal_days={story.survival_goal_days}")
        
        context['character_survival'] = {
            'days_survived': max(1, character.days_survived),
            'survival_goal': story.survival_goal_days,
            'days_remaining': story.survival_goal_days - character.days_survived,
            'is_active': character.status == 'active'
        }
        
        print(f"DEBUG context_processor: context={context}")
    except Exception as e:
        # If anything fails, return empty context (navbar won't show counter)
        print(f"DEBUG context_processor ERROR: {e}")
        import traceback
        traceback.print_exc()
        pass
    
    return context

