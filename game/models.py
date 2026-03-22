from django.db import models
from django.conf import settings
import uuid

# BackendUser removed in favor of integrated User model

class Story(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    world_description = models.TextField()
    genre = models.CharField(max_length=100, null=True, blank=True)
    
    # Localization
    title_it = models.CharField(max_length=255, null=True, blank=True)
    world_description_it = models.TextField(null=True, blank=True)
    genre_it = models.CharField(max_length=100, null=True, blank=True)

    survival_goal_days = models.IntegerField(default=10)
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='stories', db_column='created_by', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'stories'
        verbose_name_plural = "Stories"

    def __str__(self):
        return self.title

class Character(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='characters', db_column='user_id', on_delete=models.CASCADE)
    story = models.ForeignKey(Story, related_name='characters', db_column='story_id', on_delete=models.DO_NOTHING)
    insertion_point = models.TextField(null=True, blank=True)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('dead', 'Dead'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    
    # Game state summary (moved from Story)
    current_state = models.TextField(null=True, blank=True)
    
    # Survival stats
    hunger = models.IntegerField(default=100)
    thirst = models.IntegerField(default=100)
    fatigue = models.IntegerField(default=0)
    days_survived = models.IntegerField(default=0)
    last_played_date = models.DateTimeField(null=True, blank=True)
    
    # Death tracking
    deaths = models.IntegerField(default=0)
    can_resurrect = models.BooleanField(default=True)
    
    gold = models.IntegerField(default=0)
    current_location = models.ForeignKey('MapNode', db_column='current_location_id', null=True, blank=True, on_delete=models.SET_NULL, related_name='characters_present', help_text="La posizione attuale del personaggio sulla mappa")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'characters'

    def __str__(self):
        return f"{self.user.username} in {self.story.title}"
    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_instance = Character.objects.get(pk=self.pk)
                # If status changes from something else to active, cleanup data
                if old_instance.status != 'active' and self.status == 'active':
                    self.cleanup_for_restart()
            except Character.DoesNotExist:
                # New object being saved with a predefined PK
                pass
        super().save(*args, **kwargs)

    def cleanup_for_restart(self):
        """Delete turns and reset survival stats for a fresh start."""
        # Delete turns
        Turn.objects.filter(character=self).delete()
        # Reset survival stats
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 0
        self.days_survived = 0
        self.current_state = None
        self.insertion_point = None
        self.gold = 0
        # XP and Level might also be reset if desired, but request implies starting from zero
        # Request says "riparte con un'avventura da zero come ora e quindi i dati della vecchia andrebbero cancellati"
        # Since BackendUser holds stats like hp, xp, level, we might need to reset those too if they are linked.
        # However, BackendUser seems to be shared across characters? (ForeignKey user_id)
        # Looking at models.py, stats are in BackendUser.
        # But wait, Character has hunger/thirst/fatigue.
        # Let's also check if we should reset the user stats.
        # For now, let's keep it to character-specific data.

class Turn(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    story = models.ForeignKey(Story, db_column='story_id', on_delete=models.DO_NOTHING)
    character = models.ForeignKey(Character, db_column='character_id', on_delete=models.CASCADE)
    user_action = models.TextField()
    narration = models.TextField()
    turn_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'turns'

    def __str__(self):
        return f"Turn {self.turn_number} - {self.character}"

class Quest(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    story = models.ForeignKey(Story, db_column='story_id', on_delete=models.DO_NOTHING, help_text="La storia a cui appartiene questa missione")
    title = models.CharField(max_length=255, help_text="Il titolo della missione")
    description = models.TextField(help_text="Descrizione dettagliata della missione")
    quest_type = models.CharField(
        max_length=50, 
        choices=[('MAIN', 'Main Quest'), ('SIDE', 'Side Quest')],
        default='MAIN',
        help_text="Tipo di missione: Principale o Secondaria"
    )
    objectives = models.TextField(default="[]", help_text="Lista degli obiettivi (formato JSON)")
    xp_reward = models.IntegerField(default=100, help_text="Punti Esperienza (XP) guadagnati al completamento")
    gold_reward = models.IntegerField(default=50, help_text="Oro guadagnato al completamento")
    item_rewards = models.TextField(default="[]", null=True, blank=True, help_text="Oggetti ottenuti come ricompensa (formato JSON)")
    quest_giver = models.CharField(max_length=255, null=True, blank=True, help_text="Nome dell'NPC che assegna la missione")
    quest_giver_description = models.TextField(null=True, blank=True, help_text="Descrizione dell'NPC che assegna la missione")
    is_repeatable = models.BooleanField(default=False, help_text="Se la missione può essere completata più volte")
    required_level = models.IntegerField(default=1, help_text="Livello minimo richiesto per attivare la missione")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'quests'

    def __str__(self):
        return self.title

class Enemy(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    story = models.ForeignKey(Story, db_column='story_id', on_delete=models.DO_NOTHING, help_text="La storia a cui appartiene questo nemico")
    name = models.CharField(max_length=255, help_text="Il nome del nemico")
    description = models.TextField(null=True, blank=True, help_text="Descrizione fisica e comportamentale")
    enemy_type = models.CharField(
        max_length=50, 
        choices=[('COMMON', 'Common'), ('ELITE', 'Elite'), ('BOSS', 'Boss')],
        default='COMMON',
        help_text="Grado di pericolosità del nemico"
    )
    level = models.IntegerField(default=1, help_text="Livello di difficoltà")
    hp = models.IntegerField(default=50, help_text="Punti Vita iniziali")
    max_hp = models.IntegerField(default=50, help_text="Punti Vita massimi")
    attack = models.IntegerField(default=5, help_text="Potenza d'attacco")
    defense = models.IntegerField(default=5, help_text="Valore di difesa")
    xp_reward = models.IntegerField(default=20, help_text="XP guadagnati sconfiggendolo")
    gold_min = models.IntegerField(default=5, help_text="Oro minimo rilasciato")
    gold_max = models.IntegerField(default=15, help_text="Oro massimo rilasciato")
    loot_table = models.TextField(default="[]", null=True, blank=True, help_text="Lista degli oggetti droppabili (formato JSON)")
    image_url = models.TextField(null=True, blank=True, help_text="Nome del file immagine in static/images")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'enemies'
        verbose_name_plural = "Enemies"

    def __str__(self):
        return self.name

class NPC(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    story = models.ForeignKey(Story, related_name='npcs', db_column='story_id', on_delete=models.DO_NOTHING, help_text="La storia a cui appartiene questo NPC")
    name = models.CharField(max_length=255, help_text="Il nome dell'NPC")
    description = models.TextField(null=True, blank=True, help_text="Descrizione e ruolo dell'NPC nel mondo")
    image_url = models.TextField(null=True, blank=True, help_text="Nome del file immagine in static/images")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'npcs'
        verbose_name = "NPC"
        verbose_name_plural = "NPCs"

    def __str__(self):
        return self.name

class Item(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    gold_cost = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'items'

    def __str__(self):
        return self.name

class Map(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    story = models.ForeignKey(Story, db_column='story_id', related_name='maps', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    name_it = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    description_it = models.TextField(null=True, blank=True)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'maps'
        verbose_name = "Map"
        verbose_name_plural = "Maps"

    def __str__(self):
        return self.name

class MapNode(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    story = models.ForeignKey(Story, db_column='story_id', on_delete=models.DO_NOTHING)
    map = models.ForeignKey(Map, db_column='map_id', related_name='nodes', on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey('self', db_column='parent_id', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    name_it = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    description_it = models.TextField(null=True, blank=True)
    node_type = models.CharField(max_length=50)
    x = models.IntegerField(default=500)
    y = models.IntegerField(default=500)
    icon = models.CharField(max_length=100, null=True, blank=True)
    is_starting_location = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'map_nodes'
        verbose_name = "Map Node"
        verbose_name_plural = "Map Nodes"

    def __str__(self):
        return self.name

class MapEdge(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    story = models.ForeignKey(Story, db_column='story_id', on_delete=models.DO_NOTHING)
    map = models.ForeignKey(Map, db_column='map_id', related_name='edges', on_delete=models.CASCADE, null=True, blank=True)
    from_node = models.ForeignKey(MapNode, related_name='edges_from', db_column='from_node_id', on_delete=models.CASCADE)
    to_node = models.ForeignKey(MapNode, related_name='edges_to', db_column='to_node_id', on_delete=models.CASCADE)
    travel_description = models.TextField(null=True, blank=True)
    bidirectional = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'map_edges'
        verbose_name = "Map Edge"
        verbose_name_plural = "Map Edges"

    def __str__(self):
        return f"{self.from_node} -> {self.to_node}"
