#!/usr/bin/env python3
"""Test text sanitization to ensure weird characters are handled properly."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from utils.text_sanitizer import sanitize_text, detect_problematic_chars


def test_sanitization():
    """Test various problematic characters."""
    
    test_cases = [
        # Test case with the specific issue we encountered
        ("A door materialized\u0014white frame", "A door materialized—white frame"),
        
        # Test various dash types
        ("En dash\u2013test", "En dash–test"),
        ("Em dash\u2014test", "Em dash—test"),
        
        # Test quotes
        ("He said \u201chello\u201d", 'He said "hello"'),
        ("It\u2019s working", "It's working"),
        ("\u2018Single quotes\u2019", "'Single quotes'"),
        
        # Test spaces and control characters
        ("Non\u00a0breaking\u00a0space", "Non breaking space"),
        ("Zero\u200bwidth\u200bspace", "Zerowidthspace"),
        
        # Test other control characters
        ("Control\x01characters\x02removed", "Controlcharactersremoved"),
        ("But\nnewlines\tand\ttabs\nare\tpreserved", "But\nnewlines\tand\ttabs\nare\tpreserved"),
        
        # Test ellipsis
        ("Wait\u2026", "Wait..."),
        
        # Test multiple issues
        ("Complex\u0014text with \u201cquotes\u201d and\u00a0spaces\u2026", 
         'Complex—text with "quotes" and spaces...'),
    ]
    
    print("Testing text sanitization...\n")
    
    all_passed = True
    for input_text, expected in test_cases:
        result = sanitize_text(input_text)
        passed = result == expected
        all_passed &= passed
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {repr(input_text[:30])}...")
        if not passed:
            print(f"  Expected: {repr(expected)}")
            print(f"  Got:      {repr(result)}")
        
        # Detect problematic chars in input
        problems = detect_problematic_chars(input_text)
        if problems:
            print(f"  Found: {problems}")
    
    print("\n" + "="*60)
    
    # Test the specific story text
    story_snippet = """Marcus walked through\u0014not to his cubicle, but onto empty street.
Employee photos covered the desk\u0014strangers wearing Marcus's defeated expression.
A door materialized in the conference room wall\u0014white frame, brass handle."""
    
    print("\nTesting story snippet with weird characters:")
    print("Original (with problems):")
    problems = detect_problematic_chars(story_snippet)
    print(f"Problematic characters found: {problems}")
    
    sanitized = sanitize_text(story_snippet)
    print("\nSanitized version:")
    print(sanitized)
    
    print("\n" + "="*60)
    if all_passed:
        print("All tests PASSED! ✓")
    else:
        print("Some tests FAILED! ✗")
    
    return all_passed


if __name__ == "__main__":
    success = test_sanitization()
    sys.exit(0 if success else 1)