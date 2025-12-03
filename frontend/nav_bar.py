"""
Navigation bar component for Collabook RPG
Provides a horizontal navigation menu for authenticated users
"""

import streamlit as st
from localization import t, Language

def show_nav_bar():
    """Display horizontal navigation bar at top of page"""
    lang = Language(st.session_state.get("language", "en"))
    
    # Navigation bar styling
    st.markdown("""
        <style>
        /* Navbar styling moved to style.css or inline here if needed, 
           but removing the empty container div wrapper */
        </style>
    """, unsafe_allow_html=True)
    
    # Use a container
    with st.container():
        # Create columns for navigation buttons
        # Adjusted layout: Journey/Worlds | Character | Rules | Lang | Logout
        cols = st.columns([2, 2, 2, 2, 2])
        
        # Get current page (if available)
        current_page = st.session_state.get("current_page", "journey")
        
        # Check if user has a selected story
        has_story = st.session_state.get("story") is not None
        
        with cols[0]:
            if has_story:
                journey_text = "🎮 Your Journey" if lang == Language.EN else "🎮 Il Tuo Viaggio"
                if st.button(journey_text, key="nav_journey", use_container_width=True,
                            type="primary" if current_page == "journey" else "secondary"):
                    st.session_state.current_page = "journey"
                    st.switch_page("pages/journey.py")
            else:
                worlds_text = "🌍 Worlds" if lang == Language.EN else "🌍 Mondi"
                if st.button(worlds_text, key="nav_worlds", use_container_width=True,
                            type="primary" if current_page == "worlds" else "secondary"):
                    st.session_state.current_page = "worlds"
                    st.switch_page("pages/worlds.py")
        
        with cols[1]:
            character_text = "👤 Character" if lang == Language.EN else "👤 Personaggio"
            if st.button(character_text, key="nav_character", use_container_width=True,
                        type="primary" if current_page == "character" else "secondary"):
                st.session_state.current_page = "character"
                st.switch_page("pages/character.py")
        
        with cols[2]:
            rules_text = "📜 Rules" if lang == Language.EN else "📜 Regole"
            if st.button(rules_text, key="nav_rules", use_container_width=True,
                        type="primary" if current_page == "rules" else "secondary"):
                st.session_state.current_page = "rules"
                st.switch_page("pages/rules.py")
        
        with cols[3]:
            logout_text = "🚪 Logout" if lang == Language.EN else "🚪 Esci"
            if st.button(logout_text, key="nav_logout", use_container_width=True, type="secondary"):
                # Clear session and return to login
                st.session_state.token = None
                st.session_state.user = None
                st.session_state.character = None
                st.session_state.story = None
                st.session_state.history = []
                st.session_state.current_page = None
                st.switch_page("app.py")


