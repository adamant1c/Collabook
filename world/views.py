from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.utils.translation import gettext as _
from core.api_client import CollabookAPI

class WorldSelectionView(View):
    template_name = 'world/selection.html'

    def get(self, request):
        if 'token' not in request.session:
            return redirect('accounts:login')
        
        try:
            stories = CollabookAPI.list_stories(request.session['token'])
            user = CollabookAPI.get_current_user(request.session['token'])
            user_characters = user.get('characters', [])
            
            # Add 'existing_char' flag to stories
            for story in stories:
                story['existing_char'] = next((c for c in user_characters if c['story_id'] == story['id']), None)
            
            default_worlds = [s for s in stories if s.get('is_default', False)]
            custom_worlds = [s for s in stories if not s.get('is_default', False)]
            
            return render(request, self.template_name, {
                'default_worlds': default_worlds,
                'custom_worlds': custom_worlds,
                'is_admin': user.get('role') == 'admin'
            })
        except Exception as e:
            messages.error(request, str(e))
            return render(request, self.template_name, {'error': str(e)})

    def post(self, request):
        if 'token' not in request.session:
            return redirect('accounts:login')
        
        story_id = request.POST.get('story_id')
        action = request.POST.get('action')
        
        if action == 'join':
            try:
                # Get current language code from request or session
                lang = request.LANGUAGE_CODE[:2] if hasattr(request, 'LANGUAGE_CODE') else 'en'
                
                character = CollabookAPI.join_story(story_id, request.session['token'], language=lang)
                request.session['character_id'] = character['id']
                request.session['story_id'] = story_id
                messages.success(request, _("Entering world..."))
                return redirect('world:journey')
            except Exception as e:
                messages.error(request, str(e))
                return redirect('world:selection')
        
        elif action == 'continue':
            try:
                user = CollabookAPI.get_current_user(request.session['token'])
                user_characters = user.get('characters', [])
                existing_char = next((c for c in user_characters if c['story_id'] == story_id), None)
                
                if existing_char:
                    request.session['character_id'] = existing_char['id']
                    request.session['story_id'] = story_id
                    messages.success(request, _("Resuming adventure..."))
                    return redirect('world:journey')
                else:
                    messages.error(request, _("Character not found."))
                    return redirect('world:selection')
            except Exception as e:
                messages.error(request, str(e))
                return redirect('world:selection')
        
        return redirect('world:selection')

class JourneyView(View):
    template_name = 'world/journey.html'

    def get(self, request):
        if 'token' not in request.session:
            return redirect('accounts:login')
        
        if 'character_id' not in request.session:
            messages.warning(request, _("Please select a world first."))
            return redirect('world:selection')
        
        try:
            # We don't have a direct API to get character details by ID easily without iterating user chars
            # But we can assume session has valid ID.
            # Ideally we should fetch character state.
            # For now, let's just render the page. The history is stored in session in Streamlit.
            # In Django, we should probably store history in session too, or fetch it from backend if backend supported it (it doesn't seem to persist history in DB fully for retrieval? actually it does in `interactions` table but API might not expose it easily as a list).
            # Streamlit app stores `st.session_state.history`.
            # We'll use Django session for history.
            
            history = request.session.get('history', [])
            
            # We need character info for the "Arrival" text if history is empty
            user = CollabookAPI.get_current_user(request.session['token'])
            character = next((c for c in user.get('characters', []) if c['id'] == request.session['character_id']), None)
            
            if not character:
                messages.error(request, _("Character not found."))
                return redirect('world:selection')
                
            return render(request, self.template_name, {
                'history': history,
                'character': character
            })
        except Exception as e:
            messages.error(request, str(e))
            return redirect('world:selection')

    def post(self, request):
        if 'token' not in request.session:
            return redirect('accounts:login')
        
        user_action = request.POST.get('user_action')
        if not user_action:
            return redirect('world:journey')
        
        try:
            lang = request.LANGUAGE_CODE[:2] if hasattr(request, 'LANGUAGE_CODE') else 'en'
            character_id = request.session['character_id']
            
            response = CollabookAPI.interact(character_id, user_action, request.session['token'], language=lang)
            
            history = request.session.get('history', [])
            # Fix image URLs to use Django static paths
            entities = response.get('detected_entities', [])
            for entity in entities:
                if 'image_url' in entity and entity['image_url']:
                    # Se l'URL non inizia già con /static/, aggiungilo
                    if not entity['image_url'].startswith('/static/'):
                        entity['image_url'] = f"/static/images/{entity['image_url']}"

            history.append({
                'action': user_action,
                'narration': response['narration'],
                'entities': entities
            })
            request.session['history'] = history
            
            return redirect('world:journey')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('world:journey')
