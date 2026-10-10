#!/usr/bin/env python3
"""
cipher_backend.py
Core logic for the Cipher Analysis Terminal, including:
• ROT13, ROT-47
• Caesar Cipher (custom shift)
• Atbash
• Base64 (Encode/Decode)
• Text Reversal
• Frequency Analysis & Readability Score (for brute-forcing)
"""
import re
import string
import base64
from typing import Callable, Dict, Tuple

# === Common Helpers ===

# Set of common English letters for frequency analysis score
ENGLISH_LETTERS = {'e', 't', 'a', 'o', 'i', 'n', 's', 'h', 'r'}

# Regex to strip zero-width characters (for ROT47)
_ZW_RE = re.compile(r'[\u200B\u200C\u200D\uFEFF]')

# === ROT13 (Fixed) ===
# Variable name fixed: rot13table -> _rot13_table
_rot13_table = str.maketrans(
    string.ascii_uppercase + string.ascii_lowercase,
    string.ascii_uppercase[13:] + string.ascii_uppercase[:13]
    + string.ascii_lowercase[13:] + string.ascii_lowercase[:13]
)

def rot13(s: str) -> str:
    """Applies the ROT13 cipher (letters only)."""
    return s.translate(_rot13_table)

# === ROT47 (Fixed and Core) ===

def rot47_core(s: str) -> str:
    """Applies the ROT47 cipher to printable ASCII (33-126)."""
    out = []
    for ch in s:
        o = ord(ch)
        # Printable ASCII block: 33 ('!') to 126 ('~'). Total 94 chars.
        if 33 <= o <= 126:
            # Formula: 33 + ((current_ord - start_ord + shift) % range)
            out.append(chr(33 + ((o - 33 + 47) % 94)))
        else:
            out.append(ch)  # Leave others unchanged (spaces, newlines, etc.)
    return ''.join(out)

def rot47_no_zw(s: str) -> str:
    """ROT-47 after removing zero-width characters (as per original design)."""
    return rot47_core(_ZW_RE.sub('', s))

# === Caesar Cipher (New) ===

def caesar_cipher(s: str, shift: int) -> str:
    """Generic Caesar cipher (applies to letters only, like ROT13)."""
    shift = shift % 26
    
    # Create the translation table
    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    
    table = str.maketrans(
        upper + lower,
        upper[shift:] + upper[:shift] +
        lower[shift:] + lower[:shift]
    )
    return s.translate(table)

# === Atbash (New) ===

def atbash(s: str) -> str:
    """Applies the Atbash cipher (A=Z, B=Y, etc.)."""
    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    
    # Reverse the alphabets for the mapping
    table = str.maketrans(
        upper + lower,
        upper[::-1] + lower[::-1]
    )
    return s.translate(table)

# === Base64 (New) ===

def base64_encode(s: str) -> str:
    """Encodes text to Base64 (returns string, strips trailing newline)."""
    try:
        encoded_bytes = base64.b64encode(s.encode('utf-8'))
        return encoded_bytes.decode('utf-8').strip()
    except Exception:
        return "[ERROR: Base64 Encoding failed]"

def base64_decode(s: str) -> str:
    """Decodes Base64 to text (handles padding issues)."""
    try:
        # Base64 requires input length to be a multiple of 4. Add padding if needed.
        s_padded = s + '=' * (4 - len(s) % 4)
        decoded_bytes = base64.b64decode(s_padded)
        return decoded_bytes.decode('utf-8')
    except Exception:
        return "[ERROR: Base64 Decoding failed]"

# === Reversal Helper ===

def reverse_text(s: str) -> str:
    """Reverses the text string."""
    return s[::-1]

# === Cipher Registry for GUI Integration ===
# (Function, needs_shift, is_encoding) - needs_shift is for Caesar
CIPHERS: Dict[str, Tuple[str, Callable, bool, bool]] = {
    # ROT Ciphers (Self-Inverting, so encode/decode are the same function)
    "ROT13": ("ROT13 (Letters Only)", rot13, False, True),
    "ROT47": ("ROT-47 (Printable ASCII)", rot47_core, False, True),
    
    # Classical Ciphers
    "CAESAR": ("Caesar Cipher", lambda s, shift=3: caesar_cipher(s, shift), True, True), # Shift input handled by GUI
    "ATBASH": ("Atbash", atbash, False, True),
    
    # Encoding Schemes (Requires separate encode/decode functions)
    "B64_ENC": ("Base64 Encode", base64_encode, False, True),
    "B64_DEC": ("Base64 Decode", base64_decode, False, False),
    
    # Helper Transformations
    "REVERSE": ("Reverse Text", reverse_text, False, True),
}

# --------------------------------------------------------------------------------------

## 2. Analysis and Brute-Force Functions

# These functions will power the **'Stats' Panel** and the **'Brute Force'** mode.

def frequency_analysis(text: str) -> Dict[str, float]:
    """Calculates the frequency of each alphabetic character in the text."""
    text = text.lower()
    total_alpha_chars = 0
    char_counts: Dict[str, int] = {}
    
    for char in text:
        if 'a' <= char <= 'z':
            total_alpha_chars += 1
            char_counts[char] = char_counts.get(char, 0) + 1
            
    if total_alpha_chars == 0:
        return {}
    
    # Convert counts to percentages, sorted by frequency
    frequencies = {
        char: (count / total_alpha_chars) * 100 
        for char, count in char_counts.items()
    }
    
    # Sort by frequency (descending)
    sorted_freq = dict(
        sorted(frequencies.items(), key=lambda item: item[1], reverse=True)
    )
    
    return sorted_freq

def calculate_readability_score(text: str) -> float:
    """
    Assigns a simple score based on the frequency of common English letters.
    A higher score suggests the text is closer to natural English.
    """
    text = text.lower()
    score = 0
    
    # Simple check: Does the text contain a high number of common English letters?
    for char, freq in frequency_analysis(text).items():
        if char in ENGLISH_LETTERS:
            # Weight the score by the frequency of common letters
            score += freq
            
    # Normalize by total number of characters (to prevent very short strings from having a perfect score)
    return score / (len(text) if len(text) > 0 else 1)

def rot_brute_force(text: str) -> Dict[int, Tuple[str, float]]:
    """
    Applies all 25 possible Caesar shifts (ROT 1-25) to find likely decryptions.
    Returns a dictionary of {shift: (decoded_text, score)}.
    """
    results = {}
    
    # ROT13 is shift 13, but we check all 25 for any Caesar cipher.
    for shift in range(1, 26):
        # To 'decode' a Caesar cipher, we apply the inverse shift
        inverse_shift = 26 - shift
        decoded_text = caesar_cipher(text, inverse_shift)
        score = calculate_readability_score(decoded_text)
        results[shift] = (decoded_text, score)
        
    # Sort results by the highest readability score
    sorted_results = dict(
        sorted(results.items(), key=lambda item: item[1][1], reverse=True)
    )
    
    return sorted_results