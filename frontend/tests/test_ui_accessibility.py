"""
Test Suite for UI Accessibility (TDD)
Verifies that UI components generate HTML compliant with WCAG 2.1 AA.
"""

import pytest
import re
from frontend import ui_components

def test_stat_card_accessibility():
    """Test Stat Card HTML structure and ARIA attributes"""
    # This function doesn't exist yet, but we're doing TDD
    html = ui_components.get_stat_card_html("Health", 50, "❤️", 100)
    
    # Check for semantic role
    assert 'role="progressbar"' in html or 'role="region"' in html
    
    # Check for accessible label
    assert 'aria-label="Health: 50 out of 100"' in html or 'aria-label="Health"' in html
    
    # Check for contrast-safe colors (checking for variable usage)
    assert 'var(--text-primary)' in html or 'color:' in html

def test_quest_card_accessibility():
    """Test Quest Card HTML structure"""
    html = ui_components.get_quest_card_html(
        "Save the Village", 
        "Defeat the goblins", 
        100, 
        50, 
        "main"
    )
    
    # Check for article role
    assert 'role="article"' in html
    
    # Check for heading hierarchy
    assert '<h3' in html
    
    # Check for aria-label on the card
    assert 'aria-label="Quest: Save the Village"' in html

def test_combat_log_accessibility():
    """Test Combat Log HTML structure"""
    logs = ["Player hits for 10 damage", "Enemy misses"]
    html = ui_components.get_combat_log_html(logs)
    
    # Check for log role or region
    assert 'role="log"' in html or 'role="region"' in html
    
    # Check for aria-live for dynamic updates
    assert 'aria-live="polite"' in html

def test_enemy_card_accessibility():
    """Test Enemy Card HTML structure"""
    html = ui_components.get_enemy_card_html("Goblin", 1, 10, 20, "common")
    
    # Check for article role
    assert 'role="article"' in html
    
    # Check for progress bar accessibility
    assert 'role="progressbar"' in html
    assert 'aria-valuenow="10"' in html
    assert 'aria-valuemax="20"' in html
    assert 'aria-label="Enemy Health"' in html

def test_color_contrast_variables():
    """
    Verify that CSS variables defined in style.css meet contrast ratio.
    This is a basic check to ensure variables are used.
    """
    # We can't parse CSS easily here without a parser, 
    # but we can check if the HTML components use the high-contrast variables
    html = ui_components.get_stat_card_html("Test", 10, "T", 20)
    
    # Should use our defined variables
    assert 'var(--' in html
