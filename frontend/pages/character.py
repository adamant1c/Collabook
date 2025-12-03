import streamlit as st
from localization import t, Language
from nav_bar import show_nav_bar
from ui_components import apply_custom_css

st.set_page_config(
    page_title="Character Sheet - Collabook RPG",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom RPG theme
apply_custom_css()

# Get language
lang = Language(st.session_state.get("language", "en"))

# Check authentication
if "token" not in st.session_state or st.session_state.token is None:
    st.error("Please login first" if lang == Language.EN else "Effettua prima l'accesso")
    st.stop()

# Show navigation bar
st.session_state.current_page = "character"
show_nav_bar()

# Get user and character data
user = st.session_state.get("user", {})
character = st.session_state.get("character", {})

# Page title
title = "Character Sheet" if lang == Language.EN else "Scheda Personaggio"
st.title(f"👤 {title}")

# Character header
st.markdown(f"""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(145deg, #d4af37, #ffd700); 
                border-radius: 10px; margin-bottom: 2rem; border: 2px solid #8b4513;'>
        <h2 style='margin: 0; color: #2a1810; font-family: "Cinzel", serif;'>
            ⚔️ {user.get('name', 'Hero')} ⚔️
        </h2>
        <div style='font-size: 1.1rem; color: #5d4e37; margin-top: 0.5rem;'>
            {user.get('profession', 'Adventurer')} • Level {user.get('level', 1)}
        </div>
    </div>
""", unsafe_allow_html=True)

# Stats layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚔️ Combat Stats" if lang == Language.EN else "⚔️ Statistiche di Combattimento")
    
    # HP
    hp_label = "Health Points" if lang == Language.EN else "Punti Salute"
    st.metric(f"❤️ {hp_label}", f"{user.get('hp', 0)} / {user.get('max_hp', 100)}")
    
    # Core stats with descriptions
    strength_desc = t("strength_desc", lang)
    magic_desc = t("magic_desc", lang)
    dexterity_desc = t("dexterity_desc", lang)
    defense_desc = t("defense_desc", lang)
    
    st.metric(f"💪 {t('strength', lang)}", user.get('strength', 0), help=strength_desc)
    st.metric(f"✨ {t('magic', lang)}", user.get('magic', 0), help=magic_desc)
    st.metric(f"🎯 {t('dexterity', lang)}", user.get('dexterity', 0), help=dexterity_desc)
    st.metric(f"🛡️ {t('defense', lang)}", user.get('defense', 0), help=defense_desc)

with col2:
    st.subheader("📊 Progression" if lang == Language.EN else "📊 Progressione")
    
    level_label = "Level" if lang == Language.EN else "Livello"
    st.metric(f"📊 {level_label}", user.get('level', 1))
    
    # XP calculation
    xp_thresholds = {1: 100, 2: 300, 3: 600, 4: 1000, 5: 1500, 6: 2100, 
                    7: 2800, 8: 3600, 9: 4500}
    next_level_xp = xp_thresholds.get(user.get('level', 1), 4500 + (user.get('level', 1) - 9) * 1000)
    current_xp = user.get('xp', 0)
    
    xp_label = "Experience" if lang == Language.EN else "Esperienza"
    st.metric(f"🌟 {xp_label}", f"{current_xp} / {next_level_xp}")
    
    # XP Progress bar
    xp_progress = min(100, (current_xp / next_level_xp) * 100)
    st.progress(xp_progress / 100)
    
    st.markdown("---")
    
    st.subheader("🍖💧😴 Survival" if lang == Language.EN else "🍖💧😴 Sopravvivenza")
    
    if character:
        # Hunger
        hunger = character.get("hunger", 100)
        hunger_label = "Hunger" if lang == Language.EN else "Fame"
        st.metric(f"🍖 {hunger_label}", f"{hunger}/100")
        st.progress(hunger / 100)
        
        # Thirst
        thirst = character.get("thirst", 100)
        thirst_label = "Thirst" if lang == Language.EN else "Sete"
        st.metric(f"💧 {thirst_label}", f"{thirst}/100")
        st.progress(thirst / 100)
        
        # Fatigue
        fatigue = character.get("fatigue", 0)
        fatigue_label = "Fatigue" if lang == Language.EN else "Affaticamento"
        st.metric(f"😴 {fatigue_label}", f"{fatigue}/100")
        st.progress(fatigue / 100)

# Character backstory
if user.get('description'):
    st.markdown("---")
    backstory_label = "📜 Backstory" if lang == Language.EN else "📜 Storia"
    st.subheader(backstory_label)
    st.write(user.get('description'))

# Role badge
st.markdown("---")
role_label = "Role" if lang == Language.EN else "Ruolo"
role_color = "#8b0000" if user.get('role') == 'admin' else "#4682b4"
st.markdown(f"""
    <div style='text-align: center; padding: 1rem; background: {role_color}; 
                border-radius: 8px; color: white; font-weight: bold;'>
        👑 {role_label}: {user.get('role', 'player').upper()}
    </div>
""", unsafe_allow_html=True)
