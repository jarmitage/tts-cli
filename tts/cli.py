#!/usr/bin/env python3
"""
TTS command line tool for generating speech from text in multiple languages.
Supports both Kokoro and Chatterbox TTS engines.
"""

import sys
import fire
from pathlib import Path
from typing import Optional

from .core.engine import TTSEngineType
from .utils.audio import process_audio_chunk, stitch_audio_files
from .utils.file import read_input_file, prepare_output_directory
from .utils.text import process_text_chunks
from .config.settings import (
    OutputMode, DEFAULT_SAMPLE_RATE, DEFAULT_VOICE,
    DEFAULT_SPEED, DEFAULT_SENTENCES_PER_CHUNK,
    DEFAULT_EXAGGERATION, DEFAULT_CFG_WEIGHT,
    LANGUAGE_CODES
)
from .models.audio_chunk import AudioChunk

def read_stdin() -> Optional[str]:
    """Read text from standard input."""
    if not sys.stdin.isatty():  # Check if stdin has data
        return sys.stdin.read().strip()
    return None

def validate_inputs(text: Optional[str], input_file: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Validate input parameters and return the text to use."""
    stdin_text = read_stdin()
    
    if text is None and input_file is None and stdin_text is None:
        raise ValueError("Either text, input_file, or stdin input must be provided")
    if sum(1 for x in [text, input_file, stdin_text] if x is not None) > 1:
        raise ValueError("Cannot provide multiple input sources (text, input_file, or stdin)")
    
    return stdin_text, input_file

def parse_output_mode(mode: str) -> OutputMode:
    """Parse and validate output mode."""
    try:
        return OutputMode[mode.upper()]
    except KeyError:
        raise ValueError(f"Invalid mode: {mode}. Must be 'play', 'save', or 'both'")

def parse_engine_type(engine: str) -> TTSEngineType:
    """Parse and validate engine type."""
    try:
        return TTSEngineType(engine.lower())
    except ValueError:
        raise ValueError(f"Invalid engine: {engine}. Must be 'kokoro' or 'chatterbox'")

def validate_language(engine_type: TTSEngineType, language: str) -> None:
    """Validate language support for the selected engine."""
    if engine_type == TTSEngineType.KOKORO and language not in LANGUAGE_CODES:
        raise ValueError(f"Unsupported language code. Must be one of: {', '.join(LANGUAGE_CODES.keys())}")
    if engine_type == TTSEngineType.CHATTERBOX and language != "en-gb":
        raise ValueError("Chatterbox currently only supports English (en-gb)")

def create_tts_engine(engine_type: TTSEngineType, language: str, device: str) -> 'TTSEngine':
    """Create and return the appropriate TTS engine."""
    if engine_type == TTSEngineType.KOKORO:
        from .core.kokoro import KokoroEngine
        return KokoroEngine(language_code=LANGUAGE_CODES[language])
    else:  # Chatterbox
        from .core.chatterbox import ChatterboxEngine
        return ChatterboxEngine(device=device)

def generate_speech(
    text: Optional[str] = None,
    input_file: Optional[str] = None,
    output_dir: Optional[str] = ".",
    filename: str = "output",
    language: str = "en-gb",
    voice: str = DEFAULT_VOICE,
    speed: float = DEFAULT_SPEED,
    split_pattern: Optional[str] = None,
    sentences_per_chunk: int = DEFAULT_SENTENCES_PER_CHUNK,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    mode: str = "play",
    wait_after_play: bool = True,
    stitch: bool = True,
    engine: str = "kokoro",
    device: Optional[str] = None,
    audio_prompt_path: Optional[str] = None,
    exaggeration: float = DEFAULT_EXAGGERATION,
    cfg_weight: float = DEFAULT_CFG_WEIGHT,
) -> None:
    """
    Generate speech from text using either Kokoro or Chatterbox TTS.
    """
    # Input validation and get stdin text if any
    stdin_text, input_file = validate_inputs(text, input_file)
    
    # Parse and validate modes and engine
    output_mode = parse_output_mode(mode)
    engine_type = parse_engine_type(engine)
    validate_language(engine_type, language)
    
    # Prepare output directory
    output_path = None
    if output_mode in (OutputMode.SAVE, OutputMode.BOTH):
        output_path = Path(output_dir)
        prepare_output_directory(output_path)
    
    # Handle input sources
    if stdin_text is not None:
        text = stdin_text
    elif input_file is not None:
        text = read_input_file(input_file)
        if filename == "output":
            filename = Path(input_file).stem
    
    # Early exit if no text
    if not text:
        print("ERROR: No text to process")
        return
    
    # Process text into chunks
    texts = process_text_chunks(text, split_pattern, sentences_per_chunk)
    
    # Create TTS engine
    tts_engine = create_tts_engine(engine_type, language, device)
    
    # Process all chunks
    for i, chunk_text in enumerate(texts):
        # Generate audio using the selected engine
        graphemes, phonemes, audio = tts_engine.generate(
            chunk_text,
            voice=voice,
            speed=speed,
            audio_prompt_path=audio_prompt_path,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight
        )
        
        chunk = AudioChunk(
            text=graphemes,
            phonemes=phonemes,
            audio=audio,
            index=i
        )
        
        process_audio_chunk(
            chunk=chunk,
            output_mode=output_mode,
            output_path=output_path,
            filename=filename,
            sample_rate=tts_engine.sample_rate,
            wait_after_play=wait_after_play
        )
    
    # Stitch audio files if requested and in a save mode
    if stitch and output_path and output_mode in (OutputMode.SAVE, OutputMode.BOTH):
        stitch_audio_files(output_path, filename)

def main():
    """
    Main entry point for the TTS command line tool.
    """
    try:
        # Check if stdin has data and no arguments provided
        if len(sys.argv) == 1 and not sys.stdin.isatty():
            # Call generate_speech with default arguments
            generate_speech()
        else:
            if len(sys.argv) == 1:
                sys.argv.append("--help")
            fire.Fire(generate_speech)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 