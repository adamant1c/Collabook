"""
Multi-language support for Collabook RPG

Supports Italian and English with easy switching.
"""

import os
from enum import Enum

class Language(str, Enum):
    IT = "it"  # Italian
    EN = "en"  # English

# Translation strings
TRANSLATIONS = {
    # Common
    "app_title": {
        "en": "Collabook RPG",
        "it": "Collabook RPG"
    },
    "app_subtitle": {
        "en": "Epic Adventures Await!",
        "it": "Avventure Epiche ti Aspettano!"
    },
    
    # Authentication
    "login": {
        "en": "Login",
        "it": "Accedi"
    },
    "register": {
        "en": "Register",
        "it": "Registrati"
    },
    "username": {
        "en": "Username",
        "it": "Nome utente"
    },
    "password": {
        "en": "Password",
        "it": "Password"
    },
    "email": {
        "en": "Email",
        "it": "Email"
    },
    "name": {
        "en": "Name",
        "it": "Nome"
    },
    "logout": {
        "en": "Logout",
        "it": "Esci"
    },
    
    # Character
    "character_name": {
        "en": "Character Name",
        "it": "Nome Personaggio"
    },
    "profession": {
        "en": "Profession",
        "it": "Professione"
    },
    "level": {
        "en": "Level",
        "it": "Livello"
    },
    "health": {
        "en": "Health",
        "it": "Salute"
    },
    "strength": {
        "en": "Strength",
        "it": "Forza"
    },
    "magic": {
        "en": "Magic",
        "it": "Magia"
    },
    "dexterity": {
        "en": "Dexterity",
        "it": "Destrezza"
    },
    "defense": {
        "en": "Defense",
        "it": "Difesa"
    },
    "experience": {
        "en": "Experience",
        "it": "Esperienza"
    },
    "strength_desc": {
        "en": "Physical Power",
        "it": "Potenza Fisica"
    },
    "magic_desc": {
        "en": "Magical Ability",
        "it": "Abilità Magica"
    },
    "dexterity_desc": {
        "en": "Agility & Speed",
        "it": "Agilità & Velocità"
    },
    "defense_desc": {
        "en": "Damage Resistance",
        "it": "Resistenza Danni"
    },
    
    # Survival
    "survival": {
        "en": "Survival",
        "it": "Sopravvivenza"
    },
    "hunger": {
        "en": "Hunger",
        "it": "Fame"
    },
    "thirst": {
        "en": "Thirst",
        "it": "Sete"
    },
    "fatigue": {
        "en": "Fatigue",
        "it": "Affaticamento"
    },
    "you_are_hungry": {
        "en": "⚠️ You are hungry!",
        "it": "⚠️ Hai fame!"
    },
    "you_are_thirsty": {
        "en": "⚠️ You are thirsty!",
        "it": "⚠️ Hai sete!"
    },
    "you_are_tired": {
        "en": "⚠️ You are tired!",
        "it": "⚠️ Sei stanco!"
    },
    
    # Actions
    "items": {
        "en": "Items",
        "it": "Oggetti"
    },
    "rest": {
        "en": "Rest",
        "it": "Riposa"
    },
    "explore": {
        "en": "Explore",
        "it": "Esplora"
    },
    "attack": {
        "en": "Attack",
        "it": "Attacca"
    },
    "defend": {
        "en": "Defend",
        "it": "Difendi"
    },
    "flee": {
        "en": "Flee",
        "it": "Fuggi"
    },
    
    # Combat
    "combat": {
        "en": "Combat",
        "it": "Combattimento"
    },
    "victory": {
        "en": "Victory!",
        "it": "Vittoria!"
    },
    "defeat": {
        "en": "Defeat",
        "it": "Sconfitta"
    },
    "critical_hit": {
        "en": "CRITICAL HIT!",
        "it": "COLPO CRITICO!"
    },
    
    # Quests
    "quests": {
        "en": "Quests",
        "it": "Missioni"
    },
    "accept_quest": {
        "en": "Accept Quest",
        "it": "Accetta Missione"
    },
    "complete_quest": {
        "en": "Complete Quest",
        "it": "Completa Missione"
    },
    "rewards": {
        "en": "Rewards",
        "it": "Ricompense"
    },
    
    # Worlds
    "worlds": {
        "en": "Worlds",
        "it": "Mondi"
    },
    "select_world": {
        "en": "Select World",
        "it": "Seleziona Mondo"
    },
    "historical": {
        "en": "Historical",
        "it": "Storico"
    },
    "fantasy": {
        "en": "Fantasy",
        "it": "Fantasy"
    },
    "scifi": {
        "en": "Sci-Fi",
        "it": "Fantascienza"
    },
    
    # Messages
    "welcome": {
        "en": "Welcome to Collabook RPG!",
        "it": "Benvenuto a Collabook RPG!"
    },
    "session_expired": {
        "en": "Session expired. Please login again.",
        "it": "Sessione scaduta. Effettua nuovamente l'accesso."
    },
    "error": {
        "en": "Error",
        "it": "Errore"
    },
    "success": {
        "en": "Success",
        "it": "Successo"
    },
    "loading": {
        "en": "Loading...",
        "it": "Caricamento..."
    },
    
    # Game Rules
    "game_rules": {
        "en": "Game Rules",
        "it": "Regole del Gioco"
    },
    "rules_intro": {
        "en": "Welcome to Collabook RPG! Here are the rules of the game:",
        "it": "Benvenuto a Collabook RPG! Ecco le regole del gioco:"
    },
    "rule_1_title": {
        "en": "1. Character Creation",
        "it": "1. Creazione del Personaggio"
    },
    "rule_1_desc": {
        "en": "Create your hero by choosing a profession and writing a backstory. Your stats are rolled randomly.",
        "it": "Crea il tuo eroe scegliendo una professione e scrivendo una storia. Le tue statistiche sono generate casualmente."
    },
    "rule_2_title": {
        "en": "2. Exploration",
        "it": "2. Esplorazione"
    },
    "rule_2_desc": {
        "en": "Explore the world by typing your actions. The AI Dungeon Master will narrate the results.",
        "it": "Esplora il mondo scrivendo le tue azioni. Il Dungeon Master AI narrerà i risultati."
    },
    "rule_3_title": {
        "en": "3. Survival",
        "it": "3. Sopravvivenza"
    },
    "rule_3_desc": {
        "en": "Manage your Hunger, Thirst, and Fatigue. Rest and eat to stay alive.",
        "it": "Gestisci Fame, Sete e Affaticamento. Riposa e mangia per restare vivo."
    },
    
    # Character Creation
    "roll_dice": {
        "en": "Roll Dice & Reveal Stats",
        "it": "Lancia i Dadi & Rivela Statistiche"
    },
    "stats_revealed": {
        "en": "The Fates have spoken! Your stats are:",
        "it": "Il Fato ha parlato! Le tue statistiche sono:"
    },
    "roll_dice_button": {
        "en": "🎲 Roll for Stats",
        "it": "🎲 Lancia i Dadi"
    },
    "stats_generated": {
        "en": "Stats Generated!",
        "it": "Statistiche Generate!"
    },
    
    # Sidebar
    "hp_label": {
        "en": "Health Points (HP)",
        "it": "Punti Salute (HP)"
    },
    "xp_label": {
        "en": "Experience Points (XP)",
        "it": "Punti Esperienza (XP)"
    },
    
    # World Selection
    "choose_your_world": {
        "en": "Choose Your World",
        "it": "Scegli il Tuo Mondo"
    },
    "available_worlds": {
        "en": "🌍 Available Worlds",
        "it": "🌍 Mondi Disponibili"
    },
    "create_world_admin": {
        "en": "➕ Create World (Admin)",
        "it": "➕ Crea Mondo (Admin)"
    },
    "admin_create_worlds": {
        "en": "👑 As an admin, you can create new worlds!",
        "it": "👑 Come admin, puoi creare nuovi mondi!"
    },
    "no_worlds_available": {
        "en": "No worlds available yet.",
        "it": "Nessun mondo disponibile ancora."
    },
    "classic_worlds": {
        "en": "🎭 Classic Worlds",
        "it": "🎭 Mondi Classici"
    },
    "custom_worlds": {
        "en": "🌟 Custom Worlds",
        "it": "🌟 Mondi Personalizzati"
    },
    "only_admin_create": {
        "en": "🔒 Only administrators can create new worlds.",
        "it": "🔒 Solo gli amministratori possono creare nuovi mondi."
    },
    "custom_worlds_approval": {
        "en": "Custom worlds will be available after admin approval.",
        "it": "I mondi personalizzati saranno disponibili dopo l'approvazione dell'admin."
    },
    "continue_adventure": {
        "en": "Continue Adventure",
        "it": "Continua Avventura"
    },
    "enter_world": {
        "en": "Enter World",
        "it": "Entra nel Mondo"
    },
    "error_loading_worlds": {
        "en": "Error loading worlds",
        "it": "Errore nel caricamento dei mondi"
    },
    
    # Navigation
    "your_journey": {
        "en": "🎮 Your Journey",
        "it": "🎮 Il Tuo Viaggio"
    },
    "character_sheet": {
        "en": "👤 Character Sheet",
        "it": "👤 Scheda Personaggio"
    },
    "world_selection": {
        "en": "🌍 Select World",
        "it": "🌍 Scegli Mondo"
    },
}

