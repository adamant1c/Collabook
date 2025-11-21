import streamlit as st
from api_client import CollabookAPI

st.set_page_config(page_title="Collabook", page_icon="📖", layout="wide")

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "character" not in st.session_state:
    st.session_state.character = None
if "story" not in st.session_state:
    st.session_state.story = None
if "history" not in st.session_state:
    st.session_state.history = []

# Page navigation
def main():
    st.title("📖 Collabook")
    st.markdown("### Collaborative Story Generation Platform")
    
    # Check backend connection
    try:
        import requests
        import os
        BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            st.sidebar.success("✓ Backend Connected")
        else:
            st.sidebar.error("✗ Backend Error")
            return
    except Exception as e:
        st.sidebar.error(f"✗ Backend Offline: {str(e)[:50]}")
        st.info("🔧 Please start the backend service first.")
        return
    
    # Navigation based on state
    if st.session_state.user is None:
        show_user_creation()
    elif st.session_state.story is None:
        show_story_selection()
    else:
        show_game_interface()

def show_user_creation():
    """Page for creating user profile"""
    st.header("Create Your Character")
    
    with st.form("user_form"):
        name = st.text_input("Character Name", placeholder="e.g., Aria the Bold")
        profession = st.text_input("Profession", placeholder="e.g., Wandering Knight")
        description = st.text_area("Character Description", 
                                   placeholder="Describe your character's background, personality, skills...")
        avatar_description = st.text_area("Avatar Description", 
                                          placeholder="Describe how your character looks...")
        
        submitted = st.form_submit_button("Create Character")
        
        if submitted and name:
            try:
                user = CollabookAPI.create_user(name, profession, description, avatar_description)
                st.session_state.user = user
                st.success(f"✓ Character '{name}' created!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating character: {str(e)}")

def show_story_selection():
    """Page for selecting or creating a story"""
    st.header(f"Welcome, {st.session_state.user['name']}!")
    
    tab1, tab2 = st.tabs(["Join Existing Story", "Create New Story"])
    
    with tab1:
        st.subheader("Available Stories")
        try:
            stories = CollabookAPI.list_stories()
            if not stories:
                st.info("No stories available yet. Create one!")
            else:
                for story in stories:
                    with st.expander(f"📚 {story['title']} ({story.get('genre', 'Unknown')})"):
                        st.markdown(f"**World:** {story['world_description']}")
                        st.markdown(f"**Current State:** {story.get('current_state', 'Starting...')}")
                        if st.button(f"Join '{story['title']}'", key=f"join_{story['id']}"):
                            try:
                                character = CollabookAPI.join_story(story['id'], st.session_state.user['id'])
                                st.session_state.character = character
                                st.session_state.story = story
                                st.success(f"✓ Joined '{story['title']}'!")
                                st.info(f"**Your Introduction:** {character['insertion_point']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error joining story: {str(e)}")
        except Exception as e:
            st.error(f"Error loading stories: {str(e)}")
    
    with tab2:
        st.subheader("Create a New Story")
        with st.form("story_form"):
            title = st.text_input("Story Title", placeholder="e.g., The Lost Kingdom")
            genre = st.selectbox("Genre", ["Fantasy", "Sci-Fi", "Mystery", "Horror", "Adventure"])
            world_description = st.text_area("World Description", 
                                             placeholder="Describe the world, its rules, setting, atmosphere...")
            
            submitted = st.form_submit_button("Create Story")
            
            if submitted and title and world_description:
                try:
                    story = CollabookAPI.create_story(title, world_description, genre)
                    character = CollabookAPI.join_story(story['id'], st.session_state.user['id'])
                    st.session_state.story = story
                    st.session_state.character = character
                    st.success(f"✓ Story '{title}' created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating story: {str(e)}")

def show_game_interface():
    """Interactive game interface"""
    st.header(f"📖 {st.session_state.story['title']}")
    
    # Sidebar with info
    with st.sidebar:
        st.subheader("Your Character")
        st.write(f"**Name:** {st.session_state.user['name']}")
        st.write(f"**Profession:** {st.session_state.user.get('profession', 'N/A')}")
        st.write(f"**Description:** {st.session_state.user.get('description', 'N/A')}")
        
        if st.button("← Leave Story"):
            st.session_state.story = None
            st.session_state.character = None
            st.session_state.history = []
            st.rerun()
    
    # Story history
    st.subheader("Story So Far")
    
    if not st.session_state.history:
        st.info(f"**Introduction:** {st.session_state.character.get('insertion_point', 'You enter the story...')}")
    else:
        for i, turn in enumerate(st.session_state.history):
            with st.container():
                st.markdown(f"**Turn {i+1}: Your Action**")
                st.markdown(f"> _{turn['action']}_")
                st.markdown(f"**Narration:**")
                st.markdown(turn['narration'])
                st.divider()
    
    # User input
    st.subheader("What do you do?")
    
    with st.form("action_form", clear_on_submit=True):
        user_action = st.text_area("Describe your action", 
                                   placeholder="e.g., I draw my sword and approach the mysterious door...",
                                   height=100)
        submitted = st.form_submit_button("🎭 Act")
        
        if submitted and user_action:
            with st.spinner("The story unfolds..."):
                try:
                    response = CollabookAPI.interact(st.session_state.character['id'], user_action)
                    st.session_state.history.append({
                        "action": user_action,
                        "narration": response['narration']
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
