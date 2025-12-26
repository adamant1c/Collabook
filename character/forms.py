from django import forms
from django.utils.translation import gettext_lazy as _

class CharacterCreationForm(forms.Form):
    PROFESSION_CHOICES = [
        ('Warrior', _('Warrior')),
        ('Mage', _('Mage')),
        ('Rogue', _('Rogue')),
        ('Cleric', _('Cleric')),
        ('Ranger', _('Ranger')),
        ('Paladin', _('Paladin')),
        ('Bard', _('Bard')),
        ('Druid', _('Druid')),
    ]

    profession = forms.ChoiceField(label=_("Profession"), choices=PROFESSION_CHOICES)
    description = forms.CharField(label=_("Backstory"), widget=forms.Textarea(attrs={'rows': 5}), help_text=_("Describe your character's background..."))
