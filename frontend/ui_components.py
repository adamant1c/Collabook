"""
Enhanced UI components for Collabook RPG
Tabletop game-themed interface elements with Accessibility Support (WCAG 2.1 AA)
"""

import streamlit as st

def apply_custom_css():
    """Load custom CSS for RPG theme"""
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def render_title(text, icon="🎲"):
    """Render ornate title with icon"""
    st.markdown(f"""
        <h1 style="text-align: center; margin-bottom: 2rem;" aria-label="{text}">
            <span aria-hidden="true">{icon}</span> {text} <span aria-hidden="true">{icon}</span>
        </h1>
    """, unsafe_allow_html=True)

def get_stat_card_html(label, value, icon="📊", max_value=None):
    """Generate HTML for stat card with accessibility attributes"""
    if max_value:
        percentage = (value / max_value) * 100
        return f"""
            <div class="stat-card" role="region" aria-label="{label}: {value} out of {max_value}">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <strong><span aria-hidden="true">{icon}</span> {label}</strong>
                    <span style="color: var(--gold-primary);">{value}/{max_value}</span>
                </div>
                <div class="progress-container" 
                     role="progressbar" 
                     aria-valuenow="{value}" 
                     aria-valuemin="0" 
                     aria-valuemax="{max_value}" 
                     aria-label="{label} Progress"
                     style="background: rgba(255,255,255,0.1); border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, var(--gold-primary), var(--gold-hover)); 
                                width: {percentage}%; height: 100%; border-radius: 4px; 
                                box-shadow: 0 0 10px rgba(212,175,55,0.3);"></div>
                </div>
            </div>
        """
    else:
        return f"""
            <div class="stat-card" role="region" aria-label="{label}: {value}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong><span aria-hidden="true">{icon}</span> {label}</strong>
                    <span style="font-size: 1.5rem; color: var(--gold-primary); font-family: 'Cinzel', serif;">{value}</span>
                </div>
            </div>
        """

def render_stat_card(label, value, icon="📊", max_value=None):
    """Render a stat in RPG character sheet style"""
    html = get_stat_card_html(label, value, icon, max_value)
    st.markdown(html, unsafe_allow_html=True)

def get_quest_card_html(title, description, reward_xp, reward_gold, quest_type="side"):
    """Generate HTML for quest card with accessibility attributes"""
    type_icon = "⭐" if quest_type == "main" else "📌"
    type_color = "var(--gold-primary)" if quest_type == "main" else "var(--text-secondary)"
    
    return f"""
        <article class="quest-card" role="article" aria-label="Quest: {title}">
            <header>
                <h3 style="color: {type_color} !important; font-size: 1.4rem; margin-top: 0;">
                    <span aria-hidden="true">{type_icon}</span> {title}
                </h3>
            </header>
            <p style="font-family: 'Inter', sans-serif; line-height: 1.6; color: var(--text-primary); opacity: 0.9;">
                {description}
            </p>
            <footer style="display: flex; gap: 1.5rem; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);" aria-label="Quest Rewards">
                <div style="color: var(--gold-primary); font-weight: bold;" aria-label="{reward_xp} XP Reward">
                    <span aria-hidden="true">🌟</span> {reward_xp} XP
                </div>
                <div style="color: var(--gold-primary); font-weight: bold;" aria-label="{reward_gold} Gold Reward">
                    <span aria-hidden="true">💰</span> {reward_gold} Gold
                </div>
                <div style="color: var(--text-muted); text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; margin-left: auto;">
                    {quest_type}
                </div>
            </footer>
        </article>
    """

def render_quest_card(title, description, reward_xp, reward_gold, quest_type="side"):
    """Render quest in ornate card style"""
    html = get_quest_card_html(title, description, reward_xp, reward_gold, quest_type)
    st.markdown(html, unsafe_allow_html=True)

def get_combat_log_html(logs):
    """Generate HTML for combat log with accessibility attributes"""
    log_html = "<div class=\"combat-log\" role=\"log\" aria-live=\"polite\" aria-label=\"Combat Log\" style=\"background: rgba(0,0,0,0.3); border-radius: 8px; padding: 1rem; max-height: 300px; overflow-y: auto; font-family: 'Inter', sans-serif;\">"
    
    for log in logs:
        # Add icons based on content
        if "CRITICAL" in log:
            icon = "💥"
            style = "color: var(--danger); font-weight: bold;"
        elif "Victory" in log or "defeated" in log:
            icon = "🎉"
            style = "color: var(--success); font-weight: bold;"
        elif "Miss" in log or "misses" in log:
            icon = "💨"
            style = "color: var(--text-muted); font-style: italic;"
        elif "damage" in log:
            icon = "⚔️"
            style = "color: var(--text-primary);"
        else:
            icon = "•"
            style = "color: var(--text-secondary);"
        
        log_html += f"<div style=\"margin: 0.5rem 0; {style}\"><span aria-hidden=\"true\">{icon}</span> {log}</div>"
    
    log_html += "</div>"
    return log_html

def render_combat_log(logs):
    """Render combat log in ancient scroll style"""
    html = get_combat_log_html(logs)
    st.markdown(html, unsafe_allow_html=True)

