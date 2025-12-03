import streamlit as st
from api_client import CollabookAPI
from localization import t, Language
from ui_components import apply_custom_css, render_hp_bar

st.set_page_config(
    page_title="Collabook RPG", 
    page_icon="🎲", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom RPG theme
apply_custom_css()

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "character" not in st.session_state:
    st.session_state.character = None
if "story" not in st.session_state:
    st.session_state.story = None
if "history" not in st.session_state:
    st.session_state.history = []
if "in_combat" not in st.session_state:
    st.session_state.in_combat = False
if "combat_enemy" not in st.session_state:
    st.session_state.combat_enemy = None
if "language" not in st.session_state:
    st.session_state.language = "en"  # Default English

def check_backend() -> bool:
    """Check if backend is available"""
    try:
        import requests
        import os
        BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def show_sidebar_character_stats():
    """Display character stats in sidebar (informational only)"""
    lang = Language(st.session_state.get("language", "en"))
    user = st.session_state.get("user")
    character = st.session_state.get("character")
    
    if not user:
        return
    
    with st.sidebar:
        st.markdown(f"""
            <div style='text-align: center; padding: 1rem; background: linear-gradient(145deg, #d4af37, #ffd700); 
                        border-radius: 10px; margin-bottom: 1rem; border: 2px solid #8b4513;'>
                <h2 style='margin: 0; color: #2a1810; font-family: "Cinzel", serif;'>
                    ⚔️ {user.get('name', 'Hero')} ⚔️
                </h2>
                <div style='font-size: 0.9rem; color: #5d4e37; margin-top: 0.5rem;'>
                    {user.get('profession', 'Adventurer')}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Level & Role Badge
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div style='text-align: center; background: #2d5016; color: #ffd700; 
                            padding: 0.5rem; border-radius: 8px; font-weight: bold;'>
                    📊 Level {user.get('level', 1)}
                </div>
            """, unsafe_allow_html=True)
        with col2:
            role_color = "#8b0000" if user.get('role') == 'admin' else "#4682b4"
            st.markdown(f"""
                <div style='text-align: center; background: {role_color}; color: white; 
                            padding: 0.5rem; border-radius: 8px; font-weight: bold;'>
                    👑 {user.get('role','player').upper()}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # HP Bar
        hp_label = t("hp_label", lang)
        render_hp_bar(user.get('hp', 100), user.get('max_hp', 100), label=hp_label)
        
        # Core stats with descriptions
        from ui_components import render_stat_card
        
        strength_desc = t("strength_desc", lang)
        render_stat_card(f"{t('strength', lang)} ({strength_desc})", user.get('strength', 0), icon="💪")
        
        magic_desc = t("magic_desc", lang)
        render_stat_card(f"{t('magic', lang)} ({magic_desc})", user.get('magic', 0), icon="✨")
        
        dexterity_desc = t("dexterity_desc", lang)
        render_stat_card(f"{t('dexterity', lang)} ({dexterity_desc})", user.get('dexterity', 0), icon="🎯")
        
        defense_desc = t("defense_desc", lang)
        render_stat_card(f"{t('defense', lang)} ({defense_desc})", user.get('defense', 0), icon="🛡️")
        
        st.markdown("---")
        
        # Logout button
        logout_text = "🚪 Logout" if lang == Language.EN else "🚪 Esci"
        if st.button(logout_text, use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.character = None
            st.session_state.story = None
            st.session_state.history = []
            st.rerun()

# Include all the auth functions from original app.py
# (show_auth_page, show_login, show_registration, show_password_reset, show_character_creation)
# These remain unchanged for now...

# Import these functions from the original file structure
from app_auth import show_auth_page, show_character_creation

def main():
    """Main application entry point with navigation"""
    
    # Check backend connection
   if not check_backend():
        st.error("⚠️ Backend service is offline. Please start the backend first.")
        st.info("Run: `docker-compose up`")
        return
    
    lang = Language(st.session_state.get("language", "en"))
    
    # Route based on authentication state
    if st.session_state.token is None:
        show_auth_page()
        return
    
    # Fetch user data if not already loaded
    if st.session_state.user is None:
        try:
            st.session_state.user = CollabookAPI.get_current_user(st.session_state.token)
            st.session_state.character = st.session_state.user.get("character")
        except Exception as e:
            st.error(f"Failed to load user data: {str(e)}")
            st.session_state.token = None
            st.rerun()
            return
    
    # Check if character needs customization (first login)
    character = st.session_state.character
    if character and not character.get("profession"):
        show_character_creation()
        return
    
    # Show sidebar with character stats
    show_sidebar_character_stats()
    
    # Define navigation pages
    if st.session_state.story is None:
        # Before world selection - show only world selection
        worlds_page = st.Page("pages/worlds.py", title=t("world_selection", lang), icon="🌍")
        rules_page = st.Page("pages/rules.py", title=t("game_rules", lang), icon="📜")
        
        pg = st.navigation([worlds_page, rules_page])
    else:
        # After world selection - show full navigation
        journey_page = st.Page("pages/journey.py", title=t("your_journey", lang), icon="🎮")
        character_page = st.Page("pages/character.py", title=t("character_sheet", lang), icon="👤")
        rules_page = st.Page("pages/rules.py", title=t("game_rules", lang), icon="📜")
        worlds_page = st.Page("pages/worlds.py", title=t("world_selection", lang), icon="🌍")
        
        pg = st.navigation([journey_page, character_page, worlds_page, rules_page])
    
    # Run the selected page
    pg.run()

if __name__ == "__main__":
    main()
