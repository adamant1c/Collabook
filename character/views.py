from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.utils.translation import gettext as _
import random
from core.api_client import CollabookAPI
from .forms import CharacterCreationForm
from asgiref.sync import sync_to_async

class CharacterCreationView(View):
    template_name = 'character/creation.html'

    async def get(self, request):
        session_token = await sync_to_async(request.session.get)('token')
        if not session_token:
            return redirect('accounts:login')
        
        # Check if character already has profession (skip creation)
        try:
            user = await CollabookAPI.get_current_user(session_token)
            character = user.get('character')
            if character and character.get('profession'):
                return redirect('world:selection') # TODO: Implement world app
        except Exception as e:
            messages.error(request, str(e))
            return redirect('accounts:login')

        form = CharacterCreationForm()
        stats = await sync_to_async(request.session.get)('rolled_stats')
        character_name = character.get('name') if character else user.get('username', 'Hero')
        return await sync_to_async(render)(request, self.template_name, {'form': form, 'stats': stats, 'character_name': character_name})

    async def post(self, request):
        session_token = await sync_to_async(request.session.get)('token')
        if not session_token:
            return redirect('accounts:login')

        if 'roll_stats' in request.POST:
            stats = {
                "strength": random.randint(3, 18),
                "magic": random.randint(3, 18),
                "dexterity": random.randint(3, 18),
                "defense": random.randint(3, 18),
                "hp": random.randint(50, 100),
                "max_hp": random.randint(100, 200)
            }
            await sync_to_async(request.session.__setitem__)('rolled_stats', stats)
            messages.success(request, _("Stats generated!"))
            return redirect('character:create')
        
        form = CharacterCreationForm(request.POST)
        if form.is_valid():
            stats = await sync_to_async(request.session.get)('rolled_stats')
            if not stats:
                # We need user info for the error page context
                try:
                    user = await CollabookAPI.get_current_user(session_token)
                    username = user.get('username', 'Hero')
                except:
                    username = 'Hero'
                    
                messages.error(request, _("Please roll stats first!"))
                return await sync_to_async(render)(request, self.template_name, {
                    'form': form, 
                    'character_name': username,
                    'error_popup': True,
                    'popup_message': _("You must roll your dice to determine your hero's destiny before beginning the adventure!")
                })
            
            try:
                user = await CollabookAPI.get_current_user(session_token)
                character = user.get('character')
                if not character:
                    messages.error(request, _("Character record not found. Please contact support."))
                    return redirect('character:create')
                
                update_data = {
                    "profession": form.cleaned_data['profession'],
                    "description": form.cleaned_data['description']
                }
                update_data.update(stats)
                
                await CollabookAPI.update_character(session_token, character['id'], update_data)
                
                # Clear stats
                await sync_to_async(request.session.pop)('rolled_stats', None)
                
                messages.success(request, _("Character created!"))
                return redirect('world:selection') # TODO: Implement world app
            except Exception as e:
                messages.error(request, str(e))
                return redirect('character:create')
        
        stats = await sync_to_async(request.session.get)('rolled_stats')
        return await sync_to_async(render)(request, self.template_name, {'form': form, 'stats': stats})

class CharacterSheetView(View):
    template_name = 'character/sheet.html'

    async def get(self, request):
        session_token = await sync_to_async(request.session.get)('token')
        if not session_token:
            return redirect('accounts:login')
        
        try:
            user = await CollabookAPI.get_current_user(session_token)
            character = user.get('character')
            if not character:
                messages.warning(request, _("Please create a character first."))
                return redirect('character:create')
            
            return await sync_to_async(render)(request, self.template_name, {'character': character, 'user': user})
        except Exception as e:
            messages.error(request, str(e))
            return redirect('world:selection')
