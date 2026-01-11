from django.db import models
import uuid

class BackendUser(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    username = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default='player')
    name = models.CharField(max_length=255)
    profession = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    avatar_description = models.TextField(null=True, blank=True)
    
    # RPG Stats
    hp = models.IntegerField(default=0)
    max_hp = models.IntegerField(default=200)
    strength = models.IntegerField(default=0)
    magic = models.IntegerField(default=0)
    dexterity = models.IntegerField(default=0)
    defense = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'users'
        verbose_name = "Backend User"

    def __str__(self):
        return self.username

class Story(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    world_description = models.TextField()
    genre = models.CharField(max_length=100, null=True, blank=True)
    survival_goal_days = models.IntegerField(default=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'stories'
        verbose_name_plural = "Stories"

    def __str__(self):
        return self.title

class Character(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    user = models.ForeignKey(BackendUser, related_name='characters', db_column='user_id', on_delete=models.DO_NOTHING)
    story = models.ForeignKey(Story, related_name='characters', db_column='story_id', on_delete=models.DO_NOTHING)
    insertion_point = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, default='active')
    
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'characters'

    def __str__(self):
        return f"{self.user.username} in {self.story.title}"

class Turn(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    story = models.ForeignKey(Story, db_column='story_id', on_delete=models.DO_NOTHING)
    character = models.ForeignKey(Character, db_column='character_id', on_delete=models.DO_NOTHING)
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
