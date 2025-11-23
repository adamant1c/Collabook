"""
Character Portrait System

Automatically displays character images when mentioned in narration.

Naming Convention:
- npc_<CharacterName>.png/jpg/webp
- Examples:
  - npc_KingHarold.png
  - npc_ElvenQueen.jpg
  - npc_MerchantGiovanni.webp

Rules:
1. Filenames are case-insensitive for matching
2. Spaces in names replaced with underscores
3. Multiple formats supported: .png, .jpg, .jpeg, .webp
4. Images stored in: frontend/assets/characters/
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional

# Supported image formats
SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.webp']

# Assets directory
ASSETS_DIR = Path(__file__).parent / "assets" / "characters"

def ensure_assets_directory():
    """Create assets directory if it doesn't exist"""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

def normalize_character_name(name: str) -> str:
    """
    Normalize character name for filename matching
    
    Examples:
        "King Harold" -> "kingharold"
        "Merchant Giovanni" -> "merchantgiovanni"
        "Dark Mage" -> "darkmage"
    """
    # Remove special characters, convert to lowercase, remove spaces
    normalized = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
    return normalized

def get_available_characters() -> List[Dict[str, str]]:
    """
    Scan assets directory and return list of available characters
    
    Returns:
        List of dicts with 'name' and 'path' keys
        Example: [{'name': 'King Harold', 'path': 'npc_KingHarold.png'}, ...]
    """
    ensure_assets_directory()
    
    characters = []
    
    for file in ASSETS_DIR.iterdir():
        if file.suffix.lower() in SUPPORTED_FORMATS:
            # Extract character name from filename
            # npc_KingHarold.png -> King Harold
            if file.stem.startswith('npc_'):
                char_name = file.stem[4:]  # Remove 'npc_' prefix
                # Add spaces before capital letters
                char_name = re.sub(r'([A-Z])', r' \1', char_name).strip()
                
                characters.append({
                    'name': char_name,
                    'filename': file.name,
                    'path': str(file.relative_to(Path(__file__).parent))
                })
    
    return characters

def find_character_image(character_name: str) -> Optional[str]:
    """
    Find character image by name (case-insensitive, flexible matching)
    
    Args:
        character_name: Name mentioned in text (e.g., "King Harold", "king harold")
        
    Returns:
        Relative path to image file or None if not found
    """
    ensure_assets_directory()
    
    normalized_search = normalize_character_name(character_name)
    
    # Search for matching file
    for file in ASSETS_DIR.iterdir():
        if file.suffix.lower() in SUPPORTED_FORMATS:
            # Normalize filename (without extension and npc_ prefix)
            if file.stem.startswith('npc_'):
                normalized_file = normalize_character_name(file.stem[4:])
                
                if normalized_file == normalized_search:
                    return f"assets/characters/{file.name}"
    
    return None

def extract_character_mentions(text: str, available_chars: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Extract character mentions from narration text
    
    Args:
        text: Narration text
        available_chars: List of available characters from get_available_characters()
        
    Returns:
        List of mentioned characters with their image paths
        Example: [{'name': 'King Harold', 'path': 'assets/characters/npc_KingHarold.png'}, ...]
    """
    mentioned = []
    
    for char in available_chars:
        # Case-insensitive search for character name in text
        pattern = re.compile(re.escape(char['name']), re.IGNORECASE)
        
        if pattern.search(text):
            mentioned.append({
                'name': char['name'],
                'path': char['path']
            })
    
    return mentioned

def create_character_prompt_hint(available_chars: List[Dict[str, str]]) -> str:
    """
    Create LLM prompt hint about available characters
    
    This helps the LLM know which NPCs have visual representations
    and encourages their use in narration.
    
    Args:
        available_chars: List from get_available_characters()
        
    Returns:
        String to append to LLM context
    """
    if not available_chars:
        return ""
    
    char_names = [c['name'] for c in available_chars]
    
    hint = f"\nAvailable NPCs (with portraits): {', '.join(char_names[:5])}"
    if len(char_names) > 5:
        hint += f" and {len(char_names) - 5} more"
    
    return hint

# Example usage and documentation
if __name__ == "__main__":
    print("Character Portrait System - Testing")
    print("=" * 50)
    
    # Ensure directory exists
    ensure_assets_directory()
    print(f"✅ Assets directory: {ASSETS_DIR}")
    
    # List available characters
    chars = get_available_characters()
    print(f"\n📸 Available Characters: {len(chars)}")
    for char in chars:
        print(f"  - {char['name']} ({char['filename']})")
    
    # Test character detection
    test_text = "King Harold greets you warmly. The Merchant Giovanni offers his wares."
    mentioned = extract_character_mentions(test_text, chars)
    print(f"\n🔍 Characters mentioned in test text:")
    for char in mentioned:
        print(f"  - {char['name']} -> {char['path']}")
    
    # Test name normalization
    test_names = ["King Harold", "king harold", "KING HAROLD", "King  Harold"]
    print(f"\n🔤 Name normalization test:")
    for name in test_names:
        normalized = normalize_character_name(name)
        found = find_character_image(name)
        print(f"  '{name}' -> '{normalized}' -> {found or 'NOT FOUND'}")
