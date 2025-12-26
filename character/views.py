from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.utils.translation import gettext as _
import random
from core.api_client import CollabookAPI
from .forms import CharacterCreationForm

class CharacterCreationView(View):
    template_name = 'character/creation.html'

    def get(self, request):
        if 'token' not in request.session:
            return redirect('accounts:login')
        
        # Check if character already has profession (skip creation)
        try:
            user = CollabookAPI.get_current_user(request.session['token'])
            character = user.get('character')
            if character and character.get('profession'):
                return redirect('world:selection') # TODO: Implement world app
        except Exception as e:
            messages.error(request, str(e))
            return redirect('accounts:login')

        form = CharacterCreationForm()
        stats = request.session.get('rolled_stats')
        character_name = character.get('name') if character else user.get('username', 'Hero')
        return render(request, self.template_name, {'form': form, 'stats': stats, 'character_name': character_name})

    def post(self, request):
        if 'token' not in request.session:
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
            request.session['rolled_stats'] = stats
            messages.success(request, _("Stats generated!"))
            return redirect('character:create')
        
        form = CharacterCreationForm(request.POST)
        if form.is_valid():
            stats = request.session.get('rolled_stats')
            if not stats:
                messages.error(request, _("Please roll stats first!"))
                return render(request, self.template_name, {
                    'form': form, 
                    'character_name': user.get('username', 'Hero'),
                    'error_popup': True,
                    'popup_message': _("You must roll your dice to determine your hero's destiny before beginning the adventure!")
                })
            
            try:
                user = CollabookAPI.get_current_user(request.session['token'])
                character = user.get('character')
                if not character:
                    messages.error(request, _("Character record not found. Please contact support."))
                    return redirect('character:create')
                
                update_data = {
                    "profession": form.cleaned_data['profession'],
                    "description": form.cleaned_data['description']
                }
                update_data.update(stats)
                
                CollabookAPI.update_character(request.session['token'], character['id'], update_data)
                
                # Clear stats
                del request.session['rolled_stats']
                
                messages.success(request, _("Character created!"))
                return redirect('world:selection') # TODO: Implement world app
            except Exception as e:
                messages.error(request, str(e))
                return redirect('character:create')
        
        stats = request.session.get('rolled_stats')
        return render(request, self.template_name, {'form': form, 'stats': stats})
