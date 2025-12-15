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

        submitted = st.form_submit_button(button_label)

        if submitted:
            error_msg = "Please fill in all fields" if lang == Language.EN else "Compila tutti i campi"
            success_msg = "✓ Login successful!" if lang == Language.EN else "✓ Accesso riuscito!"
            error_prefix = "Login failed" if lang == Language.EN else "Accesso fallito"

            has_error = False

            if not username or not password:
                st.error(error_msg)
                has_error = True

            if not has_error:
                try:
                    token = CollabookAPI.login(username, password)
                    st.session_state.token = token
                    st.success(success_msg)
                    st.rerun()
                except Exception as e:
                    st.error(f"{error_prefix}: {str(e)}")

def show_registration():
    """Account registration - character creation happens after login"""
    lang = Language(st.session_state.get("language", "en"))

    fill_all = "Please fill all fields" if lang == Language.EN else "Compila tutti i campi"
    password_match = "Passwords do not match" if lang == Language.EN else "Le password non corrispondono"
    password_len = "Password must be at least 6 characters" if lang == Language.EN else "Password troppo corta"
    username_len = "Username must be at least 3 characters" if lang == Language.EN else "Username troppo corto"
    error_prefix = "Registration failed" if lang == Language.EN else "Registrazione fallita"
    success_text = "✓ Welcome, your adventure begins!"
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
    
    # Prepare strings OUTSIDE the form
    username_label = f"⚔️ {t('username', lang)}"
    username_help = "This will be your character name too" if lang == Language.EN else "Questo sarà anche il nome del tuo personaggio"
    email_label = f"📧 {t('email', lang)}"
    password_label = f"🔑 {t('password', lang)}"
    confirm_label = "🔑 Confirm Password" if lang == Language.EN else "🔑 Conferma Password"
    submit_text = t('register', lang).upper() if lang == Language.EN else "REGISTRATI"
    button_label = f"⚔️ {submit_text}"

    with st.form("registration_form"):
        username = st.text_input(username_label, max_chars=50, help=username_help)
        email = st.text_input(email_label)
        password = st.text_input(password_label, type="password")
        password_confirm = st.text_input(confirm_label, type="password")
        
        submitted = st.form_submit_button(button_label)
        
        if submitted:
            # Validation messages
            fill_all = "Please fill in all required fields" if lang == Language.EN else "Compila tutti i campi obbligatori"
            password_match = "Passwords do not match" if lang == Language.EN else "Le password non corrispondono"
            password_len = "Password must be at least 6 characters" if lang == Language.EN else "La password deve essere di almeno 6 caratteri"
            username_len = "Username must be at least 3 characters" if lang == Language.EN else "Il nome utente deve essere di almeno 3 caratteri"
            
            has_error = False

            if not username or not email or not password:
                st.error(fill_all)
                has_error = True

            if password != password_confirm:
                st.error(password_match)
                has_error = True

            if len(password) < 6:
                st.error(password_len)
                has_error = True

            if len(username) < 3:
                st.error(username_len)
                has_error = True

            if not has_error:
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
    
    # Prepare strings OUTSIDE the form
    char_name_header = f"### 👤 {character.get('name', 'Character')}"
    profession_label = f"🛡️ {t('profession', lang)}"
    professions = {
        "en": ["Warrior", "Mage", "Rogue", "Cleric", "Ranger", "Paladin", "Bard", "Druid"],
        "it": ["Guerriero", "Mago", "Ladro", "Chierico", "Ranger", "Paladino", "Bardo", "Druido"]
    }
    backstory_label = "📜 Backstory" if lang == Language.EN else "📜 Storia"
    backstory_help = "Describe your character's background..." if lang == Language.EN else "Descrivi il background del tuo personaggio..."
    submit_text = "Begin Adventure" if lang == Language.EN else "Inizia Avventura"
    button_label = f"⚔️ {submit_text}"

    with st.form("character_creation_form"):
        st.markdown(char_name_header)
        
        # Profession dropdown
        profession = st.selectbox(profession_label, professions[lang.value])
        
        # Backstory
        backstory = st.text_area(backstory_label, max_chars=500, help=backstory_help)
        
        submitted = st.form_submit_button(button_label)
        
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
        # Prepare strings OUTSIDE
        email_label = f"📧 {t('email', lang)}" if lang == Language.EN else "📧 Email"
        button_text = "Send Reset Link" if lang == Language.EN else "Invia Link Reset"
        
        with st.form("request_reset_form"):
            email = st.text_input(email_label)
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
        # Prepare strings OUTSIDE
        token_label = "Reset Token" if lang == Language.EN else "Token Reset"
        token_help = "Check your email or console logs" if lang == Language.EN else "Controlla la tua email o i log della console"
        new_pass = "New Password" if lang == Language.EN else "Nuova Password"
        confirm_pass = "Confirm New Password" if lang == Language.EN else "Conferma Nuova Password"
        button_text = "Reset Password" if lang == Language.EN else "Reimposta Password"

        with st.form("reset_password_form"):
            token = st.text_input(token_label, help=token_help)
            new_password = st.text_input(new_pass, type="password")
            confirm_password = st.text_input(confirm_pass, type="password")
            
            submitted = st.form_submit_button(button_text)
            
            if submitted:
                password_match = "Passwords do not match" if lang == Language.EN else "Le password non corrispondono"
                password_len = "Password must be at least 6 characters" if lang == Language.EN else "La password deve essere di almeno 6 caratteri"
                success_reset = "✓ Password reset successful! You can now login." if lang == Language.EN else "✓ Password reimpostata con successo! Ora puoi accedere."
                error_prefix = "Error" if lang == Language.EN else "Errore"

                has_error = False

                if new_password != confirm_password:
                    st.error(password_match)
                    has_error = True

                if len(new_password) < 6:
                    st.error(password_len)
                    has_error = True

                if not has_error:
                    try:
                        CollabookAPI.reset_password(token, new_password)
                        st.success(success_reset)
                    except Exception as e:
                        st.error(f"{error_prefix}: {str(e)}")

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



if __name__ == "__main__":
    main()
