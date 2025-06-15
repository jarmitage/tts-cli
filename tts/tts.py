#!/usr/bin/env python3
"""
TTS command line tool for generating speech from text in multiple languages.
Supports both Kokoro and Chatterbox TTS engines.
"""

import fire
import soundfile as sf
import sounddevice as sd
from typing import Optional, Union, List
from pathlib import Path
import os
import markdown
import re
from bs4 import BeautifulSoup
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass
import sys
from .engines import TTSEngine, KokoroEngine, ChatterboxEngine

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

class OutputMode(Enum):
    PLAY = auto()      # Only play audio
    SAVE = auto()      # Only save to file
    BOTH = auto()      # Both play and save

class TTSEngineType(Enum):
    KOKORO = "kokoro"
    CHATTERBOX = "chatterbox"

@dataclass
class AudioChunk:
    """Container for generated audio chunks and their metadata."""
    text: str
    phonemes: str
    audio: np.ndarray
    index: int

def read_text_file(file_path: str) -> str:
    """Read text from a plain text file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_markdown_file(file_path: str) -> str:
    """
    Read and convert markdown file to plain text.
    Strips HTML tags and handles basic markdown formatting.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html = markdown.markdown(md_content)
    
    # Parse HTML and extract text
    soup = BeautifulSoup(html, 'html.parser')
    
    # Handle headers and paragraphs with newlines
    for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
        elem.append('\n\n')
    
    # Extract text and clean up whitespace
    text = soup.get_text()
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def play_audio(audio: np.ndarray, sample_rate: int, blocking: bool = True) -> None:
    """Play audio using sounddevice."""
    try:
        sd.play(audio, sample_rate, blocking=blocking)
        if blocking:
            sd.wait()
    except sd.PortAudioError as e:
        print(f"Audio playback error: {e}")

def save_audio(audio_chunk: AudioChunk, output_path: Path, filename: str, sample_rate: int) -> None:
    """Save audio chunk to file."""
    # Always use numbered chunks for consistency
    output_file = output_path / f"{filename}_{audio_chunk.index}.wav"
    
    print(f"Saving to: {output_file}")
    sf.write(str(output_file), audio_chunk.audio, sample_rate)

def process_audio_chunk(
    chunk: AudioChunk,
    output_mode: OutputMode,
    output_path: Optional[Path],
    filename: str,
    sample_rate: int,
    wait_after_play: bool = True
) -> None:
    """Process a single audio chunk according to output mode."""
    print(f"\nProcessing chunk {chunk.index}:")
    print(f"Text: {chunk.text}")
    print(f"Phonemes: {chunk.phonemes}")

    if output_mode in (OutputMode.PLAY, OutputMode.BOTH):
        print("Playing audio...")
        play_audio(chunk.audio, sample_rate, blocking=wait_after_play)
    
    if output_mode in (OutputMode.SAVE, OutputMode.BOTH) and output_path:
        save_audio(chunk, output_path, filename, sample_rate)
    
    print("-" * 40)

def get_audio_chunks(output_path: Path, filename: str) -> List[Path]:
    """Get sorted list of audio chunk files."""
    chunks = sorted(output_path.glob(f"{filename}_*.wav"))
    if not chunks:
        print("No audio chunks found to stitch")
    return chunks

def create_chunk_list_file(chunks: List[Path], output_path: Path) -> Path:
    """Create a temporary file listing all audio chunks for ffmpeg."""
    list_file = output_path / "chunks.txt"
    with open(list_file, 'w') as f:
        for chunk in chunks:
            f.write(f"file '{chunk.name}'\n")
    return list_file

def run_ffmpeg_stitch(list_file: Path, output_file: Path) -> None:
    """Run ffmpeg to concatenate audio files."""
    import subprocess
    try:
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', str(list_file),
            '-c', 'copy',
            str(output_file)
        ], check=True)
        print(f"\nSuccessfully combined audio chunks into: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error stitching audio files: {e}")
    except Exception as e:
        print(f"Unexpected error during audio stitching: {e}")

def cleanup_files(list_file: Path, chunks: List[Path]) -> None:
    """Clean up temporary files after stitching."""
    try:
        list_file.unlink()
        for chunk in chunks:
            chunk.unlink()
    except Exception as e:
        print(f"Warning: Error during cleanup: {e}")

def stitch_audio_files(output_path: Path, filename: str) -> None:
    """Combine numbered audio chunks into a single file using ffmpeg."""
    # Get audio chunks
    chunks = get_audio_chunks(output_path, filename)
    if not chunks:
        return
        
    # Create file list for ffmpeg
    list_file = create_chunk_list_file(chunks, output_path)
    
    # Output file path
    output_file = output_path / f"{filename}.wav"
    
    # Run ffmpeg to concatenate files
    run_ffmpeg_stitch(list_file, output_file)
    
    # Clean up individual chunks and list file
    cleanup_files(list_file, chunks)

def validate_inputs(text: Optional[str], input_file: Optional[str]) -> None:
    """Validate input parameters."""
    if text is None and input_file is None:
        raise ValueError("Either text or input_file must be provided")
    if text is not None and input_file is not None:
        raise ValueError("Cannot provide both text and input_file")

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

def prepare_output_directory(output_mode: OutputMode, output_dir: str) -> Optional[Path]:
    """Prepare output directory if needed."""
    if output_mode in (OutputMode.SAVE, OutputMode.BOTH):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    return None

