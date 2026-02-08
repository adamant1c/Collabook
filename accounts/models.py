from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Role choices mapped from Backend UserRole
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('PLAYER', 'Player'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PLAYER')
    
    # Character Info
    name = models.CharField(max_length=255, blank=True, null=True) # Display name for the character
    profession = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    avatar_description = models.TextField(null=True, blank=True)
    
    # RPG Stats
    hp = models.IntegerField(default=100)
    max_hp = models.IntegerField(default=100)
    strength = models.IntegerField(default=0)
    magic = models.IntegerField(default=0)
    dexterity = models.IntegerField(default=0)
    defense = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    
    # Account Management fallback fields for backend
    reset_token = models.CharField(max_length=255, null=True, blank=True)
    reset_token_expires = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username
