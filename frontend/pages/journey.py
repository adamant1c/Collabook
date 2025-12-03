import streamlit as st
from localization import t, Language
from api_client import CollabookAPI
from nav_bar import show_nav_bar
from ui_components import apply_custom_css

st.set_page_config(
    page_title="Your Journey - Collabook RPG",
    page_icon="🎮",
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
st.session_state.current_page = "journey"
show_nav_bar()

# Check if world is selected
if "story" not in st.session_state or st.session_state.story is None:
    st.warning("Please select a world first" if lang == Language.EN else "Seleziona prima un mondo")
    st.stop()

# Story history
st.subheader("📜 Your Journey" if lang == Language.EN else "📜 Il Tuo Viaggio")

if not st.session_state.get("history", []):
    insertion = st.session_state.character.get('insertion_point', 'You enter the world...')
    arrival_text = "Your Arrival" if lang == Language.EN else "Il Tuo Arrivo"
    st.markdown(f"""
        <div class="journey-description">
            <strong>{arrival_text}</strong>
            {insertion}
        </div>
    """, unsafe_allow_html=True)
else:
    for i, turn in enumerate(st.session_state.history):
        with st.container():
            action_label = "Your Action" if lang == Language.EN else "La Tua Azione"
            response_label = "The World Responds" if lang == Language.EN else "Il Mondo Risponde"
            
            st.markdown(f"**Turn {i+1} • {action_label}:**")
            st.markdown(f"> _{turn['action']}_")
            st.markdown(f"**{response_label}:**")
            st.markdown(f'<div class="llm-response">{turn["narration"]}</div>', unsafe_allow_html=True)
            st.divider()

# User action input
what_do_label = "✨ What do you do?" if lang == Language.EN else "✨ Cosa fai?"
st.subheader(what_do_label)

with st.form("action_form", clear_on_submit=True):
    action_label = "Describe your action" if lang == Language.EN else "Descrivi la tua azione"
    placeholder = "e.g., I cautiously approach the ancient door, examining it for traps..." if lang == Language.EN else "es., Mi avvicino cautamente all'antica porta, esaminandola per trappole..."
    help_text = "Be descriptive! The AI responds to your creativity." if lang == Language.EN else "Sii descrittivo! L'IA risponde alla tua creatività."
    
    user_action = st.text_area(
        action_label,
        placeholder=placeholder,
        height=100,
        help=help_text
    )
    
    button_text = "🎭 Take Action" if lang == Language.EN else "🎭 Agisci"
    submitted = st.form_submit_button(button_text, use_container_width=True)
    
    if submitted and user_action:
        spinner_text = "🎲 The dungeon master considers..." if lang == Language.EN else "🎲 Il dungeon master riflette..."
        with st.spinner(spinner_text):
            try:
                # Get current language
                current_lang = st.session_state.get("language", "en")
                
                response = CollabookAPI.interact(
                    st.session_state.character['id'], 
                    user_action,
                    st.session_state.token,
                    language=current_lang
                )
                
                if "history" not in st.session_state:
                    st.session_state.history = []
                    
                st.session_state.history.append({
                    "action": user_action,
                    "narration": response['narration']
                })
                st.rerun()
            except Exception as e:
                st.session_state.interaction_error = str(e)
                st.rerun()

# Handle errors outside the form
if "interaction_error" in st.session_state and st.session_state.interaction_error:
    error_msg = st.session_state.interaction_error
    if "404" in error_msg:
        char_not_found = "⚠️ Character not found. Your session may have expired or the character was deleted." if lang == Language.EN else "⚠️ Personaggio non trovato. La tua sessione potrebbe essere scaduta o il personaggio è stato eliminato."
        return_button = "Return to World Selection" if lang == Language.EN else "Torna alla Selezione Mondo"
        
        st.error(char_not_found)
        if st.button(return_button, key="error_return_btn"):
            st.session_state.character = None
            st.session_state.story = None
            del st.session_state.interaction_error
            st.rerun()
    else:
        st.error(f"Error: {error_msg}" if lang == Language.EN else f"Errore: {error_msg}")
        dismiss_text = "Dismiss Error" if lang == Language.EN else "Chiudi Errore"
        if st.button(dismiss_text):
            del st.session_state.interaction_error
            st.rerun()
