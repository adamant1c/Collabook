import streamlit as st
from api_client import CollabookAPI
from ui_components import (
    apply_custom_css, render_title, render_stat_card, 
    render_quest_card, render_combat_log, render_enemy_card,
    render_level_up_animation, render_dice_roll, render_hp_bar
)

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

def main():
    """Main application entry point"""
    
    # Check backend connection
    if not check_backend():
        st.error("⚠️ Backend service is offline. Please start the backend first.")
        st.info("Run: `docker-compose up`")
        return
    
    # Route based on authentication state
    if st.session_state.token is None:
        show_auth_page()
    else:
        # Verify token is still valid
        try:
            user = CollabookAPI.get_current_user(st.session_state.token)
            st.session_state.user = user
            show_game_app()
        except:
            # Token expired or invalid
            st.session_state.token = None
            st.session_state.user = None
            st.warning("Session expired. Please login again.")
            st.rerun()

def check_backend():
    """Check if backend is accessible"""
    try:
        import requests
        import os
        BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def show_auth_page():
    """Authentication page with login and registration"""
    
    render_title("Collabook RPG", icon="⚔️")
    st.markdown("""
        <div style='text-align: center; font-family: "Cinzel", serif; font-size: 1.3rem; 
                    color: var(--wood-dark); margin-bottom: 2rem;'>
            🎲 Epic Adventures Await! 🎲<br/>
            <span style='font-size: 1rem; color: var(--stone-gray);'>
                Enter a world of collaborative storytelling and heroic quests
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "✨ Register", "🔑 Reset Password"])
    
    with tab1:
        show_login()
    
    with tab2:
        show_registration()
    
    with tab3:
        show_password_reset()

def show_login():
    """Login form"""
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if not username or not password:
                st.error("Please fill in all fields")
                return
            
            try:
                token = CollabookAPI.login(username, password)
                st.session_state.token = token
                st.success("✓ Login successful!")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {str(e)}")

def show_registration():
    """Registration wizard with guided character creation"""
    st.subheader("Create Your Hero")
    
    with st.form("registration_form"):
        st.markdown("#### Account Information")
        username = st.text_input("Username", max_chars=50, 
                                 help="Your unique username (3-50 characters)")
        email = st.text_input("Email", help="Required for password recovery")
        password = st.text_input("Password", type="password", 
                                help="Minimum 6 characters")
        password_confirm = st.text_input("Confirm Password", type="password")
        
        st.markdown("#### Character Information")
        name = st.text_input("Character Name", 
                            placeholder="e.g., Elara the Wise",
                            help="Your character's display name")
        
        profession = st.selectbox("Profession", [
            "",
            "Warrior - Master of combat and weaponry",
            "Mage - Wielder of arcane magic",
            "Rogue - Skilled in stealth and cunning",
            "Cleric - Healer and divine magic user",
            "Ranger - Expert tracker and archer",
            "Paladin - Holy warrior with divine powers",
            "Bard - Inspirer and jack-of-all-trades",
            "Druid - Nature magic and shapeshifting"
        ])
        
        if profession:
            profession = profession.split(" - ")[0]  # Extract just the name
        
        description = st.text_area("Character Background", 
                                   placeholder="Describe your character's personality, goals, and backstory...",
                                   help="This helps the AI understand your character")
        
        avatar_description = st.text_area("Physical Appearance", 
                                          placeholder="Describe how your character looks...",
                                          help="Hair color, build, distinctive features, clothing style...")
        
        submitted = st.form_submit_button("⚔️ Begin Your Adventure")
        
        if submitted:
            # Validation
            if not all([username, email, password, password_confirm, name]):
                st.error("Please fill in all required fields")
                return
            
            if password != password_confirm:
                st.error("Passwords do not match")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters")
                return
            
            if len(username) < 3:
                st.error("Username must be at least 3 characters")
                return
            
            try:
                token = CollabookAPI.register(
                    username=username,
                    email=email,
                    password=password,
                    name=name,
                    profession=profession if profession else None,
                    description=description if description else None,
                    avatar_description=avatar_description if avatar_description else None
                )
                st.session_state.token = token
                st.success(f"✓ Welcome, {name}! Your adventure begins...")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Registration failed: {str(e)}")

def show_password_reset():
    """Password reset form"""
    st.subheader("Reset Your Password")
    
    reset_step = st.radio("Step", ["Request Reset", "Enter Reset Code"], horizontal=True)
    
    if reset_step == "Request Reset":
        with st.form("request_reset_form"):
            email = st.text_input("Email Address")
            submitted = st.form_submit_button("Send Reset Link")
            
            if submitted and email:
                try:
                    CollabookAPI.request_password_reset(email)
                    st.success("✓ If the email exists, a reset link has been sent. Check your console for now (email not configured).")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        with st.form("reset_password_form"):
            token = st.text_input("Reset Token", help="Check your email or console logs")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            submitted = st.form_submit_button("Reset Password")
            
            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                    return
                
                if len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                    return
                
                try:
                    CollabookAPI.reset_password(token, new_password)
                    st.success("✓ Password reset successful! You can now login.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def show_game_app():
    """Main game interface (after authentication)"""
    
    # Sidebar with user info
    with st.sidebar:
        st.title("🎮 Collabook")
        st.markdown("---")
        st.subheader(f"👤 {st.session_state.user['name']}")
        st.caption(f"@{st.session_state.user['username']}")
        
        if st.session_state.user.get('profession'):
            st.write(f"**Class:** {st.session_state.user['profession']}")
        
        st.write(f"**Level:** {st.session_state.user.get('level', 1)}")
        st.write(f"**XP:** {st.session_state.user.get('xp', 0)}")
        
        # Role badge
        role = st.session_state.user.get('role', 'player')
        if role == 'admin':
            st.info("👑 **Admin**")
        
        st.markdown("---")
        
        if st.button("🚪 Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.character = None
            st.session_state.story = None
            st.session_state.history = []
            st.rerun()
    
    # Main content area
    if st.session_state.story is None:
        show_story_selection()
    else:
        show_game_interface()

def show_story_selection():
    """Select or create a story world"""
    st.title("Choose Your World")
    
    # Show admin option to create worlds
    if st.session_state.user.get('role') == 'admin':
        st.info("👑 As an admin, you can create new worlds!")
    
    tab1, tab2 = st.tabs(["🌍 Available Worlds", "➕ Create World (Admin)"])
    
    with tab1:
        try:
            stories = CollabookAPI.list_stories(st.session_state.token)
            
            if not stories:
                st.warning("No worlds available yet.")
            else:
                # Separate default and custom worlds
                default_worlds = [s for s in stories if s.get('is_default', False)]
                custom_worlds = [s for s in stories if not s.get('is_default', False)]
                
                if default_worlds:
                    st.subheader("🎭 Classic Worlds")
                    for story in default_worlds:
                        show_story_card(story)
                
                if custom_worlds:
                    st.subheader("🌟 Custom Worlds")
                    for story in custom_worlds:
                        show_story_card(story)
        except Exception as e:
            st.error(f"Error loading worlds: {str(e)}")
    
    with tab2:
        if st.session_state.user.get('role') != 'admin':
            st.warning("🔒 Only administrators can create new worlds.")
            st.info("Custom worlds will be available after admin approval.")
        else:
            show_world_creation()

def show_story_card(story):
    """Display a story card with join button"""
    with st.expander(f"📚 {story['title']} • {story.get('genre', 'Adventure')}"):
        st.markdown(f"**World:** {story['world_description']}")
        
        if story.get('current_state'):
            st.markdown(f"*{story['current_state']}*")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button(f"Enter World", key=f"join_{story['id']}"):
                try:
                    character = CollabookAPI.join_story(
                        story['id'], 
                        st.session_state.token
                    )
                    st.session_state.character = character
                    st.session_state.story = story
                    st.success(f"✓ Entering '{story['title']}'...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def show_world_creation():
    """World creation form (admin only)"""
    st.subheader("Create a New World")
    
    with st.form("world_form"):
        title = st.text_input("World Title", placeholder="e.g., The Shattered Realms")
        genre = st.selectbox("Genre", [
            "Fantasy",
            "Science Fiction",
            "Horror",
            "Mystery",
            "Historical",
            "Cyberpunk",
            "Post-Apocalyptic",
            "Steampunk"
        ])
        world_description = st.text_area("World Description", 
                                         placeholder="Describe the setting, rules, atmosphere, and key features of this world...",
                                         height=200)
        
        submitted = st.form_submit_button("🌍 Create World")
        
        if submitted and title and world_description:
            try:
                story = CollabookAPI.create_story_admin(
                    title=title,
                    world_description=world_description,
                    genre=genre,
                    token=st.session_state.token
                )
                st.success(f"✓ World '{title}' created!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

def show_game_interface():
    """Interactive gameplay interface"""
    st.title(f"📖 {st.session_state.story['title']}")
    
    # Sidebar with character stats
    with st.sidebar:
        st.markdown("---")
        st.subheader("📊 Your Stats")
        
        # Get user stats
        user = st.session_state.user
        
        # HP Bar
        hp_percentage = (user['hp'] / user['max_hp']) * 100
        st.markdown(f"**❤️ HP:** {user['hp']}/{user['max_hp']}")
        st.progress(hp_percentage / 100)
        
        # Other stats
        st.write(f"**💪 STR:** {user['strength']}/200")
        st.write(f"**✨ MP:** {user['magic']}/200")
        st.write(f"**🎯 DEX:** {user['dexterity']}/200")
        st.write(f"**🛡️ DEF:** {user['defense']}/200")
        
        # Level and XP
        st.markdown("---")
        st.write(f"**🌟 Level:** {user['level']}")
        st.write(f"**⭐ XP:** {user['xp']}")
        
        # Calculate XP to next level (simplified)
        xp_thresholds = {1: 100, 2: 300, 3: 600, 4: 1000, 5: 1500, 6: 2100, 
                        7: 2800, 8: 3600, 9: 4500}
        next_level_xp = xp_thresholds.get(user['level'], 4500 + (user['level'] - 9) * 1000)
        st.progress(min(user['xp'] / next_level_xp, 1.0))
        st.caption(f"Next level: {next_level_xp} XP")
        
        st.markdown("---")
        
        if st.button("← Leave World"):
            st.session_state.story = None
            st.session_state.character = None
            st.session_state.history = []
            st.rerun()
    
    # Story history
    st.subheader("📜 Your Journey")
    
    if not st.session_state.history:
        insertion = st.session_state.character.get('insertion_point', 'You enter the world...')
        st.info(f"**Your Arrival:** {insertion}")
    else:
        for i, turn in enumerate(st.session_state.history):
            with st.container():
                st.markdown(f"**Turn {i+1} • Your Action:**")
                st.markdown(f"> _{turn['action']}_")
                st.markdown(f"**The World Responds:**")
                st.markdown(turn['narration'])
                st.divider()
    
    # User action input
    st.subheader("✨ What do you do?")
    
    with st.form("action_form", clear_on_submit=True):
        user_action = st.text_area("Describe your action", 
                                   placeholder="e.g., I cautiously approach the ancient door, examining it for traps...",
                                   height=100,
                                   help="Be descriptive! The AI responds to your creativity.")
        
        submitted = st.form_submit_button("🎭 Take Action", use_container_width=True)
        
        if submitted and user_action:
            with st.spinner("🎲 The dungeon master considers..."):
                try:
                    response = CollabookAPI.interact(
                        st.session_state.character['id'], 
                        user_action,
                        st.session_state.token
                    )
                    st.session_state.history.append({
                        "action": user_action,
                        "narration": response['narration']
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
