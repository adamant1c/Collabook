import streamlit as st
from api_client import CollabookAPI
from localization import t, Language, t_world
from ui_components import (
    apply_custom_css, render_title, render_stat_card, 
    render_quest_card, render_combat_log, render_enemy_card,
    render_level_up_animation, render_dice_roll, render_hp_bar,
    render_survival_counter
)

st.set_page_config(
    page_title="Collabook RPG", 
    page_icon="🎲", 
    layout="wide",
    initial_sidebar_state="collapsed"
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
        else:
            # Redirect to appropriate page based on state
            if st.session_state.story is None:
                # No world selected - go to worlds page
                st.switch_page("pages/worlds.py")
            else:
                # World selected - go to journey page
                st.switch_page("pages/journey.py")

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

def show_auth_page():
    """Authentication page with login and registration"""
    
    # Get current language
    lang = Language(st.session_state.get("language", "en"))
    
    render_title(t("app_title", lang), icon="⚔️")
    
    # Subtitle with translation
    subtitle = t("app_subtitle", lang) if lang == Language.EN else "Avventure Epiche ti Aspettano!"
    welcome_text = "Enter a world of collaborative storytelling and heroic quests" if lang == Language.EN else "Entra in un mondo di narrazione collaborativa e missioni eroiche"
    
    st.markdown(f"""
        <div style='text-align: center; font-family: "Cinzel", serif; font-size: 1.3rem; 
                    color: var(--gold); margin-bottom: 2rem;'>
            🎲 {subtitle} 🎲<br/>
            <span style='font-size: 1rem; color: var(--parchment-light);'>
                {welcome_text}
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # Language selector
    st.markdown("<div style='text-align: right; margin-bottom: 1rem;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([6, 1, 1])
    with col2:
        if st.button("🇬🇧 EN", use_container_width=True, help="English"):
            st.session_state.language = "en"
            st.rerun()
    with col3:
        if st.button("🇮🇹 IT", use_container_width=True, help="Italiano"):
            st.session_state.language = "it"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Show current language
    current_lang = st.session_state.get("language", "en")
    lang_display = "🇬🇧 English" if current_lang == "en" else "🇮🇹 Italiano"
    lang_label = "Language" if current_lang == "en" else "Lingua"
    st.markdown(f"<p style='text-align: right; color: var(--gold); font-size: 0.9rem;'>{lang_label}: {lang_display}</p>", unsafe_allow_html=True)
    
    # Tabs with translations
    login_tab = f"🔐 {t('login', lang)}"
    register_tab = f"✨ {t('register', lang)}"
    reset_tab = "🔑 Reset Password" if lang == Language.EN else "🔑 Recupera Password"
    
    tab1, tab2, tab3 = st.tabs([login_tab, register_tab, reset_tab])
    
    with tab1:
        show_login()
    
    with tab2:
        show_registration()
    
    with tab3:
        show_password_reset()

def show_login():
    """Login form"""
    lang = Language(st.session_state.get("language", "en"))
    
    try:
        # Translated headers
        title = "Login to Your Account" if lang == Language.EN else "Accedi al Tuo Account"
        subtitle = "Continue your epic adventure" if lang == Language.EN else "Continua la tua avventura epica"
        
        st.markdown(f"""
            <h3 style='color: #d4af37; font-family: "Cinzel", serif; 
                       text-shadow: 2px 2px 4px rgba(0,0,0,0.5); text-align: center;'>
                🔐 {title}
            </h3>
            <p style='color: #e8d4a0; text-align: center; margin-bottom: 1.5rem;'>
                {subtitle}
            </p>
            <style>
                /* Login form styling */
                .stTextInput label {{
                    color: #d4af37 !important;
                    font-weight: 600;
                    font-size: 1.05rem;
                }}
                .stTextInput > div > div > input {{
                    background-color: rgba(245, 235, 210, 0.95) !important;
                    color: #3d2f1f !important;
                    border: 2px solid #8b7355 !important;
                }}
                .stTextInput > div > div > input:focus {{
                    border-color: #d4af37 !important;
                    box-shadow: 0 0 8px rgba(212, 175, 55, 0.5);
                }}
            </style>
        """, unsafe_allow_html=True)
        
        # Prepare strings OUTSIDE the form to prevent errors inside
        username_label = f"⚔️ {t('username', lang)}"
        password_label = f"🔑 {t('password', lang)}"
        submit_label = t('login', lang).upper() if lang == Language.EN else "ACCEDI"
        button_label = f"🎮 {submit_label}"
        
        with st.form("login_form"):
            username = st.text_input(username_label)
            password = st.text_input(password_label, type="password")
            
            # Button must be rendered!
            submitted = st.form_submit_button(button_label)
            
            if submitted:
                error_msg = "Please fill in all fields" if lang == Language.EN else "Compila tutti i campi"
                success_msg = "✓ Login successful!" if lang == Language.EN else "✓ Accesso riuscito!"
                error_prefix = "Login failed" if lang == Language.EN else "Accesso fallito"
                
                if not username or not password:
                    st.error(error_msg)
                    return
                
                try:
                    token = CollabookAPI.login(username, password)
                    st.session_state.token = token
                    st.success(success_msg)
                    st.rerun()
                except Exception as e:
                    st.error(f"{error_prefix}: {str(e)}")
    except Exception as e:
        st.error(f"Error rendering login form: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def show_registration():
    """Account registration - character creation happens after login"""
    lang = Language(st.session_state.get("language", "en"))
    
    # Registration header
    title = "Create Account" if lang == Language.EN else "Crea Account"
    subtitle = "Register to begin your adventure" if lang == Language.EN else "Registrati per iniziare l'avventura"
    
    st.markdown(f"""
        <h3 style='color: #d4af37; font-family: "Cinzel", serif;
                   text-shadow: 2px 2px 4px rgba(0,0,0,0.5); text-align: center;'>
            ✨ {title}
        </h3>
        <p style='color: #e8d4a0; text-align: center; margin-bottom: 1.5rem;'>
            {subtitle}
        </p>
        <style>
            /* Registration form styling */
            div[data-baseweb="input"] label {{
                color: #d4af37 !important;
                font-weight: 600;
            }}
        </style>
    """, unsafe_allow_html=True)
    
    with st.form("registration_form"):
        username = st.text_input(f"⚔️ {t('username', lang)}", max_chars=50, 
                                help="This will be your character name too" if lang == Language.EN else "Questo sarà anche il nome del tuo personaggio")
        email = st.text_input(f"📧 {t('email', lang)}")
        password = st.text_input(f"🔑 {t('password', lang)}", type="password")
        password_confirm = st.text_input("🔑 Confirm Password" if lang == Language.EN else "🔑 Conferma Password", type="password")
        
        submit_text = t('register', lang).upper() if lang == Language.EN else "REGISTRATI"
        submitted = st.form_submit_button(f"⚔️ {submit_text}")
        
        if submitted:
            # Validation messages
            fill_all = "Please fill in all required fields" if lang == Language.EN else "Compila tutti i campi obbligatori"
            password_match = "Passwords do not match" if lang == Language.EN else "Le password non corrispondono"
            password_len = "Password must be at least 6 characters" if lang == Language.EN else "La password deve essere di almeno 6 caratteri"
            username_len = "Username must be at least 3 characters" if lang == Language.EN else "Il nome utente deve essere di almeno 3 caratteri"
            success_msg = "✓ Welcome, {name}! Your adventure begins..." if lang == Language.EN else "✓ Benvenuto, {name}! La tua avventura inizia..."
            error_prefix = "Registration failed" if lang == Language.EN else "Registrazione fallita"
            
            if not username or not email or not password:
                st.error(fill_all)
                return
            
            if password != password_confirm:
                st.error(password_match)
                return
            
            if len(password) < 6:
                st.error(password_len)
                return
            
            if len(username) < 3:
                st.error(username_len)
                return
            
            try:
                # Use username as character name - character customization happens after login
                token = CollabookAPI.register(
                    username=username,
                    email=email,
                    password=password,
                    name=username,  # Character name = Username
                    profession=None,  # Will be set after login
                    description=None,  # Will be set after login
                    avatar_description=None
                )
                st.session_state.token = token
                success_text = f"✓ Welcome, {username}! Your adventure begins..." if lang == Language.EN else f"✓ Benvenuto, {username}! La tua avventura inizia..."
                st.success(success_text)
                st.balloons()
                st.rerun()
            except Exception as e:
                error_str = str(e)
                # Translate common error messages to Italian
                if lang == Language.IT:
                    if "Username already registered" in error_str:
                        error_str = "Nome utente già registrato"
                    elif "Email already registered" in error_str:
                        error_str = "Email già registrata"
                    elif "Invalid email format" in error_str:
                        error_str = "Formato email non valido"
                    elif "400 Client Error: Bad Request" in error_str:
                        error_str = "Richiesta non valida. Verifica che tutti i campi siano compilati correttamente."
                    elif "429 Client Error: Too Many Requests" in error_str:
                        error_str = "Troppi tentativi. Riprova tra un'ora."
                
                error_prefix = "Registration failed" if lang == Language.EN else "Registrazione fallita"
                st.error(f"{error_prefix}: {error_str}")



def show_character_creation():
    """Character customization screen after first login"""
    lang = Language(st.session_state.get("language", "en"))
    
    title = "Create Your Hero" if lang == Language.EN else "Crea il Tuo Eroe"
    subtitle = "Customize your character" if lang == Language.EN else "Personalizza il tuo personaggio"
    
    st.markdown(f"""
        <h1 style='text-align: center; color: #d4af37; font-family: "Cinzel", serif;'>
            ⚔️ {title} ⚔️
        </h1>
        <p style='text-align: center; color: #e8d4a0; font-size: 1.2rem; margin-bottom: 2rem;'>
            {subtitle}
        </p>
    """, unsafe_allow_html=True)
    
    character = st.session_state.character
    
    # Initialize stats in session state if not present
    if "rolled_stats" not in st.session_state:
        st.session_state.rolled_stats = None
    
    # Dice roll button (outside form)
    roll_button_text = t("roll_dice_button", lang)
    if st.button(roll_button_text, use_container_width=True):
        import random
        # Roll stats: 3d6 for each stat (range 3-18)
        st.session_state.rolled_stats = {
            "strength": random.randint(3, 18),
            "magic": random.randint(3, 18),
            "dexterity": random.randint(3, 18),
            "defense": random.randint(3, 18),
            "hp": random.randint(50, 100),
            "max_hp": random.randint(100, 200)
        }
        st.rerun()
    
    # Display rolled stats if available
    if st.session_state.rolled_stats:
        stats_title = t("stats_generated", lang)
        st.success(f"✨ {stats_title}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"💪 {t('strength', lang)}", st.session_state.rolled_stats["strength"])
            st.metric(f"✨ {t('magic', lang)}", st.session_state.rolled_stats["magic"])
        with col2:
            st.metric(f"🎯 {t('dexterity', lang)}", st.session_state.rolled_stats["dexterity"])
            st.metric(f"🛡️ {t('defense', lang)}", st.session_state.rolled_stats["defense"])
        with col3:
            st.metric("❤️ HP", st.session_state.rolled_stats["hp"])
            st.metric("❤️ Max HP", st.session_state.rolled_stats["max_hp"])
    
    with st.form("character_creation_form"):
        st.markdown(f"### 👤 {character.get('name', 'Character')}")
        
        # Profession dropdown
        profession_label = f"🛡️ {t('profession', lang)}"
        professions = {
            "en": ["Warrior", "Mage", "Rogue", "Cleric", "Ranger", "Paladin", "Bard", "Druid"],
            "it": ["Guerriero", "Mago", "Ladro", "Chierico", "Ranger", "Paladino", "Bardo", "Druido"]
        }
        profession = st.selectbox(profession_label, professions[lang.value])
        
        # Backstory
        backstory_label = "📜 Backstory" if lang == Language.EN else "📜 Storia"
        backstory_help = "Describe your character's background..." if lang == Language.EN else "Descrivi il background del tuo personaggio..."
        backstory = st.text_area(backstory_label, max_chars=500, help=backstory_help)
        
        submit_text = "Begin Adventure" if lang == Language.EN else "Inizia Avventura"
        submitted = st.form_submit_button(f"⚔️ {submit_text}")
        
        if submitted:
            try:
                # Prepare update data
                update_data = {
                    "profession": profession,
                    "description": backstory
                }
                
                # Add stats if rolled
                if st.session_state.rolled_stats:
                    update_data.update(st.session_state.rolled_stats)
                
                # Update character with profession, backstory, and stats
                CollabookAPI.update_character(
                    st.session_state.token,
                    character["id"],
                    update_data
                )
                
                # Manually update local state to reflect changes
                st.session_state.character["profession"] = profession
                st.session_state.character["description"] = backstory
                if st.session_state.rolled_stats:
                    st.session_state.character.update(st.session_state.rolled_stats)
                
                # Clear rolled stats
                st.session_state.rolled_stats = None
                
                st.success("✓ Character created!" if lang == Language.EN else "✓ Personaggio creato!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")


def show_password_reset():
    """Password reset form"""
    lang = Language(st.session_state.get("language", "en"))
    
    # Translated headers
    title = "Reset Your Password" if lang == Language.EN else "Recupera la Tua Password"
    subtitle = "Recover your account" if lang == Language.EN else "Recupera il tuo account"
    
    st.markdown(f"""
        <h3 style='color: #d4af37; font-family: "Cinzel", serif;
                   text-shadow: 2px 2px 4px rgba(0,0,0,0.5); text-align: center;'>
            🔑 {title}
        </h3>
        <p style='color: #e8d4a0; text-align: center; margin-bottom: 1.5rem;'>
            {subtitle}
        </p>
    """, unsafe_allow_html=True)
    
    step_label = "Step" if lang == Language.EN else "Passo"
    request_text = "Request Reset" if lang == Language.EN else "Richiedi Reset"
    enter_code = "Enter Reset Code" if lang == Language.EN else "Inserisci Codice"
    
    reset_step = st.radio(step_label, [request_text, enter_code], horizontal=True)
    
    if reset_step == request_text:
        with st.form("request_reset_form"):
            email_label = f"📧 {t('email', lang)}" if lang == Language.EN else "📧 Email"
            email = st.text_input(email_label)
            
            button_text = "Send Reset Link" if lang == Language.EN else "Invia Link Reset"
            submitted = st.form_submit_button(button_text)
            
            if submitted and email:
                try:
                    CollabookAPI.request_password_reset(email)
                    success = "✓ If the email exists, a reset link has been sent. Check your console for now (email not configured)." if lang == Language.EN else "✓ Se l'email esiste, un link di reset è stato inviato. Controlla la console per ora (email non configurata)."
                    st.success(success)
                except Exception as e:
                    error = "Error" if lang == Language.EN else "Errore"
                    st.error(f"{error}: {str(e)}")
    else:
        with st.form("reset_password_form"):
            token_label = "Reset Token" if lang == Language.EN else "Token Reset"
            token_help = "Check your email or console logs" if lang == Language.EN else "Controlla la tua email o i log della console"
            new_pass = "New Password" if lang == Language.EN else "Nuova Password"
            confirm_pass = "Confirm New Password" if lang == Language.EN else "Conferma Nuova Password"
            
            token = st.text_input(token_label, help=token_help)
            new_password = st.text_input(new_pass, type="password")
            confirm_password = st.text_input(confirm_pass, type="password")
            
            button_text = "Reset Password" if lang == Language.EN else "Reimposta Password"
            submitted = st.form_submit_button(button_text)
            
            if submitted:
                password_match = "Passwords do not match" if lang == Language.EN else "Le password non corrispondono"
                password_len = "Password must be at least 6 characters" if lang == Language.EN else "La password deve essere di almeno 6 caratteri"
                success_reset = "✓ Password reset successful! You can now login." if lang == Language.EN else "✓ Password reimpostata con successo! Ora puoi accedere."
                error_prefix = "Error" if lang == Language.EN else "Errore"

                if new_password != confirm_password:
                    st.error(password_match)
                    return
                
                if len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                    return
                
                try:
                    CollabookAPI.reset_password(token, new_password)
                    st.success("✓ Password reset successful! You can now login.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def show_main_app():
    """Main application interface"""
    user = st.session_state.user
    
    # Sidebar - Character Sheet Style
    with st.sidebar:
        st.markdown(f"""
            <div style='text-align: center; padding: 1rem; background: linear-gradient(145deg, #d4af37, #ffd700); 
                        border-radius: 10px; margin-bottom: 1rem; border: 2px solid #8b4513;'>
                <h2 style='margin: 0; color: #2a1810; font-family: "Cinzel", serif;'>
                    ⚔️ {user['name']} ⚔️
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
                    📊 Level {user['level']}
                </div>
            """, unsafe_allow_html=True)
        with col2:
            role_color = "#8b0000" if user['role'] == 'admin' else "#4682b4"
            st.markdown(f"""
                <div style='text-align: center; background: {role_color}; color: white; 
                            padding: 0.5rem; border-radius: 8px; font-weight: bold;'>
                    👑 {user['role'].upper()}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Get language for labels
        lang = Language(st.session_state.get("language", "en"))
        
        # HP Bar (consolidated - only one)
        hp_label = t("hp_label", lang)
        render_hp_bar(user['hp'], user['max_hp'], label=hp_label)
        
        # Stats in ornate cards with descriptions
        strength_desc = t("strength_desc", lang)
        render_stat_card(f"{t('strength', lang)} ({strength_desc})", user['strength'], icon="💪")
        
        magic_desc = t("magic_desc", lang)
        render_stat_card(f"{t('magic', lang)} ({magic_desc})", user['magic'], icon="✨")
        
        dexterity_desc = t("dexterity_desc", lang)
        render_stat_card(f"{t('dexterity', lang)} ({dexterity_desc})", user['dexterity'], icon="🎯")
        
        defense_desc = t("defense_desc", lang)
        render_stat_card(f"{t('defense', lang)} ({defense_desc})", user['defense'], icon="🛡️")
        
        # XP Progress
        xp_thresholds = {1: 100, 2: 300, 3: 600, 4: 1000, 5: 1500, 6: 2100, 
                        7: 2800, 8: 3600, 9: 4500}
        next_level_xp = xp_thresholds.get(user['level'], 4500 + (user['level'] - 9) * 1000)
        xp_progress = min(100, (user['xp'] / next_level_xp) * 100)
        st.markdown(f"""
            <div class='stat-card'>
                <strong>🌟 Experience</strong>
                <div style='margin-top: 0.5rem;'>
                    <div style='background: rgba(212,175,55,0.2); border-radius: 5px; height: 20px; position: relative;'>
                        <div class='xp-progress' style='background: linear-gradient(90deg, #d4af37, #ffd700); 
                                    width: {xp_progress}%; height: 100%; border-radius: 5px; 
                                    box-shadow: 0 0 10px rgba(255,215,0,0.5);'></div>
                        <span style='position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); 
                                     font-weight: bold; font-size: 0.85rem; color: #2a1810;'>
                            {user['xp']} / {next_level_xp}
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Phase 5: Survival Stats
        st.markdown("""
            <div style='text-align: center; font-family: "Cinzel", serif; 
                        font-size: 1.2rem; color: #d4af37; margin-bottom: 0.5rem;'>
                🍖💧😴 Survival
            </div>
        """, unsafe_allow_html=True)
        
        # Get character for survival stats
        character = st.session_state.get("character")
        if character:
            # Hunger bar
            hunger = character.get("hunger", 100)
            hunger_color = "#2d5016" if hunger > 50 else "#d4af37" if hunger > 20 else "#8b0000"
            st.markdown(f"""
                <div style='margin-bottom: 0.5rem;'>
                    <div style='font-size: 0.9rem; color: #5d4e37;'>🍖 Hunger: {hunger}/100</div>
""", unsafe_allow_html=True)
            
            # Days Survived Counter
            days_survived = character.get("days_survived", 0)
            render_survival_counter(days_survived)

def show_story_selection():
    """Select or create a story world"""
    lang = Language(st.session_state.get("language", "en"))
    
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
                        show_story_card(story)
                
                if custom_worlds:
                    st.subheader(t("custom_worlds", lang))
                    for story in custom_worlds:
                        show_story_card(story)
        except Exception as e:
            error_msg = t("error_loading_worlds", lang)
            st.error(f"{error_msg}: {str(e)}")
    
    with tab2:
        if st.session_state.user.get('role') != 'admin':
            st.warning(t("only_admin_create", lang))
            st.info(t("custom_worlds_approval", lang))
        else:
            show_world_creation()

def show_story_card(story):
    """Display a story card with join button"""
    lang = Language(st.session_state.get("language", "en"))
    
    # Translate title and description if available
    display_title = t_world(story['title'], 'title', lang) or story['title']
    display_desc = t_world(story['title'], 'description', lang) or story['world_description']
    
    with st.expander(f"📚 {display_title} • {story.get('genre', 'Adventure')}"):
        world_label = "World" if lang == Language.EN else "Mondo"
        st.markdown(f"**{world_label}:** {display_desc}")
        
        if story.get('current_state'):
            st.markdown(f"*{story['current_state']}*")
        
        # Check if user already has a character in this story
        user_characters = st.session_state.user.get('characters', [])
        existing_char = next((c for c in user_characters if c['story_id'] == story['id']), None)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if existing_char:
                continue_text = t("continue_adventure", lang)
                if st.button(continue_text, key=f"continue_{story['id']}"):
                    st.session_state.character = existing_char
                    st.session_state.story = story
                    success_msg = f"✓ Resuming adventure in '{story['title']}'..." if lang == Language.EN else f"✓ Riprendendo l'avventura in '{story['title']}'..."
                    st.success(success_msg)
                    st.rerun()
            else:
                enter_text = t("enter_world", lang)
                if st.button(enter_text, key=f"join_{story['id']}"):
                    try:
                        # Get current language from session state
                        current_lang = st.session_state.get("language", "en")
                        character = CollabookAPI.join_story(
                            story['id'], 
                            st.session_state.token,
                            language=current_lang
                        )
                        # Refresh user to get the new character in the list
                        st.session_state.user = CollabookAPI.get_current_user(st.session_state.token)
                        st.session_state.character = character
                        st.session_state.story = story
                        success_msg = f"✓ Entering '{story['title']}'..." if lang == Language.EN else f"✓ Entrando in '{story['title']}'..."
                        st.success(success_msg)
                        st.rerun()
                    except Exception as e:
                        error_text = "Error" if lang == Language.EN else "Errore"
                        st.error(f"{error_text}: {str(e)}")

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

def render_hp_bar(current_hp, max_hp, label="HP"):
    hp_percentage = (current_hp / max_hp) * 100
    st.markdown(f"""
        <div class='stat-card'>
            <strong>❤️ {label}</strong>
            <div style='margin-top: 0.5rem;'>
                <div style='background: #333; border-radius: 5px; height: 20px; position: relative;'>
                    <div style='background: linear-gradient(90deg, #ff4d4d, #cc0000); 
                                width: {hp_percentage}%; height: 100%; border-radius: 5px; 
                                box-shadow: 0 0 10px rgba(255,0,0,0.5);'></div>
                    <span style='position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); 
                                 font-weight: bold; font-size: 0.85rem; color: white;'>
                        {current_hp} / {max_hp}
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_stat_card(name, value, icon=""):
    st.markdown(f"""
        <div class='stat-card'>
            <strong>{icon} {name}:</strong> <span style='float: right;'>{value}</span>
        </div>
    """, unsafe_allow_html=True)

def show_game_interface():
    """Main game interface with RPG theme"""
    user = st.session_state.user
    
    # Sidebar - Character Sheet Style
    with st.sidebar:
        st.markdown(f"""
            <div style='text-align: center; padding: 1rem; background: linear-gradient(145deg, #d4af37, #ffd700); 
                        border-radius: 10px; margin-bottom: 1rem; border: 2px solid #8b4513;'>
                <h2 style='margin: 0; color: #2a1810; font-family: "Cinzel", serif;'>
                    ⚔️ {user['name']} ⚔️
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
                    📊 Level {user['level']}
                </div>
            """, unsafe_allow_html=True)
        with col2:
            role_color = "#8b0000" if user['role'] == 'admin' else "#4682b4"
            st.markdown(f"""
                <div style='text-align: center; background: {role_color}; color: white; 
                            padding: 0.5rem; border-radius: 8px; font-weight: bold;'>
                    👑 {user['role'].upper()}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Get language for labels
        lang = Language(st.session_state.get("language", "en"))
        
        # HP Bar (consolidated - only one)
        hp_label = t("hp_label", lang)
        render_hp_bar(user['hp'], user['max_hp'], label=hp_label)
        
        # Stats in ornate cards with descriptions
        strength_desc = t("strength_desc", lang)
        render_stat_card(f"{t('strength', lang)} ({strength_desc})", user['strength'], icon="💪")
        
        magic_desc = t("magic_desc", lang)
        render_stat_card(f"{t('magic', lang)} ({magic_desc})", user['magic'], icon="✨")
        
        dexterity_desc = t("dexterity_desc", lang)
        render_stat_card(f"{t('dexterity', lang)} ({dexterity_desc})", user['dexterity'], icon="🎯")
        
        defense_desc = t("defense_desc", lang)
        render_stat_card(f"{t('defense', lang)} ({defense_desc})", user['defense'], icon="🛡️")
        
        # XP Progress
        xp_thresholds = {1: 100, 2: 300, 3: 600, 4: 1000, 5: 1500, 6: 2100, 
                        7: 2800, 8: 3600, 9: 4500}
        next_level_xp = xp_thresholds.get(user['level'], 4500 + (user['level'] - 9) * 1000)
        xp_progress = min(100, (user['xp'] / next_level_xp) * 100)
        st.markdown(f"""
            <div class='stat-card'>
                <strong>🌟 Experience</strong>
                <div style='margin-top: 0.5rem;'>
                    <div style='background: rgba(212,175,55,0.2); border-radius: 5px; height: 20px; position: relative;'>
                        <div class='xp-progress' style='background: linear-gradient(90deg, #d4af37, #ffd700); 
                                    width: {xp_progress}%; height: 100%; border-radius: 5px; 
                                    box-shadow: 0 0 10px rgba(255,215,0,0.5);'></div>
                        <span style='position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); 
                                     font-weight: bold; font-size: 0.85rem; color: #2a1810;'>
                            {user['xp']} / {next_level_xp}
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Phase 5: Survival Stats
        st.markdown("""
            <div style='text-align: center; font-family: "Cinzel", serif; 
                        font-size: 1.2rem; color: #d4af37; margin-bottom: 0.5rem;'>
                🍖💧😴 Survival
            </div>
        """, unsafe_allow_html=True)
        
        # Get character for survival stats
        character = st.session_state.get("character")
        if character:
            # Hunger bar
            hunger = character.get("hunger", 100)
            hunger_color = "#2d5016" if hunger > 50 else "#d4af37" if hunger > 20 else "#8b0000"
            st.markdown(f"""
                <div style='margin-bottom: 0.5rem;'>
                    <div style='font-size: 0.9rem; color: #5d4e37;'>🍖 Hunger: {hunger}/100</div>
                    <div style='background: rgba(93,78,55,0.2); border-radius: 5px; height: 15px;'>
                        <div style='background: {hunger_color}; width: {hunger}%; height: 100%; 
                                    border-radius: 5px; transition: width 0.3s;'></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Thirst bar
            thirst = character.get("thirst", 100)
            thirst_color = "#4682b4" if thirst > 50 else "#d4af37" if thirst > 20 else "#8b0000"
            st.markdown(f"""
                <div style='margin-bottom: 0.5rem;'>
                    <div style='font-size: 0.9rem; color: #5d4e37;'>💧 Thirst: {thirst}/100</div>
                    <div style='background: rgba(93,78,55,0.2); border-radius: 5px; height: 15px;'>
                        <div style='background: {thirst_color}; width: {thirst}%; height: 100%; 
                                    border-radius: 5px; transition: width 0.3s;'></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Fatigue bar
            fatigue = character.get("fatigue", 0)
            fatigue_color = "#2d5016" if fatigue < 50 else "#d4af37" if fatigue < 80 else "#8b0000"
            st.markdown(f"""
                <div style='margin-bottom: 0.5rem;'>
                    <div style='font-size: 0.9rem; color: #5d4e37;'>😴 Fatigue: {fatigue}/100</div>
                    <div style='background: rgba(93,78,55,0.2); border-radius: 5px; height: 15px;'>
                        <div style='background: {fatigue_color}; width: {fatigue}%; height: 100%; 
                                    border-radius: 5px; transition: width 0.3s;'></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Warnings
            warnings = []
            if hunger < 30:
                warnings.append("⚠️ You are hungry!")
            if thirst < 40:
                warnings.append("⚠️ You are thirsty!")
            if fatigue > 70:
                warnings.append("⚠️ You are tired!")
            
            for warning in warnings:
                st.warning(warning)
            
            # Inventory & Rest buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎒 Items", use_container_width=True):
                    st.session_state.show_inventory = True
            with col2:
                if st.button("😴 Rest", use_container_width=True):
                    st.session_state.show_rest = True
        
        st.markdown("---")
        
        # Logout Button
        if st.button("← Leave World", use_container_width=True):
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
                    # Get current language
                    lang = st.session_state.get("language", "en")
                    
                    response = CollabookAPI.interact(
                        st.session_state.character['id'], 
                        user_action,
                        st.session_state.token,
                        language=lang
                    )
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
            st.error("⚠️ Character not found. Your session may have expired or the character was deleted.")
            if st.button("Return to World Selection", key="error_return_btn"):
                st.session_state.character = None
                st.session_state.story = None
                del st.session_state.interaction_error
                st.rerun()
        else:
            st.error(f"Error: {error_msg}")
            # Clear error on next interaction
            if st.button("Dismiss Error"):
                del st.session_state.interaction_error
                st.rerun()

if __name__ == "__main__":
    main()
