from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.utils.translation import gettext as _
from core.api_client import CollabookAPI
import json
import re
from asgiref.sync import sync_to_async
from game.models import Turn, Character, Story
from django.core.mail import send_mail

def clean_narration(text):
    """
    Remove JSON metadata and other non-narrative elements from the narration text.
    Handle cases where the LLM might have returned a raw JSON string or embedded metadata.
    """
    if not text:
        return text
    
    # Step 1: Remove Markdown code blocks if present (handle both complete and incomplete)
    # First try to match complete code blocks
    text = re.sub(r'```(?:json)?\s*(\{.*?\})\s*```', r'\1', text, flags=re.DOTALL).strip()
    
    # Handle incomplete code blocks (no closing ```) - strip the opening
    text = re.sub(r'```(?:json)?\s*', '', text, flags=re.DOTALL).strip()
    # Also strip any trailing ``` that might be left
    text = re.sub(r'\s*```\s*$', '', text, flags=re.DOTALL).strip()

    # Step 2: Try to parse as JSON if it looks like one
    if text.startswith('{'):
        try:
            # Try to find and extract just the "response" field value directly using regex
            # This works even if the JSON is truncated after the response field
            response_match = re.search(r'"response"\s*:\s*"((?:[^"\\]|\\.)*)(?:"|$)', text, flags=re.DOTALL)
            if response_match:
                extracted = response_match.group(1)
                # Unescape common escape sequences
                extracted = extracted.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                return extracted.strip()
            
            # Clean up potential trailing commas and newlines before parsing
            json_text = re.sub(r',\s*\}', '}', text)
            json_text = re.sub(r',\s*\]', ']', json_text)
            
            # Try to fix truncated JSON by closing open structures
            open_braces = json_text.count('{') - json_text.count('}')
            open_brackets = json_text.count('[') - json_text.count(']')
            json_text = json_text + '}' * max(0, open_braces) + ']' * max(0, open_brackets)
            
            data = json.loads(json_text)
            
            def extract_from_dict(d):
                if not isinstance(d, dict):
                    return None
                
                # Check for common wrappers or fields
                # "response" -> { "message": "..." } is common
                if "response" in d:
                    res = d["response"]
                    if isinstance(res, str):
                        return res
                    if isinstance(res, dict):
                        # Recursive check in nested response
                        nested = extract_from_dict(res)
                        if nested: return nested
                
                # Priority list of fields
                for field in ['narration', 'message', 'description', 'text', 'content']:
                    if field in d and d[field] and isinstance(d[field], str):
                        return d[field]
                return None

            if isinstance(data, dict):
                extracted = extract_from_dict(data)
                if extracted:
                    return extracted.strip()
            elif isinstance(data, list) and data:
                # If it's a list, check the first element
                if isinstance(data[0], dict):
                    extracted = extract_from_dict(data[0])
                    if extracted:
                        return extracted.strip()
                    
        except (json.JSONDecodeError, ValueError):
            # If JSON parsing fails, try regex extraction as fallback
            response_match = re.search(r'"response"\s*:\s*"((?:[^"\\]|\\.)*)(?:"|$)', text, flags=re.DOTALL)
            if response_match:
                extracted = response_match.group(1)
                extracted = extracted.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                return extracted.strip()

    # Step 3: Handle mixed strings or legacy cleanup
    # Remove common JSON keys and their values if parsing failed
    cleanup_patterns = [
        r',?\s*"suggested_actions"\s*:\s*\[.*?\]',
        r',?\s*"suggested_actions"\s*:\s*\{.*?\}',
        r',?\s*"player_stats"\s*:\s*\{.*?\}',
        r',?\s*"world"\s*:\s*\{.*?\}',
        r',?\s*"event"\s*:\s*[^,}\]]+',
        r',?\s*"enemy"\s*:\s*[^,}\]]+',
        r',?\s*"status"\s*:\s*[^,}\]]+',
        r',?\s*"metadata"\s*:\s*\{.*?\}',
        r',?\s*"char"\s*:\s*\{[^}]*\}',
        r',?\s*"history"\s*:\s*\[[^\]]*\]',
        r',?\s*"entities"\s*:\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\}?',
    ]
    
    cleaned_text = text
    for pattern in cleanup_patterns:
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL)
    
    # Step 4: Final cleanup of punctuation/whitespace
    # Remove empty braces/brackets if they were left over
    cleaned_text = re.sub(r'\{\s*\}', '', cleaned_text)
    cleaned_text = re.sub(r'\[\s*\]', '', cleaned_text)
    
    # Remove wrapping braces if they still exist (often found in "mixed" responses)
    cleaned_text = cleaned_text.strip()
    if cleaned_text.startswith('{') and (cleaned_text.endswith('}') or not '}' in cleaned_text):
        cleaned_text = re.sub(r'^\{', '', cleaned_text)
        cleaned_text = re.sub(r'\}$', '', cleaned_text)
        cleaned_text = cleaned_text.strip()
        
    # Remove lingering JSON keys like "narration": or "message":
    cleaned_text = re.sub(r'^\s*"(?:narration|message|description|response)"\s*:\s*', '', cleaned_text)
    
    # Remove trailing/leading quotes if they were part of a JSON value
    if (cleaned_text.startswith('"') and cleaned_text.endswith('"')) or \
       (cleaned_text.startswith("'") and cleaned_text.endswith("'")):
        cleaned_text = cleaned_text[1:-1].strip()

    # Remove trailing commas and normalize whitespace
    cleaned_text = re.sub(r',\s*$', '', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_text.strip()

def translate_story_data(story):
    """Translate story title, genre and description if in known list or if DB has translation"""
    from django.utils.translation import get_language
    
    lang = get_language()
    is_italian = lang and lang.startswith('it')

    # 1. Check DB columns (Priority for Custom Worlds)
    if is_italian:
        if story.get('title_it'):
            story['title'] = story['title_it']
        if story.get('world_description_it'):
            story['world_description'] = story['world_description_it']
        if story.get('genre_it'):
            story['genre'] = story['genre_it']
            
    return story

class WorldSelectionView(View):
    template_name = 'world/selection.html'

    async def get(self, request):
        session_token = await sync_to_async(request.session.get)('token')
        if not session_token:
            return redirect('accounts:login')
        
        try:
            stories = await CollabookAPI.list_stories(session_token)
            user = await CollabookAPI.get_current_user(session_token)
            user_characters = user.get('characters', [])
            
            # Add 'existing_char' flag to stories and translate
            for story in stories:
                story['existing_char'] = next((c for c in user_characters if c['story_id'] == story['id']), None)
                translate_story_data(story)
            
            default_worlds = [s for s in stories if s.get('is_default', False)]
            custom_worlds = [s for s in stories if not s.get('is_default', False)]
            
            return await sync_to_async(render)(request, self.template_name, {
                'default_worlds': default_worlds,
                'custom_worlds': custom_worlds,
                'is_admin': user.get('role') == 'admin'
            })
        except Exception as e:
            messages.error(request, str(e))
            return await sync_to_async(render)(request, self.template_name, {'error': str(e)})

    async def post(self, request):
        session_token = await sync_to_async(request.session.get)('token')
        if not session_token:
            return redirect('accounts:login')
        
        story_id = request.POST.get('story_id')
        action = request.POST.get('action')
        
        if action == 'join':
            try:
                # Get current language code from request (sync access to language code is fine)
                lang = request.LANGUAGE_CODE[:2] if hasattr(request, 'LANGUAGE_CODE') else 'en'
                
                character = await CollabookAPI.join_story(story_id, session_token, language=lang)
                await sync_to_async(request.session.__setitem__)('character_id', character['id'])
                await sync_to_async(request.session.__setitem__)('story_id', story_id)
                messages.success(request, _("Entering world..."))
                return redirect('world:journey')
            except Exception as e:
                messages.error(request, str(e))
                return redirect('world:selection')
        
        elif action == 'continue':
            try:
                user = await CollabookAPI.get_current_user(session_token)
                user_characters = user.get('characters', [])
                existing_char = next((c for c in user_characters if c['story_id'] == story_id), None)
                
                if existing_char:
                    await sync_to_async(request.session.__setitem__)('character_id', existing_char['id'])
                    await sync_to_async(request.session.__setitem__)('story_id', story_id)
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

    async def get(self, request):
        session_token = await sync_to_async(request.session.get)('token')
        if not session_token:
            return redirect('accounts:login')
        
        character_id = await sync_to_async(request.session.get)('character_id')
        if not character_id:
            messages.warning(request, _("Please select a world first."))
            return redirect('world:selection')
        
        try:
            history = await sync_to_async(request.session.get)('history', [])
            
            # We need character info for the "Arrival" text if history is empty
            user = await CollabookAPI.get_current_user(session_token)
            character = next((c for c in user.get('characters', []) if c['id'] == character_id), None)
            
            if not character:
                messages.error(request, _("Character not found."))
                return redirect('world:selection')
            
            # Check if game has ended (for PDF download button visibility)
            game_ended = False
            is_victory = False
            is_defeat = False
            is_dead = False
            
            try:
                # Async ORM access
                db_character = await Character.objects.aget(id=character_id)
                # Access related field (story) asynchronously
                db_story = await sync_to_async(lambda: db_character.story)()
                
                # Game ends if character is dead OR survival goal reached
                if db_character.status == 'dead':
                    game_ended = True
                    is_defeat = True
                    is_dead = True
                elif db_character.days_survived >= db_story.survival_goal_days:
                    game_ended = True
                    is_victory = True
            except Exception:
                pass
                
            # Get location name
            current_location_name = None
            if db_character.current_location_id:
                try:
                    from game.models import MapNode
                    locNode = await MapNode.objects.aget(id=db_character.current_location_id)
                    current_location_name = locNode.name_it if (request.LANGUAGE_CODE[:2] == 'it' and locNode.name_it) else locNode.name
                except Exception:
                    pass

            return await sync_to_async(render)(request, self.template_name, {
                'history': history,
                'character': character,
                'user': user,
                'game_ended': game_ended,
                'is_dead': is_dead,
                'is_victory': is_victory,
                'is_defeat': is_defeat,
                'current_location_name': current_location_name,
                'suggested_actions': await sync_to_async(request.session.get)('suggested_actions', []),
                'combat_active': any(e.get('type') == 'enemy' and e.get('active') for e in (history[-1].get('entities', []) if history else []))
            })
        except Exception as e:
            messages.error(request, str(e))
            return redirect('world:selection')

    async def request_restart(self, request):
        session_token = await sync_to_async(request.session.get)('token')
        if not session_token:
            return redirect('accounts:login')
        
        try:
            character_id = await sync_to_async(request.session.get)('character_id')
            
            # Async ORM chain
            db_character = await Character.objects.select_related('user', 'story').aget(id=character_id)
            user = db_character.user
            story = db_character.story

            subject = f"Richiesta Nuova Storia: {user.username} - {story.title}"
            message = f"L'utente {user.username} ({user.email}) ha richiesto di iniziare una nuova storia nel mondo '{story.title}'.\n\nID Personaggio: {character_id}\nID Mondo: {story.id}"
            
            # send_mail is blocking, wrap it
            await sync_to_async(send_mail)(
                subject,
                message,
                'noreply@collabook.com',
                ['mycollabook@gmail.com'],
                fail_silently=False,
            )
            
            messages.success(request, _("Request sent to administrator. You will be notified when the new story is ready."))
            return redirect('world:journey')
        except Exception as e:
            messages.error(request, f"Error sending request: {str(e)}")
            return redirect('world:journey')

    async def post(self, request):
        session_token = await sync_to_async(request.session.get)('token')
        if not session_token:
            return redirect('accounts:login')
        
        action = request.POST.get('action')
        if action == 'request_restart':
            return await self.request_restart(request)

        user_action = request.POST.get('user_action')
        if not user_action:
            return redirect('world:journey')
        
        try:
            lang = request.LANGUAGE_CODE[:2] if hasattr(request, 'LANGUAGE_CODE') else 'en'
            character_id = await sync_to_async(request.session.get)('character_id')
            
            response = await CollabookAPI.interact(character_id, user_action, session_token, language=lang)
            
            history = await sync_to_async(request.session.get)('history', [])
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
                'entities': entities,
                'player_stats': response.get('player_stats')
            })
            history[-1]['narration'] = clean_narration(history[-1]['narration'])
            await sync_to_async(request.session.__setitem__)('history', history)
            await sync_to_async(request.session.__setitem__)('suggested_actions', response.get('suggested_actions', []))

            return redirect('world:journey')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('world:journey')

