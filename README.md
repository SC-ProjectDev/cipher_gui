# Cipher Analysis Terminal

A cyberpunk-themed desktop GUI for encoding, decoding, and analyzing classical ciphers, built with Python and PyQt6.

## Features

### Supported Ciphers & Transforms

| Algorithm | Description |
|-----------|-------------|
| ROT13 | Classic letter rotation (letters only) |
| ROT-47 | Rotation over the full printable ASCII range (33–126) |
| Caesar Cipher | Custom shift (1–25) via the shift spinner |
| Atbash | Alphabet reversal cipher (A=Z, B=Y, ...) |
| Base64 | Encode and decode UTF-8 text (auto-padding on decode) |
| Reverse Text | Simple string reversal, chainable via the Reverse toggle |

### Analysis Tools

- **Frequency Analysis** — real-time top-5 character frequency of the input
- **Brute Force** — tries all 25 Caesar shifts, scores each result by English-letter
  readability, and shows the 5 most likely decryptions
- **Quick Crypto Suggestion** — heuristics that hint when input looks like
  ROT-47/printable-ASCII ciphertext

### Other Controls

- Copy output to clipboard
- Save output to a text file
- Reverse toggle for pre-processing input
- Real-time stats panel that updates as you type

## Installation

Requires Python 3.9+.

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python cipher_terminal_app.py
```

1. Paste or type text into the **INPUT TEXT** panel.
2. Choose an algorithm from the **SELECT ALGO** dropdown.
3. (Caesar only) set the **SHIFT** value.
4. Click **RUN CIPHER** — the result appears in the output panel.
5. Click **BRUTE FORCE** to attack an unknown Caesar/ROT ciphertext.

## Project Structure

| File | Purpose |
|------|---------|
| `cipher_terminal_app.py` | PyQt6 GUI: layout, styling, and signal wiring |
| `cipher_backend.py` | Pure-Python cipher implementations and analysis functions |

The backend has no third-party dependencies and can be imported or tested
independently of the GUI.

## Requirements

- `PyQt6` — GUI framework (only third-party dependency)
- Standard library: `re`, `string`, `base64`, `sys`, `typing`
