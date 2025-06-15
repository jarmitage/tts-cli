"""
TTS command line tool for generating speech from text in multiple languages.
Supports both Kokoro and Chatterbox TTS engines.
"""

from .cli import generate_speech, main

__version__ = "0.1.0"
__all__ = ["generate_speech", "main"]
