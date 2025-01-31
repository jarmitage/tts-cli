#!/usr/bin/env python3
"""
Kokoro TTS command line tool for generating speech from text in multiple languages.
"""

import fire
import soundfile as sf
import sounddevice as sd
from kokoro import KPipeline
from typing import Optional, Union, List
from pathlib import Path
import os
import markdown
import re
from bs4 import BeautifulSoup
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass

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

def stitch_audio_files(output_path: Path, filename: str) -> None:
    """Combine numbered audio chunks into a single file using ffmpeg."""
    import subprocess
    
    # Create file list for ffmpeg
    chunks = sorted(output_path.glob(f"{filename}_*.wav"))
    if not chunks:
        print("No audio chunks found to stitch")
        return
        
    # Create a temporary file list
    list_file = output_path / "chunks.txt"
    with open(list_file, 'w') as f:
        for chunk in chunks:
            f.write(f"file '{chunk.name}'\n")
    
    # Output file path
    output_file = output_path / f"{filename}.wav"
    
    try:
        # Run ffmpeg to concatenate files
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', str(list_file),
            '-c', 'copy',
            str(output_file)
        ], check=True)
        print(f"\nSuccessfully combined audio chunks into: {output_file}")
        
        # Clean up individual chunks and list file
        list_file.unlink()
        for chunk in chunks:
            chunk.unlink()
            
    except subprocess.CalledProcessError as e:
        print(f"Error stitching audio files: {e}")
    except Exception as e:
        print(f"Unexpected error during audio stitching: {e}")

def generate_speech(
    text: Optional[str] = None,
    input_file: Optional[str] = None,
    output_dir: Optional[str] = ".",
    filename: str = "output",
    language: str = "en-gb",
    voice: str = "bf_isabella",
    speed: float = 1.0,
    split_pattern: str = r"\n+",
    sample_rate: int = 24000,
    mode: str = "both",
    wait_after_play: bool = True,
    stitch: bool = False,
) -> None:
    """
    Generate speech from text using Kokoro TTS.

    Args:
        text: Direct input text to convert to speech
        input_file: Path to input file (.txt or .md)
        output_dir: Directory path for output files (defaults to current directory)
        filename: Base filename for output (without extension)
        language: Language code (en-us, en-gb, es, fr, hi, it, ja, pt-br, zh)
        voice: Voice ID to use (e.g. bf_alice)
        speed: Speech speed multiplier
        split_pattern: Regex pattern for splitting text into chunks
        sample_rate: Output audio sample rate in Hz
        mode: Output mode ('play', 'save', or 'both')
        wait_after_play: Wait for audio to finish before processing next chunk
        stitch: If True, combine all audio chunks into a single file (only in save modes)
    """
    # Input validation
    if text is None and input_file is None:
        raise ValueError("Either text or input_file must be provided")
    if text is not None and input_file is not None:
        raise ValueError("Cannot provide both text and input_file")
    
    # Parse output mode
    try:
        output_mode = OutputMode[mode.upper()]
    except KeyError:
        raise ValueError(f"Invalid mode: {mode}. Must be 'play', 'save', or 'both'")
    
    # Validate output directory for save modes
    output_path = None
    if output_mode in (OutputMode.SAVE, OutputMode.BOTH):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    
    # Handle file input
    if input_file is not None:
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Process based on file type
        if input_path.suffix.lower() == '.md':
            text = read_markdown_file(input_file)
        elif input_path.suffix.lower() == '.txt':
            text = read_text_file(input_file)
        else:
            raise ValueError("Input file must be .txt or .md format")
        
        # Use input filename as output filename if not specified
        if filename == "output":
            filename = input_path.stem

    if language not in LANGUAGE_CODES:
        raise ValueError(f"Unsupported language code. Must be one of: {', '.join(LANGUAGE_CODES.keys())}")
    
    # Initialize the TTS pipeline
    pipeline = KPipeline(lang_code=LANGUAGE_CODES[language])
    
    # Generate and process audio
    generator = pipeline(
        text,
        voice=voice,
        speed=speed,
        split_pattern=split_pattern
    )
    
    # Process all chunks
    for i, (graphemes, phonemes, audio) in enumerate(generator):
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
            sample_rate=sample_rate,
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
        fire.Fire(generate_speech)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
