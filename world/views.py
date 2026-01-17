from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.translation import gettext as _
from core.api_client import CollabookAPI
# Models are imported locally in the view usually to avoid circular imports? 
# No, standard django practice is top level. But I added them in the previous block.
# Wait, I added them *inside* the previous block but outside the class?
# Let's check the previous `replace_file_content` result.
# I added `from game.models import Turn, Character, Story` in the previous step's replacement content.
# However, to be safe and clean, I should move imports to the top if they are needed elsewhere, but they are only used in PDF view.
# Actually, looking at the previous tool call, I included the imports in the replacement text:
# `from game.models import Turn, Character, Story`
# So they are now at the bottom of the file before the class. This is valid Python.
# But I might want to double check if `BackendUser` is needed for `character.user`.
# Character.user is a ForeignKey to BackendUser.
# I accessed `character.user.username`. That should work if `BackendUser` is defined in `game.models` which it is.


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
            
            # Check if game has ended (for PDF download button visibility)
            game_ended = False
            try:
                from game.models import Character as DBCharacter, Story as DBStory
                db_character = DBCharacter.objects.get(id=request.session['character_id'])
                db_story = db_character.story
                
                # Game ends if character is dead OR survival goal reached
                if db_character.status == 'dead' or db_character.days_survived >= db_story.survival_goal_days:
                    game_ended = True
            except Exception:
                # If we can't check, default to False (hide button)
                pass
                
            return render(request, self.template_name, {
                'history': history,
                'character': character,
                'game_ended': game_ended
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

# PDF Generation imports
from django.http import HttpResponse
from django.template.loader import get_template
# from xhtml2pdf import pisa
from game.models import Turn, Character, Story
# We need to import the unmanaged models to query the DB directly

class DownloadStoryPDFView(View):
    def get(self, request):
        if 'token' not in request.session:
            return redirect('accounts:login')
            
        character_id = request.session.get('character_id')
        if not character_id:
            messages.warning(request, _("No active character found."))
            return redirect('world:selection')
            
        try:
            # 1. Fetch Character and Story Details
            # We use the unmanaged models from game.models
            character = Character.objects.get(id=character_id)
            story = character.story
            user = character.user
            
            # 2. Fetch turns
            turns = Turn.objects.filter(character_id=character_id).order_by('turn_number')
            
            # 3. Prepare Context
            context = {
                'story_title': story.title,
                'world_name': story.title, # or world_description summary?
                'character_name': character.user.username, # In backend this links to BackendUser
                'date': character.created_at.strftime("%B %d, %Y"),
                'insertion_point': character.insertion_point,
                'turns': turns,
            }
            
            # 4. Render Template
            template_path = 'world/story_pdf.html'
            template = get_template(template_path)
            html = template.render(context)
            
            # 5. Create PDF
            response = HttpResponse(content_type='application/pdf')
            # filename
            filename = f"{story.title.replace(' ', '_')}-{character.user.username}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            pisa_status = pisa.CreatePDF(
                html, dest=response
            )
            
            if pisa_status.err:
                return HttpResponse('We had some errors <pre>' + html + '</pre>')
                
            return response
            
        except Exception as e:
            messages.error(request, f"Error generating PDF: {str(e)}")
            return redirect('world:journey')
