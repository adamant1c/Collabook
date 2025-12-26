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
    current_state = models.TextField(null=True, blank=True)
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
    story = models.ForeignKey(Story, db_column='story_id', on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=255)
    description = models.TextField()
    quest_type = models.CharField(
        max_length=50, 
        choices=[('MAIN', 'Main Quest'), ('SIDE', 'Side Quest')],
        default='MAIN'
    )
    objectives = models.JSONField(default=list)
    xp_reward = models.IntegerField(default=0)
    gold_reward = models.IntegerField(default=0)
    item_rewards = models.JSONField(default=list, null=True, blank=True)
    quest_giver = models.CharField(max_length=255, null=True, blank=True)
    quest_giver_description = models.TextField(null=True, blank=True)
    is_repeatable = models.BooleanField(default=False)
    required_level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'quests'

    def __str__(self):
        return self.title

class Enemy(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    story = models.ForeignKey(Story, db_column='story_id', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    enemy_type = models.CharField(
        max_length=50, 
        choices=[('COMMON', 'Common'), ('ELITE', 'Elite'), ('BOSS', 'Boss')],
        default='COMMON'
    )
    level = models.IntegerField(default=1)
    hp = models.IntegerField()
    max_hp = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()
    xp_reward = models.IntegerField(default=0)
    gold_min = models.IntegerField(default=0)
    gold_max = models.IntegerField(default=0)
    loot_table = models.JSONField(default=list, null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'enemies'
        verbose_name_plural = "Enemies"

    def __str__(self):
        return self.name

class NPC(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    story = models.ForeignKey(Story, related_name='npcs', db_column='story_id', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)
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
