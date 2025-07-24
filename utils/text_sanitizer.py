"""Text sanitization utilities to prevent weird characters in output."""

import re
from typing import Dict


# Character replacement map for common problematic Unicode characters
CHAR_REPLACEMENTS: Dict[str, str] = {
    '\u0014': '—',  # Device Control Four → em dash
    '\u2013': '–',  # en dash
    '\u2014': '—',  # em dash
    '\u2018': "'",  # left single quote
    '\u2019': "'",  # right single quote
    '\u201c': '"',  # left double quote
    '\u201d': '"',  # right double quote
    '\u2026': '...',  # horizontal ellipsis
    '\u00a0': ' ',  # non-breaking space
    '\u200b': '',  # zero-width space
    '\u200c': '',  # zero-width non-joiner
    '\u200d': '',  # zero-width joiner
    '\u2022': '•',  # bullet
    '\u00b7': '·',  # middle dot
    '\ufeff': '',  # zero-width no-break space (BOM)
}


def sanitize_text(text: str) -> str:
    """
    Sanitize text by replacing problematic Unicode characters.
    
    Args:
        text: The text to sanitize
        
    Returns:
        Sanitized text with problematic characters replaced
    """
    if not text:
        return text
    
    # First, handle any invalid UTF-8 sequences by replacing them
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='replace')
    
    # Replace each problematic character
    for old_char, new_char in CHAR_REPLACEMENTS.items():
        text = text.replace(old_char, new_char)
    
    # Remove any other control characters (U+0000 to U+001F) except newline and tab
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    # Remove replacement character (U+FFFD) which appears for invalid UTF-8
    text = text.replace('\ufffd', '?')
    
    # Remove any sequences of invalid bytes that might have been converted to characters
    text = re.sub(r'[\x80-\x8F]+', '????', text)
    
    # Normalize multiple spaces (but preserve single tabs and newlines)
    text = re.sub(r'  +', ' ', text)  # Multiple spaces to single space
    text = re.sub(r' +\n', '\n', text)   # Remove trailing spaces
    text = re.sub(r'\n +', '\n', text)   # Remove leading spaces after newline
    
    return text


def detect_problematic_chars(text: str) -> Dict[str, int]:
    """
    Detect problematic characters in text for debugging.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary mapping problematic characters to their count
    """
    found_chars = {}
    
    # Check for known problematic characters
    for char in CHAR_REPLACEMENTS:
        count = text.count(char)
        if count > 0:
            found_chars[f"U+{ord(char):04X} ({repr(char)})"] = count
    
    # Check for other control characters
    for char in text:
        if ord(char) < 32 and char not in ['\n', '\t', '\r']:
            char_repr = f"U+{ord(char):04X}"
            if char_repr not in found_chars:
                found_chars[char_repr] = text.count(char)
    
    return found_chars