"""
UI component for displaying character portraits

Renders character images when detected in narration text.
"""

import streamlit as st
from character_portraits import get_available_characters, extract_character_mentions
from pathlib import Path

def render_character_portraits(narration_text: str):
    """
    Detect and display character portraits mentioned in narration
    
    Args:
        narration_text: The narration text to scan
    """
    # Get available characters
    available_chars = get_available_characters()
    
    if not available_chars:
        return  # No characters available, skip
    
    # Extract mentions
    mentioned = extract_character_mentions(narration_text, available_chars)
    
    if not mentioned:
        return  # No characters mentioned
    
    # Display portraits
    st.markdown("""
        <div style='margin: 1rem 0; padding: 1rem; 
                    background: linear-gradient(145deg, #f4e8d0, #e8d5b7);
                    border: 2px solid #d4af37; border-radius: 10px;'>
            <h4 style='margin: 0 0 1rem 0; color: #2a1810; font-family: "Cinzel", serif;'>
                👥 Characters in this Scene
            </h4>
        </div>
    """, unsafe_allow_html=True)
    
    # Display portraits in columns (max 4 per row)
    cols_per_row = min(len(mentioned), 4)
    cols = st.columns(cols_per_row)
    
    for idx, char in enumerate(mentioned):
        col_idx = idx % cols_per_row
        
        with cols[col_idx]:
            # Character card
            st.markdown(f"""
                <div style='text-align: center; padding: 0.5rem; 
                            background: white; border: 2px solid #d4af37; 
                            border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
            """, unsafe_allow_html=True)
            
            # Display image
            try:
                image_path = Path(__file__).parent / char['path']
                if image_path.exists():
                    st.image(str(image_path), use_container_width=True)
                else:
                    # Placeholder if image not found
                    st.markdown(f"""
                        <div style='background: #5d4e37; color: white; 
                                    padding: 2rem; border-radius: 8px;'>
                            <div style='font-size: 3rem;'>👤</div>
                        </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading image: {e}")
            
            # Character name
            st.markdown(f"""
                <div style='margin-top: 0.5rem; font-weight: bold; 
                            font-family: "Cinzel", serif; color: #2a1810;'>
                    {char['name']}
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

def render_character_gallery():
    """
    Show all available characters in a gallery (for admin/debug)
    """
    available_chars = get_available_characters()
    
    if not available_chars:
        st.info("📸 No character portraits available yet.")
        st.markdown("""
            **How to add characters:**
            1. Create images (PNG, JPG, or WEBP)
            2. Name them: `npc_CharacterName.png`
            3. Place in `frontend/assets/characters/`
            
            **Examples:**
            - `npc_KingHarold.png`
            - `npc_ElvenQueen.jpg`
            - `npc_MerchantGiovanni.webp`
        """)
        return
    
    st.subheader(f"📸 Character Gallery ({len(available_chars)} available)")
    
    # Display in grid
    cols = st.columns(4)
    
    for idx, char in enumerate(available_chars):
        col_idx = idx % 4
        
        with cols[col_idx]:
            with st.expander(f"👤 {char['name']}"):
                try:
                    image_path = Path(__file__).parent / char['path']
                    if image_path.exists():
                        st.image(str(image_path))
                        st.caption(f"File: `{char['filename']}`")
                    else:
                        st.error("Image file not found")
                except Exception as e:
                    st.error(f"Error: {e}")

def show_portrait_upload_ui():
    """
    Admin UI for uploading character portraits
    """
    st.subheader("📤 Upload Character Portrait")
    
    st.markdown("""
        **Naming Convention**: `npc_<CharacterName>.<ext>`
        
        Examples:
        - `npc_KingHarold.png` → "King Harold"
        - `npc_DarkMage.jpg` → "Dark Mage"
        - `npc_Goblin.webp` → "Goblin"
        
        **Supported Formats**: PNG, JPG, WEBP
    """)
    
    character_name = st.text_input(
        "Character Name",
        placeholder="e.g., King Harold, Dark Mage, Goblin Scout",
        help="Name will be automatically formatted (spaces become capitals)"
    )
    
    uploaded_file = st.file_uploader(
        "Choose image file",
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="Recommended: 512x512px or 1:1 aspect ratio"
    )
    
    if st.button("💾 Save Portrait") and character_name and uploaded_file:
        # Format filename
        # "King Harold" -> "npc_KingHarold.png"
        formatted_name = character_name.replace(" ", "")
        filename = f"npc_{formatted_name}{Path(uploaded_file.name).suffix}"
        
        # Save file
        assets_dir = Path(__file__).parent / "assets" / "characters"
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = assets_dir / filename
        
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ Portrait saved: `{filename}`")
        st.info(f"💡 LLM can now reference: **{character_name}**")
        st.balloons()
