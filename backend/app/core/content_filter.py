"""
Content Moderation System

Filters inappropriate content from user inputs and LLM outputs.
Ensures safe, age-appropriate gameplay experience.
"""

import re
import os
from typing import Dict, List, Tuple
from enum import Enum

class FilterLevel(str, Enum):
    STRICT = "strict"
    MODERATE = "moderate"
    RELAXED = "relaxed"

class ViolationType(str, Enum):
    PROFANITY = "profanity"
    VIOLENCE = "violence"
    SEXUAL = "sexual"
    HATE_SPEECH = "hate_speech"
    SPAM = "spam"

# Profanity blacklist (basic - can be extended)
PROFANITY_BLACKLIST = {
    # Common profanity
    "fuck", "shit", "damn", "hell", "ass", "bitch", "bastard",
    "crap", "piss", "dick", "cock", "pussy", "cunt",
    
    # Variations and l33t speak
    "f**k", "sh*t", "fuk", "shyt", "a$$", "b!tch",
    "fck", "sht", "dmn",
}

# Violence/gore keywords
VIOLENCE_KEYWORDS = {
    "gore", "dismember", "disembowel", "eviscerate", "mutilate",
    "torture", "massacre", "slaughter", "butcher", "carnage",
    "blood bath", "bloodbath", "decapitate", "behead",
}

# Sexual content keywords
SEXUAL_KEYWORDS = {
    "sex", "sexual", "porn", "pornography", "nude", "naked",
    "rape", "molest", "seduce", "erotic", "fetish",
}

# Hate speech patterns
HATE_SPEECH_PATTERNS = {
    # Racial slurs
    "nigger", "nigga", "chink", "spic", "kike", "wetback",
    
    # Derogatory terms
    "faggot", "tranny", "retard", "retarded",
}

def get_filter_level() -> FilterLevel:
    """Get content filter level from environment"""
    level = os.getenv("CONTENT_FILTER_LEVEL", "moderate").lower()
    try:
        return FilterLevel(level)
    except ValueError:
        return FilterLevel.MODERATE

def normalize_text(text: str) -> str:
    """Normalize text for consistent filtering"""
    # Remove special characters, lowercase, collapse whitespace
    normalized = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def check_profanity(text: str, level: FilterLevel = None) -> Tuple[bool, List[str]]:
    """
    Check text for profanity
    
    Returns:
        (has_profanity, list_of_violations)
    """
    if level is None:
        level = get_filter_level()
    
    normalized = normalize_text(text)
    violations = []
    
    if level == FilterLevel.RELAXED:
        # Only block severe profanity
        severe_words = {"fuck", "cunt", "shit"}
        blacklist = {w for w in PROFANITY_BLACKLIST if w in severe_words}
    else:
        blacklist = PROFANITY_BLACKLIST
    
    # Check for blacklisted words
    words = normalized.split()
    for word in words:
        if word in blacklist:
            violations.append(word)
    
    # Check for variations (partial matches)
    for bad_word in blacklist:
        if bad_word in normalized and len(bad_word) > 3:
            violations.append(bad_word)
    
    return len(violations) > 0, violations

def check_violence(text: str, level: FilterLevel = None) -> Tuple[bool, List[str]]:
    """Check for excessive violence/gore"""
    if level is None:
        level = get_filter_level()
    
    if level == FilterLevel.RELAXED:
        return False, []  # Allow in relaxed mode (it's an RPG after all)
    
    normalized = normalize_text(text)
    violations = []
    
    # Check for gore keywords
    for keyword in VIOLENCE_KEYWORDS:
        if keyword in normalized:
            violations.append(keyword)
    
    # Moderate: Allow some violence, block extreme
    if level == FilterLevel.MODERATE:
        allowed = {"blood", "fight", "battle", "attack", "kill"}
        violations = [v for v in violations if v not in allowed]
    
    return len(violations) > 0, violations

def check_sexual_content(text: str) -> Tuple[bool, List[str]]:
    """Check for sexual content"""
    normalized = normalize_text(text)
    violations = []
    
    for keyword in SEXUAL_KEYWORDS:
        if keyword in normalized:
            violations.append(keyword)
    
    return len(violations) > 0, violations

def check_hate_speech(text: str) -> Tuple[bool, List[str]]:
    """Check for hate speech"""
    normalized = normalize_text(text)
    violations = []
    
    for pattern in HATE_SPEECH_PATTERNS:
        if pattern in normalized:
            violations.append(pattern)
    
    return len(violations) > 0, violations

def validate_user_input(text: str, level: FilterLevel = None) -> Dict:
    """
    Validate user input for inappropriate content
    
    Returns:
        {
            "is_valid": bool,
            "violations": {type: [words]},
            "message": str
        }
    """
    if level is None:
        level = get_filter_level()
    
    violations = {}
    
    # Check profanity
    has_profanity, profanity_words = check_profanity(text, level)
    if has_profanity:
        violations[ViolationType.PROFANITY] = profanity_words
    
    # Check violence
    has_violence, violence_words = check_violence(text, level)
    if has_violence:
        violations[ViolationType.VIOLENCE] = violence_words
    
    # Check sexual content
    has_sexual, sexual_words = check_sexual_content(text)
    if has_sexual:
        violations[ViolationType.SEXUAL] = sexual_words
    
    # Check hate speech
    has_hate, hate_words = check_hate_speech(text)
    if has_hate:
        violations[ViolationType.HATE_SPEECH] = hate_words
    
    # Build result
    is_valid = len(violations) == 0
    
    if not is_valid:
        message = "Your input contains inappropriate content: "
        types = ", ".join([v.value for v in violations.keys()])
        message += types + ". Please rephrase your action."
    else:
        message = "Content validated"
    
    return {
        "is_valid": is_valid,
        "violations": violations,
        "message": message
    }

def sanitize_llm_output(text: str, level: FilterLevel = None) -> Tuple[str, bool]:
    """
    Sanitize LLM output, removing inappropriate content
    
    Returns:
        (sanitized_text, was_modified)
    """
    if level is None:
        level = get_filter_level()
    
    original = text
    sanitized = text
    
    # Check for violations
    has_profanity, profanity_words = check_profanity(text, level)
    has_sexual, sexual_words = check_sexual_content(text)
    has_hate, hate_words = check_hate_speech(text)
    
    # Replace violations with [FILTERED]
    all_violations = set(profanity_words + sexual_words + hate_words)
    
    for word in all_violations:
        # Case-insensitive replacement
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        sanitized = pattern.sub("[FILTERED]", sanitized)
    
    was_modified = sanitized != original
    
    return sanitized, was_modified

def log_violation(user_id: str, violation_type: ViolationType, content: str):
    """Log content violations for review"""
    # In production: log to file or monitoring system
    print(f"⚠️ Violation: {violation_type.value} by user {user_id}")
    print(f"   Content: {content[:100]}...")

# Configuration check
def validate_content_filter_config():
    """Validate content filter configuration on startup"""
    level = get_filter_level()
    print(f"✅ Content Filter initialized: {level.value} mode")
    print(f"   Profanity blacklist: {len(PROFANITY_BLACKLIST)} words")
    print(f"   Violence keywords: {len(VIOLENCE_KEYWORDS)} patterns")
    print(f"   Age-appropriate: {'Yes' if level != FilterLevel.RELAXED else 'Permissive'}")