# World Translations (Keyed by English Title)
WORLD_TRANSLATIONS = {
    "Echoes of the Past": {
        "title": {
            "en": "Echoes of the Past",
            "it": "Echi del Passato"
        },
        "description": {
            "en": "A historically-inspired world set in medieval Europe during the height of the Renaissance. Great kingdoms rise and fall, knights defend their honor, and scholars unlock ancient secrets. Navigate political intrigue,  participate in grand tournaments, or explore forgotten ruins.",
            "it": "Un mondo di ispirazione storica ambientato nell'Europa medievale durante l'apice del Rinascimento. Grandi regni sorgono e cadono, i cavalieri difendono il loro onore e gli studiosi svelano antichi segreti. Naviga intrighi politici, partecipa a grandi tornei o esplora rovine dimenticate."
        }
    },
    "Realm of Eternal Magic": {
        "title": {
            "en": "Realm of Eternal Magic",
            "it": "Regno della Magia Eterna"
        },
        "description": {
            "en": "A high-fantasy realm where magic flows through every living thing. Ancient dragons soar the skies, elven kingdoms hide in enchanted forests, and dwarven cities delve deep into mystical mountains. Dark forces stir in forgotten places, and heroes are called to face legendary quests.",
            "it": "Un regno high-fantasy dove la magia scorre attraverso ogni essere vivente. Antichi draghi solcano i cieli, regni elfici si nascondono in foreste incantate e città naniche scavano nelle profondità di montagne mistiche. Forze oscure si agitano in luoghi dimenticati e gli eroi sono chiamati ad affrontare missioni leggendarie."
        }
    },
    "Horizon Beyond Stars": {
        "title": {
            "en": "Horizon Beyond Stars",
            "it": "Orizzonte Oltre le Stelle"
        },
        "description": {
            "en": "The year is 2347. Humanity has colonized the solar system and made first contact with alien civilizations. Advanced AI, cybernetic augmentations, and faster-than-light travel are commonplace. Navigate space politics, explore alien worlds, uncover corporate conspiracies, or fight in the ongoing conflict between Earth Alliance and the Outer Colonies.",
            "it": "L'anno è il 2347. L'umanità ha colonizzato il sistema solare e ha stabilito il primo contatto con civiltà aliene. IA avanzate, potenziamenti cibernetici e viaggi più veloci della luce sono all'ordine del giorno. Naviga nella politica spaziale, esplora mondi alieni, svela cospirazioni aziendali o combatti nel conflitto in corso tra l'Alleanza Terrestre e le Colonie Esterne."
        }
    }
}