def get_enemy_card_html(name, level, hp, max_hp, enemy_type="common"):
    """Generate HTML for enemy card with accessibility attributes"""
    type_colors = {
        "common": "var(--text-secondary)",
        "elite": "var(--magic)",
        "boss": "var(--danger)"
    }
    
    color = type_colors.get(enemy_type, "var(--text-secondary)")
    hp_percent = (hp / max_hp) * 100
    
    return f"""
        <article class="enemy-card" role="article" aria-label="Enemy: {name}">
            <div style="background: linear-gradient(145deg, rgba(20,20,20,0.8), rgba(10,10,10,0.9)); 
                        border: 1px solid {color}; 
                        border-radius: 12px; 
                        padding: 1.5rem; 
                        margin: 1rem 0;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
                <header style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="color: {color} !important; margin: 0;">{name}</h3>
                    <span style="background: {color}; color: black; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;" aria-label="Level {level}">LVL {level}</span>
                </header>
                
                <div style="margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem; margin-bottom: 0.3rem;">
                        <span>HP</span>
                        <span aria-label="{hp} out of {max_hp}">{hp}/{max_hp}</span>
                    </div>
                    <div role="progressbar" 
                         aria-valuenow="{hp}" 
                         aria-valuemin="0" 
                         aria-valuemax="{max_hp}" 
                         aria-label="Enemy Health"
                         style="background: rgba(255,255,255,0.1); border-radius: 4px; height: 12px; position: relative; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, var(--danger), #ff5252); width: {hp_percent}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
                <footer style="margin-top: 1rem; text-align: center; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 2px; color: {color}; opacity: 0.8;">
                    {enemy_type} Enemy
                </footer>
            </div>
        </article>
    """

def render_enemy_card(name, level, hp, max_hp, enemy_type="common"):
    """Render enemy info card"""
    html = get_enemy_card_html(name, level, hp, max_hp, enemy_type)
    st.markdown(html, unsafe_allow_html=True)

def render_level_up_animation():
    """Show level up celebration"""
    st.balloons()
    st.markdown("""
        <div role="alert" aria-live="assertive"
             style="background: rgba(212, 175, 55, 0.1); 
                    backdrop-filter: blur(10px);
                    border: 1px solid var(--gold-primary); 
                    border-radius: 16px; 
                    padding: 3rem; 
                    text-align: center;
                    animation: glow 2s ease-in-out infinite;
                    margin: 2rem 0;">
            <h1 style="color: var(--gold-primary); margin: 0; font-size: 4rem; text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);">
                LEVEL UP!
            </h1>
            <p style="color: var(--text-primary); font-size: 1.5rem; margin-top: 1rem; font-family: 'Cinzel', serif;">
                Your legend grows...
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_dice_roll(result, sides=20):
    """Animated dice roll result"""
    color = "var(--gold-primary)"
    if result == 20: color = "var(--danger)" # Critical Hit
    if result == 1: color = "var(--text-muted)" # Critical Miss
    
    label = "CRITICAL HIT!" if result == 20 else "CRITICAL MISS!" if result == 1 else f"Rolled {result}"
    
    st.markdown(f"""
        <div role="status" aria-live="polite" aria-label="Dice Roll Result: {result}, {label}" style="text-align: center; margin: 2rem 0;">
            <div style="display: inline-flex; justify-content: center; align-items: center;
                        width: 100px; height: 100px;
                        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)); 
                        color: {color}; 
                        font-size: 3rem; 
                        font-weight: bold; 
                        border-radius: 20px; 
                        border: 2px solid {color};
                        box-shadow: 0 0 30px {color}40;
                        animation: shake 0.5s ease-in-out;">
                <span aria-hidden="true">{result}</span>
            </div>
            <div style="margin-top: 1rem; font-size: 1.5rem; font-weight: bold; color: {color}; font-family: 'Cinzel', serif;">
                {label}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_hp_bar(current_hp, max_hp, label="HP"):
    """Render HP bar with modern styling"""
    percentage = max(0, min(100, (current_hp / max_hp) * 100))
    
    # Color based on percentage
    if percentage > 66:
        color = "var(--success)"
    elif percentage > 33:
        color = "var(--gold-primary)"
    else:
        color = "var(--danger)"
    
    st.markdown(f"""
        <div class="stat-card" role="region" aria-label="{label}: {current_hp} out of {max_hp}">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <strong><span aria-hidden="true">❤️</span> {label}</strong>
                <span style="color: {color}; font-weight: bold;">{current_hp}/{max_hp}</span>
            </div>
            <div role="progressbar" 
                 aria-valuenow="{current_hp}" 
                 aria-valuemin="0" 
                 aria-valuemax="{max_hp}" 
                 aria-label="{label} Progress"
                 style="background: rgba(255,255,255,0.1); 
                        border-radius: 8px; 
                        height: 16px; 
                        position: relative;
                        overflow: hidden;">
                <div style="background: linear-gradient(90deg, {color}, {color}aa); 
                            width: {percentage}%; 
                            height: 100%; 
                            border-radius: 8px; 
                            box-shadow: 0 0 15px {color}66;
                            transition: width 0.5s ease;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# New function to render random dice roll stats
def render_random_stats(stats: dict):
    """Render a card showing randomly generated character stats.
    Expected keys: hp, max_hp, magic, strength, dexterity, defense, etc.
    """
    # Build HTML rows for each stat
    rows = []
    for key, value in stats.items():
        # Capitalize and replace underscores with spaces for display
        label = key.replace('_', ' ').title()
        rows.append(f"<div style='display:flex;justify-content:space-between;'><span>{label}</span><span>{value}</span></div>")
    rows_html = "\n".join(rows)
    st.markdown(f"""
        <div class='stat-card' role='region' aria-label='Random Dice Roll Stats'>
            <strong>🎲 Random Stats</strong>
            <div style='margin-top:0.5rem;'>
                {rows_html}
            </div>
        </div>
    """, unsafe_allow_html=True)