class AdventureSummaryView(View):
    template_name = 'world/adventure_summary.html'

    async def get(self, request):
        if not await sync_to_async(request.session.get)('token'):
            return redirect('accounts:login')
            
        character_id = await sync_to_async(request.session.get)('character_id')
        if not character_id:
            messages.warning(request, _("No active character found."))
            return redirect('world:selection')
            
        try:
            # Fetch Character and Story Details from managed models
            # Use sync_to_async for ORM operations that are not just single object fetches
            
            def get_summary_data():
                char = Character.objects.select_related('story').get(id=character_id)
                s = char.story
                # Clean up turns
                ts = list(Turn.objects.filter(character_id=character_id).order_by('turn_number'))
                for t in ts:
                    t.narration = clean_narration(t.narration)
                return char, s, ts

            character, story, turns = await sync_to_async(get_summary_data)()
            
            # Localize Story Title
            from django.utils.translation import get_language
            lang = get_language()
            if lang and lang.startswith('it') and story.title_it:
                story.title = story.title_it

            return await sync_to_async(render)(request, self.template_name, {
                'story': story,
                'character': character,
                'turns': turns,
                'date': character.created_at,
            })
            
        except Exception as e:
            messages.error(request, f"Error generating summary: {str(e)}")
            return redirect('world:journey')