def get_language() -> Language:
    """Get current language from environment or default"""
    lang = os.getenv("LANGUAGE", "en").lower()
    try:
        return Language(lang)
    except ValueError:
        return Language.EN

def t(key: str, lang: Language = None) -> str:
    """
    Translate a key to current language
    
    Args:
        key: Translation key
        lang: Language (default: from env)
        
    Returns:
        Translated string
    """
    if lang is None:
        lang = get_language()
    
    if key not in TRANSLATIONS:
        return f"[{key}]"  # Return key if not found
    
    return TRANSLATIONS[key].get(lang.value, TRANSLATIONS[key].get("en", key))

def set_language(lang: Language):
    """Set application language"""
    os.environ["LANGUAGE"] = lang.value

# Convenience functions
def t_en(key: str) -> str:
    """Translate to English"""
    return t(key, Language.EN)

def t_it(key: str) -> str:
    """Translate to Italian"""
    return t(key, Language.IT)

def t_world(title: str, field: str, lang: Language = None) -> str:
    """
    Translate world title or description
    
    Args:
        title: English title of the world (used as key)
        field: 'title' or 'description'
        lang: Language (default: from env)
    """
    if lang is None:
        lang = get_language()
        
    if title not in WORLD_TRANSLATIONS:
        return title if field == 'title' else ""
        
    return WORLD_TRANSLATIONS[title][field].get(lang.value, WORLD_TRANSLATIONS[title][field].get("en", ""))
