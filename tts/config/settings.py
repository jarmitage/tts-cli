from enum import Enum, auto

class OutputMode(Enum):
    PLAY = auto()      # Only play audio
    SAVE = auto()      # Only save to file
    BOTH = auto()      # Both play and save

# Default values
DEFAULT_SAMPLE_RATE = 24000
DEFAULT_VOICE = "bm_george"  # Male British English voice
DEFAULT_SPEED = 1.0
DEFAULT_SENTENCES_PER_CHUNK = 3
DEFAULT_EXAGGERATION = 0.5
DEFAULT_CFG_WEIGHT = 0.5

# Language codes for Kokoro engine
LANGUAGE_CODES = {
    'en-us': 'a',  # American English
    'en-gb': 'b',  # British English
    'es': 'e',     # Spanish
    'fr': 'f',     # French
    'hi': 'h',     # Hindi
    'it': 'i',     # Italian
    'ja': 'j',     # Japanese
    'pt-br': 'p',  # Brazilian Portuguese
    'zh': 'z'      # Mandarin Chinese
} 