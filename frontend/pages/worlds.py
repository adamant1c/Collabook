import streamlit as st
from localization import t, Language
from api_client import CollabookAPI
from nav_bar import show_nav_bar
from ui_components import apply_custom_css

st.set_page_config(
    page_title="Select World - Collabook RPG",
    page_icon="🌍",
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
st.session_state.current_page = "worlds"
show_nav_bar()

# Define functions first
def display_story_card(story, current_lang):
    """Display a story card with join button"""
    with st.expander(f"📚 {story['title']} • {story.get('genre', 'Adventure')}"):
        world_label = "World" if current_lang == Language.EN else "Mondo"
        st.markdown(f"**{world_label}:** {story['world_description']}")
        
        if story.get('current_state'):
            st.markdown(f"*{story['current_state']}*")
        
        # Check if user already has a character in this story
        user_characters = st.session_state.user.get('characters', [])
        existing_char = next((c for c in user_characters if c['story_id'] == story['id']), None)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if existing_char:
                continue_text = t("continue_adventure", current_lang)
                if st.button(continue_text, key=f"continue_{story['id']}"):
                    st.session_state.character = existing_char
                    st.session_state.story = story
                    success_msg = f"✓ Resuming adventure in '{story['title']}'..." if current_lang == Language.EN else f"✓ Riprendendo l'avventura in '{story['title']}'..."
                    st.success(success_msg)
                    st.switch_page("pages/journey.py")
            else:
                enter_text = t("enter_world", current_lang)
                if st.button(enter_text, key=f"join_{story['id']}"):
                    try:
                        character = CollabookAPI.join_story(
                            story['id'], 
                            st.session_state.token,
                            language=current_lang.value
                        )
                        # Refresh user to get the new character in the list
                        st.session_state.user = CollabookAPI.get_current_user(st.session_state.token)
                        st.session_state.character = character
                        st.session_state.story = story
                        success_msg = f"✓ Entering '{story['title']}'..." if current_lang == Language.EN else f"✓ Entrando in '{story['title']}'..."
                        st.success(success_msg)
                        st.rerun()
                    except Exception as e:
                        error_text = "Error" if current_lang == Language.EN else "Errore"
                        st.error(f"{error_text}: {str(e)}")

def show_world_creation_form(current_lang):
    """World creation form (admin only)"""
    create_world_label = "Create a New World" if current_lang == Language.EN else "Crea un Nuovo Mondo"
    st.subheader(create_world_label)
    
    with st.form("world_form"):
        title_label = "World Title" if current_lang == Language.EN else "Titolo del Mondo"
        title = st.text_input(title_label, placeholder="e.g., The Shattered Realms")
        
        genre_label = "Genre" if current_lang == Language.EN else "Genere"
        genre = st.selectbox(genre_label, [
            "Fantasy",
            "Science Fiction",
            "Horror",
            "Mystery",
            "Historical",
            "Cyberpunk",
            "Post-Apocalyptic",
            "Steampunk"
        ])
        
        desc_label = "World Description" if current_lang == Language.EN else "Descrizione del Mondo"
        placeholder = "Describe the setting, rules, atmosphere, and key features of this world..." if current_lang == Language.EN else "Descrivi l'ambientazione, le regole, l'atmosfera e le caratteristiche principali di questo mondo..."
        world_description = st.text_area(desc_label, placeholder=placeholder, height=200)
        
        button_text = "🌍 Create World" if current_lang == Language.EN else "🌍 Crea Mondo"
        submitted = st.form_submit_button(button_text)
        
        if submitted and title and world_description:
            try:
                story = CollabookAPI.create_story_admin(
                    title=title,
                    world_description=world_description,
                    genre=genre,
                    token=st.session_state.token
                )
                success_msg = f"✓ World '{title}' created!" if current_lang == Language.EN else f"✓ Mondo '{title}' creato!"
                st.success(success_msg)
                st.rerun()
            except Exception as e:
                error_text = "Error" if current_lang == Language.EN else "Errore"
                st.error(f"{error_text}: {str(e)}")

# Page title
st.title(t("choose_your_world", lang))

# Show admin option to create worlds
if st.session_state.user.get('role') == 'admin':
    st.info(t("admin_create_worlds", lang))

tab1_text = t("available_worlds", lang)
tab2_text = t("create_world_admin", lang)
tab1, tab2 = st.tabs([tab1_text, tab2_text])

with tab1:
    try:
        stories = CollabookAPI.list_stories(st.session_state.token)
        
        if not stories:
            st.warning(t("no_worlds_available", lang))
        else:
            # Separate default and custom worlds
            default_worlds = [s for s in stories if s.get('is_default', False)]
            custom_worlds = [s for s in stories if not s.get('is_default', False)]
            
            if default_worlds:
                st.subheader(t("classic_worlds", lang))
                for story in default_worlds:
                    display_story_card(story, lang)
            
            if custom_worlds:
                st.subheader(t("custom_worlds", lang))
                for story in custom_worlds:
                    display_story_card(story, lang)
    except Exception as e:
        error_msg = t("error_loading_worlds", lang)
        st.error(f"{error_msg}: {str(e)}")

with tab2:
    if st.session_state.user.get('role') != 'admin':
        st.warning(t("only_admin_create", lang))
        st.info(t("custom_worlds_approval", lang))
    else:
        show_world_creation_form(lang)