def read_input_file(input_file: str) -> str:
    """Read and process input file based on its type."""
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    if input_path.suffix.lower() == '.md':
        return read_markdown_file(input_file)
    elif input_path.suffix.lower() == '.txt':
        return read_text_file(input_file)
    else:
        raise ValueError("Input file must be .txt or .md format")

def process_text_chunks(text: str, split_pattern: Optional[str]) -> List[str]:
    """Process text into chunks for TTS processing."""
    if not isinstance(text, str):
        return text if text else []
    
    # Ensure text ends with sentence-ending punctuation
    if text and not text.rstrip()[-1] in '.!?':
        text = text.rstrip() + '.'
    
    if split_pattern:
        texts = [t.strip() for t in re.split(split_pattern, text) if t.strip()]
        # Ensure each split chunk ends with punctuation
        texts = [t if t.rstrip()[-1] in '.!?' else t.rstrip() + '.' for t in texts]
    else:
        texts = [text]
    
    return texts

def create_tts_engine(engine_type: TTSEngineType, language: str, device: str) -> TTSEngine:
    """Create and return the appropriate TTS engine."""
    if engine_type == TTSEngineType.KOKORO:
        return KokoroEngine(language_code=LANGUAGE_CODES[language])
    else:  # Chatterbox
        return ChatterboxEngine(device=device)

def process_chunks(
    engine: TTSEngine,
    processed_texts: List[str],
    output_mode: OutputMode,
    output_path: Optional[Path],
    filename: str,
    voice: str,
    speed: float,
    audio_prompt_path: Optional[str],
    exaggeration: float,
    cfg_weight: float,
    wait_after_play: bool
) -> None:
    """Process all text chunks through the TTS engine."""
    for i, chunk_text in enumerate(processed_texts):
        # Generate audio using the selected engine
        graphemes, phonemes, audio = engine.generate(
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
            sample_rate=engine.sample_rate,
            wait_after_play=wait_after_play
        )

def generate_speech(
    text: Optional[str] = None,
    input_file: Optional[str] = None,
    output_dir: Optional[str] = ".",
    filename: str = "output",
    language: str = "en-gb",
    voice: str = "bf_isabella",
    speed: float = 1.0,
    split_pattern: Optional[str] = None,
    sample_rate: int = 24000,
    mode: str = "both",
    wait_after_play: bool = True,
    stitch: bool = False,
    engine: str = "kokoro",
    device: Optional[str] = None,
    audio_prompt_path: Optional[str] = None,
    exaggeration: float = 0.5,
    cfg_weight: float = 0.5,
) -> None:
    """
    Generate speech from text using either Kokoro or Chatterbox TTS.

    Args:
        text: Direct input text to convert to speech
        input_file: Path to input file (.txt or .md)
        output_dir: Directory path for output files (defaults to current directory)
        filename: Base filename for output (without extension)
        language: Language code (en-us, en-gb, es, fr, hi, it, ja, pt-br, zh)
        voice: Voice ID to use (e.g. bf_alice)
        speed: Speech speed multiplier
        split_pattern: Regex pattern for splitting text into chunks (None for no splitting)
        sample_rate: Output audio sample rate in Hz
        mode: Output mode ('play', 'save', or 'both')
        wait_after_play: Wait for audio to finish before processing next chunk
        stitch: If True, combine all audio chunks into a single file (only in save modes)
        engine: TTS engine to use ('kokoro' or 'chatterbox')
        device: Device to use for Chatterbox ('cuda', 'mps', or 'cpu'). If None, automatically selects the best available device.
        audio_prompt_path: Path to audio file for voice cloning (Chatterbox only)
        exaggeration: Emotion exaggeration control (Chatterbox only, 0.0-1.0)
        cfg_weight: Configuration weight (Chatterbox only, 0.0-1.0)
    """
    # Input validation
    validate_inputs(text, input_file)
    
    # Parse and validate modes and engine
    output_mode = parse_output_mode(mode)
    engine_type = parse_engine_type(engine)
    validate_language(engine_type, language)
    
    # Prepare output directory
    output_path = prepare_output_directory(output_mode, output_dir)
    
    # Handle file input
    if input_file is not None:
        text = read_input_file(input_file)
        if filename == "output":
            filename = Path(input_file).stem
    
    # Process text into chunks
    texts = process_text_chunks(text, split_pattern)
    
    # Create TTS engine
    tts_engine = create_tts_engine(engine_type, language, device)
    
    # Process all chunks
    process_chunks(
        engine=tts_engine,
        processed_texts=texts,
        output_mode=output_mode,
        output_path=output_path,
        filename=filename,
        voice=voice,
        speed=speed,
        audio_prompt_path=audio_prompt_path,
        exaggeration=exaggeration,
        cfg_weight=cfg_weight,
        wait_after_play=wait_after_play
    )
    
    # Stitch audio files if requested and in a save mode
    if stitch and output_path and output_mode in (OutputMode.SAVE, OutputMode.BOTH):
        stitch_audio_files(output_path, filename)

def main():
    """
    Main entry point for the Kokoro TTS command line tool.
    """
    try:
        if len(sys.argv) == 1:
            sys.argv.append("--help")
        fire.Fire(generate_speech)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
