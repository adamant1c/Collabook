import streamlit as st
from localization import t, Language

st.set_page_config(
    page_title="Game Rules - Collabook RPG",
    page_icon="📜",
    layout="wide"
)

# Get language
lang = Language(st.session_state.get("language", "en"))

# Title
title = t("game_rules", lang)
st.markdown(f"""
    <h1 style='text-align: center; color: #d4af37; font-family: "Cinzel", serif;'>
        📜 {title} 📜
    </h1>
""", unsafe_allow_html=True)

# Rules content
if lang == Language.EN:
    st.markdown("""
    ## Welcome to Collabook RPG!
    
    Collabook RPG is an AI-powered text-based role-playing game where you create a hero and embark on epic adventures in collaborative storytelling worlds.
    
    ### 🎭 Character Creation
    
    When you first join, you'll create your character by:
    - **Choosing a Profession**: Warrior, Mage, Rogue, Cleric, Ranger, Paladin, Bard, or Druid
    - **Writing a Backstory**: Describe your character's background and motivations
    - **Rolling for Stats**: Click the "Roll for Stats" button to randomly generate your character's attributes:
        - **Strength (💪)**: Physical power for melee combat
        - **Magic (✨)**: Magical ability for spellcasting
        - **Dexterity (🎯)**: Agility and speed for dodging and ranged attacks
        - **Defense (🛡️)**: Damage resistance and armor
        - **HP**: Health Points - when this reaches 0, your character dies
    
    ### 🌍 Exploring Worlds
    
    - Choose from **Classic Worlds** (pre-made adventures) or **Custom Worlds** (created by admins)
    - Each world has its own setting, genre, and storyline
    - Your actions shape the narrative - the AI Dungeon Master responds to your choices
    
    ### ⚔️ Combat & Survival
    
    - **Health Points (HP)**: Monitor your HP carefully. If it reaches 0, your character dies
    - **Hunger & Thirst**: Keep your character fed and hydrated
    - **Fatigue**: Rest regularly to avoid exhaustion
    - **Combat**: Encounter enemies and engage in turn-based battles
    
    ### 📈 Progression
    
    - **Experience Points (XP)**: Gain XP by completing quests and defeating enemies
    - **Leveling Up**: Reach new levels to become more powerful
    - **Quests**: Accept and complete quests for rewards
    
    ### 🎲 Gameplay Tips
    
    1. **Be Descriptive**: The more detailed your actions, the richer the AI's responses
    2. **Manage Resources**: Keep an eye on your survival stats
    3. **Explore Thoroughly**: Investigate your surroundings for hidden opportunities
    4. **Think Strategically**: Combat requires careful planning
    5. **Have Fun**: This is your story - be creative and enjoy the adventure!
    
    ---
    
    ### 🔙 Navigation
    
    Use the sidebar to navigate between pages and manage your character.
    """)
else:  # Italian
    st.markdown("""
    ## Benvenuto a Collabook RPG!
    
    Collabook RPG è un gioco di ruolo testuale basato su AI dove crei un eroe e intraprendi avventure epiche in mondi di narrazione collaborativa.
    
    ### 🎭 Creazione del Personaggio
    
    Quando ti unisci per la prima volta, creerai il tuo personaggio:
    - **Scegliendo una Professione**: Guerriero, Mago, Ladro, Chierico, Ranger, Paladino, Bardo o Druido
    - **Scrivendo una Storia**: Descrivi il background e le motivazioni del tuo personaggio
    - **Lanciando i Dadi per le Statistiche**: Clicca il pulsante "Lancia i Dadi" per generare casualmente gli attributi del tuo personaggio:
        - **Forza (💪)**: Potenza fisica per il combattimento corpo a corpo
        - **Magia (✨)**: Abilità magica per lanciare incantesimi
        - **Destrezza (🎯)**: Agilità e velocità per schivare e attacchi a distanza
        - **Difesa (🛡️)**: Resistenza ai danni e armatura
        - **HP**: Punti Salute - quando raggiunge 0, il tuo personaggio muore
    
    ### 🌍 Esplorare i Mondi
    
    - Scegli tra **Mondi Classici** (avventure pre-create) o **Mondi Personalizzati** (creati dagli admin)
    - Ogni mondo ha il proprio setting, genere e trama
    - Le tue azioni plasmano la narrativa - il Dungeon Master AI risponde alle tue scelte
    
    ### ⚔️ Combattimento & Sopravvivenza
    
    - **Punti Salute (HP)**: Monitora attentamente i tuoi HP. Se raggiungono 0, il tuo personaggio muore
    - **Fame & Sete**: Mantieni il tuo personaggio nutrito e idratato
    - **Affaticamento**: Riposa regolarmente per evitare l'esaurimento
    - **Combattimento**: Incontra nemici e ingaggia battaglie a turni
    
    ### 📈 Progressione
    
    - **Punti Esperienza (XP)**: Guadagna XP completando missioni e sconfiggendo nemici
    - **Salire di Livello**: Raggiungi nuovi livelli per diventare più potente
    - **Missioni**: Accetta e completa missioni per ricompense
    
    ### 🎲 Consigli di Gioco
    
    1. **Sii Descrittivo**: Più dettagliate sono le tue azioni, più ricche saranno le risposte dell'AI
    2. **Gestisci le Risorse**: Tieni d'occhio le tue statistiche di sopravvivenza
    3. **Esplora Accuratamente**: Investiga i tuoi dintorni per opportunità nascoste
    4. **Pensa Strategicamente**: Il combattimento richiede pianificazione attenta
    5. **Divertiti**: Questa è la tua storia - sii creativo e goditi l'avventura!
    
    ---
    
    ### 🔙 Navigazione
    
    Usa la barra laterale per navigare tra le pagine e gestire il tuo personaggio.
    """)

# Back button
if st.button("← Back to Home" if lang == Language.EN else "← Torna alla Home"):
    st.switch_page("app.py")