class WorldMapView(View):
    template_name = 'world/map.html'

    async def get(self, request):
        session_token = await sync_to_async(request.session.get)('token')
        if not session_token:
            return redirect('accounts:login')
            
        story_id = await sync_to_async(request.session.get)('story_id')
        character_id = await sync_to_async(request.session.get)('character_id')
        
        if not story_id or not character_id:
            messages.warning(request, _("Please select a world first."))
            return redirect('world:selection')
            
        try:
            map_data = await CollabookAPI.get_map(story_id, session_token)
            user = await CollabookAPI.get_current_user(session_token)
            character = next((c for c in user.get('characters', []) if c['id'] == character_id), None)
            story = await CollabookAPI.get_story(story_id, session_token)
            
            # Construct pyvis graph
            from pyvis.network import Network
            import networkx as nx
            
            theme = story.get('world_metadata', {}).get('theme', 'fantasy')
            if theme == 'scifi':
                bgcolor = '#0b0e14'
                font_color = '#e3f2fd'
                edge_color = '#1e88e5'
                node_color = '#1a237e'
                node_border = '#42a5f5'
                accent = '#00e5ff'
            elif theme == 'historical':
                bgcolor = '#f5f5f5'
                font_color = '#222222'
                edge_color = '#333333'
                node_color = '#eeeeee'
                node_border = '#666666'
                accent = '#555555'
            else:
                bgcolor = '#f4e4bc'
                font_color = '#3e2723'
                edge_color = '#5d4037'
                node_color = '#ffffff'
                node_border = '#5d4037'
                accent = '#8d6e63'

            net = Network(height='100%', width='100%', bgcolor='transparent', font_color=font_color)
            
            # Disable physics initially so nodes stay at predefined (x,y) if they exist, but pyvis expects them via add_node layout if we don't supply x,y.
            net.toggle_physics(False)

            current_loc_id = character.get('current_location_id') if character else None

            # Add nodes
            for n in map_data.get('nodes', []):
                is_current = n['id'] == current_loc_id
                
                # Combine icon and name correctly
                icon = n.get('icon', '📍')
                # For language we can check request.LANGUAGE_CODE if needed, for simplicity use name_it if present
                lang = request.LANGUAGE_CODE[:2] if hasattr(request, 'LANGUAGE_CODE') else 'en'
                label = f"{icon}\n{n.get('name_it') if lang == 'it' and n.get('name_it') else n.get('name')}"
                
                # Assign visual properties
                color_dict = {
                    'background': node_color,
                    'border': accent if is_current else node_border,
                    'highlight': {'background': node_color, 'border': accent},
                    'hover': {'background': node_color, 'border': node_border}
                }

                # Set coordinates if provided; need to scale them for pyvis
                x = n.get('x', None)
                y = n.get('y', None)
                if x is not None: x = int(x)
                if y is not None: y = int(y)

                # Store all node properties to pass to js easily
                import re
                desc = n.get('description_it') if lang == 'it' and n.get('description_it') else n.get('description', '')
                if desc is None:
                    desc = ''
                clean_desc = re.sub('<[^<]+>', '', str(desc))
                title_text = f"{label.replace(chr(10), ' ')}\n{clean_desc}"

                net.add_node(
                    n['id'], 
                    label=label, 
                    title=title_text, 
                    color=color_dict,
                    size=40 if is_current else 25,
                    borderWidth=4 if is_current else 2,
                    x=x, y=y,
                    shape='dot',
                    font={'color': font_color, 'size': 14, 'face': 'Inter'},
                    raw_data=n  # Custom attribute containing the raw dict
                )

            # Add edges
            for e in map_data.get('edges', []):
                net.add_edge(
                    e['from_node_id'], 
                    e['to_node_id'],
                    color=edge_color,
                    width=2,
                    arrows='' if e.get('bidirectional') else 'to',
                    dashes=True
                )
            
            # We want to enable interaction
            net.set_options("""
            var options = {
              "physics": {
                "enabled": false
              },
              "interaction": {
                "hover": true,
                "zoomView": true,
                "dragView": true
              },
              "edges": {
                "smooth": {
                  "type": "continuous",
                  "roundness": 0.5
                }
              }
            }
            """)
            
            # Generate the HTML string without dumping it to a file
            html_graph = net.generate_html()
            
            # Inject a custom JS event listener within the generated HTML so it auto-posts
            # messages to the parent window when a node is selected.
            # Pyvis generates a script block initializing `network`. We can append our event directly to it.
            custom_js = """
            network.on("selectNode", function (params) {
                if (params.nodes.length > 0) {
                    var nodeId = params.nodes[0];
                    var nodeData = nodes.get(nodeId);
                    window.parent.postMessage({ type: "nodeSelected", node: nodeData.raw_data }, "*");
                }
            });
            network.on("deselectNode", function (params) {
                window.parent.postMessage({ type: "nodeDeselected" }, "*");
            });
            """
            html_graph = html_graph.replace("return network;", custom_js + "\nreturn network;")
            
            # Inject style for transparency and remove potential margins
            transparency_style = """
            <style>
                * {
                    background-color: transparent !important;
                }
                html, body, .card, .card-body, #mynetwork, .vis-network {
                    background-color: transparent !important;
                    background: transparent !important;
                    border: none !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    height: 100vh !important;
                    width: 100vw !important;
                    overflow: hidden !important;
                    box-shadow: none !important;
                    color: inherit !important;
                }
                /* Hide the default Pyvis Bootstrap card if it exists */
                .card {
                    border: none !important;
                }
            </style>
            """
            html_graph = html_graph.replace("</head>", transparency_style + "</head>")

            return await sync_to_async(render)(request, self.template_name, {
                'map_data': map_data,
                'character': character,
                'story': story,
                'user': user,
                'html_graph': html_graph,
            })
        except Exception as e:
            messages.error(request, f"Error loading map: {str(e)}")
            return redirect('world:journey')

    async def post(self, request):
        session_token = await sync_to_async(request.session.get)('token')
        if not session_token:
            return redirect('accounts:login')
            
        character_id = await sync_to_async(request.session.get)('character_id')
        target_node_id = request.POST.get('target_node_id')
        
        if not character_id or not target_node_id:
            return redirect('world:map')
            
        try:
            await CollabookAPI.move_character(character_id, target_node_id, session_token)
            messages.success(request, _("You have moved to a new location."))
            return redirect('world:journey')
        except Exception as e:
            messages.error(request, f"Movement failed: {str(e)}")
            return redirect('world:map')
