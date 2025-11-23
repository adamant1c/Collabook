"""
Enhanced UI components for Collabook RPG
Tabletop game-themed interface elements
"""

import streamlit as st

def apply_custom_css():
    """Load custom CSS for RPG theme"""
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def render_title(text, icon="🎲"):
    """Render ornate title with icon"""
    st.markdown(f"""
        <h1 style='text-align: center; margin-bottom: 2rem;'>
            {icon} {text} {icon}
        </h1>
    """, unsafe_allow_html=True)

def render_stat_card(label, value, icon="📊", max_value=None):
    """Render a stat in RPG character sheet style"""
    if max_value:
        percentage = (value / max_value) * 100
        st.markdown(f"""
            <div class='stat-card'>
                <strong>{icon} {label}</strong><br/>
                <div style='display: flex; align-items: center; margin-top: 0.5rem;'>
                    <div style='flex: 1; background: rgba(139,69,19,0.2); border-radius: 5px; height: 24px; position: relative;'>
                        <div style='background: linear-gradient(90deg, #d4af37, #ffd700); width: {percentage}%; height: 100%; border-radius: 5px; box-shadow: 0 0 10px rgba(212,175,55,0.5);'></div>
                        <span style='position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); font-weight: bold; color: #2a1810; text-shadow: 1px 1px 2px white;'>{value}/{max_value}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='stat-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <strong>{icon} {label}</strong>
                    <span style='font-size: 1.5rem; color: #d4af37; font-weight: bold;'>{value}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

def render_quest_card(title, description, reward_xp, reward_gold, quest_type="side"):
    """Render quest in ornate card style"""
    type_icon = "⭐" if quest_type == "main" else "📌"
    type_color = "#8b0000" if quest_type == "main" else "#2d5016"
    
    st.markdown(f"""
        <div class='quest-card'>
            <h3 style='color: {type_color} !important;'>{type_icon} {title}</h3>
            <p style='font-family: "Spectral", serif; line-height: 1.6; color: #3e2723;'>{description}</p>
            <div style='display: flex; gap: 1rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #d4af37;'>
                <div><strong>🌟 XP:</strong> {reward_xp}</div>
                <div><strong>💰 Gold:</strong> {reward_gold}</div>
                <div><strong>📋 Type:</strong> {quest_type.upper()}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_combat_log(logs):
    """Render combat log in ancient scroll style"""
    log_html = "<div class='combat-log'>"
    for log in logs:
        # Add icons based on content
        if "CRITICAL" in log:
            icon = "💥"
        elif "Victory" in log or "defeated" in log:
            icon = "🎉"
        elif "Miss" in log or "misses" in log:
            icon = "💨"
        elif "damage" in log:
            icon = "⚔️"
        else:
            icon = "•"
        
        log_html += f"<div style='margin: 0.5rem 0;'>{icon} {log}</div>"
    
    log_html += "</div>"
    st.markdown(log_html, unsafe_allow_html=True)

def render_enemy_card(name, level, hp, max_hp, enemy_type="common"):
    """Render enemy info card"""
    type_colors = {
        "common": "#5d4e37",
        "elite": "#6a0dad",
        "boss": "#8b0000"
    }
    type_icons = {
        "common": "👤",
        "elite": "👹",
        "boss": "🐉"
    }
    
    color = type_colors.get(enemy_type, "#5d4e37")
    icon = type_icons.get(enemy_type, "👤")
    hp_percent = (hp / max_hp) * 100
    
    st.markdown(f"""
        <div style='background: linear-gradient(145deg, #f4e8d0, #e8d5b7); 
                    border: 3px solid {color}; 
                    border-radius: 12px; 
                    padding: 1.5rem; 
                    margin: 1rem 0;
                    box-shadow: 0 6px 12px rgba(0,0,0,0.3), inset 0 0 15px {color}33;'>
            <h3 style='color: {color} !important; margin: 0;'>{icon} {name} (Level {level})</h3>
            <div style='margin-top: 1rem;'>
                <strong>HP:</strong>
                <div style='background: rgba(139,0,0,0.2); border-radius: 5px; height: 24px; margin-top: 0.5rem; position: relative;'>
                    <div style='background: linear-gradient(90deg, #8b0000, #a00000); width: {hp_percent}%; height: 100%; border-radius: 5px; box-shadow: 0 0 10px rgba(139,0,0,0.5);'></div>
                    <span style='position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); font-weight: bold; color: white; text-shadow: 1px 1px 2px black;'>{hp}/{max_hp}</span>
                </div>
            </div>
            <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid {color}; text-align: center; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;'>
                {enemy_type} Enemy
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_level_up_animation():
    """Show level up celebration"""
    st.balloons()
    st.markdown("""
        <div style='background: linear-gradient(145deg, #ffd700, #d4af37); 
                    border: 4px solid #8b4513; 
                    border-radius: 15px; 
                    padding: 2rem; 
                    text-align: center;
                    animation: glow 2s ease-in-out infinite;
                    box-shadow: 0 8px 16px rgba(0,0,0,0.4), 0 0 30px rgba(255,215,0,0.6);'>
            <h1 style='color: #8b0000; margin: 0; font-size: 3rem; text-shadow: 2px 2px 4px black;'>
                🎉 LEVEL UP! 🎉
            </h1>
            <p style='color: #2a1810; font-size: 1.5rem; margin-top: 1rem;'>
                Your character grows stronger!
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_dice_roll(result, sides=20):
    """Animated dice roll result"""
    color = "#8b0000" if result == 20 else "#2d5016" if result == 1 else "#d4af37"
    label = "CRITICAL HIT!" if result == 20 else "CRITICAL MISS!" if result == 1 else f"Rolled {result}"
    
    st.markdown(f"""
        <div style='text-align: center; margin: 1rem 0;'>
            <div style='display: inline-block; 
                        background: {color}; 
                        color: white; 
                        font-size: 3rem; 
                        font-weight: bold; 
                        padding: 1.5rem 2rem; 
                        border-radius: 15px; 
                        border: 3px solid #8b4513;
                        box-shadow: 0 8px 16px rgba(0,0,0,0.4), 0 0 20px {color}99;
                        animation: shake 0.5s ease-in-out;'>
                🎲 {result}
            </div>
            <div style='margin-top: 1rem; font-size: 1.5rem; font-weight: bold; color: {color};'>
                {label}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_hp_bar(current_hp, max_hp, label="HP"):
    """Render HP bar with medieval styling"""
    percentage = max(0, min(100, (current_hp / max_hp) * 100))
    
    # Color based on percentage
    if percentage > 66:
        color = "#2d5016"  # Green - healthy
    elif percentage > 33:
        color = "#d4af37"  # Gold - wounded
    else:
        color = "#8b0000"  # Red - critical
    
    st.markdown(f"""
        <div class='stat-card'>
            <strong>❤️ {label}</strong>
            <div style='background: rgba(139,0,0,0.2); 
                        border: 2px solid #5d4e37; 
                        border-radius: 8px; 
                        height: 32px; 
                        margin-top: 0.5rem; 
                        position: relative;
                        overflow: hidden;'>
                <div style='background: linear-gradient(90deg, {color}, {color}dd); 
                            width: {percentage}%; 
                            height: 100%; 
                            border-radius: 6px; 
                            box-shadow: 0 0 15px {color}99;
                            transition: width 0.5s ease;'></div>
                <span style='position: absolute; 
                             left: 50%; 
                             top: 50%; 
                             transform: translate(-50%, -50%); 
                             font-weight: bold; 
                             font-size: 1.2rem;
                             color: white; 
                             text-shadow: 2px 2px 4px black;'>
                    {current_hp} / {max_hp}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)
