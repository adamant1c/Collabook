from django.contrib import admin
from django import forms
from django.conf import settings
import os
from .models import BackendUser, Story, Character, Turn, Quest, Enemy, Item, NPC

def get_image_choices():
    """Returns a list of image filenames from static/images"""
    image_dir = os.path.join(settings.BASE_DIR, 'static', 'images')
    choices = [('', '---------')] # Default empty choice
    
    if os.path.exists(image_dir):
        # List common image extensions
        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
        for f in sorted(os.listdir(image_dir)):
            if f.lower().endswith(valid_extensions):
                # Use the filename as both label and value
                # Frontend will prepend /static/images/
                choices.append((f, f))
    return choices

class EnemyAdminForm(forms.ModelForm):
    image_url = forms.ChoiceField(choices=[], required=False)

    class Meta:
        model = Enemy
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image_url'].choices = get_image_choices()

class NPCAdminForm(forms.ModelForm):
    image_url = forms.ChoiceField(choices=[], required=False)

    class Meta:
        model = NPC
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image_url'].choices = get_image_choices()

@admin.register(BackendUser)
class BackendUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'hp', 'max_hp', 'level', 'is_active', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('role', 'level', 'is_active')

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'is_default', 'created_at')
    search_fields = ('title', 'genre')
    list_filter = ('is_default', 'genre')

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('user', 'story', 'status', 'days_survived', 'hunger', 'thirst', 'fatigue', 'gold', 'created_at')
    list_filter = ('status', 'story')
    search_fields = ('user__username', 'story__title')

@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ('character', 'story', 'turn_number', 'created_at')
    list_filter = ('story', 'character')
    readonly_fields = ('created_at',)

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'story', 'quest_type', 'required_level', 'xp_reward', 'gold_reward', 'created_at')
    list_filter = ('story', 'quest_type')
    search_fields = ('title',)

@admin.register(Enemy)
class EnemyAdmin(admin.ModelAdmin):
    form = EnemyAdminForm
    list_display = ('name', 'story', 'enemy_type', 'level', 'hp', 'max_hp', 'attack', 'defense', 'image_url')
    list_filter = ('story', 'enemy_type')
    search_fields = ('name',)

@admin.register(NPC)
class NPCAdmin(admin.ModelAdmin):
    form = NPCAdminForm
    list_display = ('name', 'story', 'image_url')
    list_filter = ('story',)
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'gold_cost')
    list_filter = ('item_type',)
    search_fields = ('name',)

