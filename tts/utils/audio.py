import soundfile as sf
import sounddevice as sd
import numpy as np
from pathlib import Path
from typing import List, Optional
import subprocess
from ..models.audio_chunk import AudioChunk
from ..config.settings import OutputMode

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
    chunks = get_audio_chunks(output_path, filename)
    if not chunks:
        return
        
    list_file = create_chunk_list_file(chunks, output_path)
    output_file = output_path / f"{filename}.wav"
    
    run_ffmpeg_stitch(list_file, output_file)
    cleanup_files(list_file, chunks)

def play_audio_file(audio_file: str, volume: float = 1.0) -> tuple[bool, str]:
    """
    Play an audio file using the system's default audio output.
    Args:
        audio_file: Path to the audio file to play
        volume: Playback volume as a multiplier (0.0-1.0, default 1.0)
    Returns:
        (success: bool, message: str)
    """
    try:
        data, samplerate = sf.read(audio_file)
        volume = max(0.0, min(volume, 1.0))
        data = data * volume
        sd.play(data, samplerate)
        sd.wait()
        return True, f"Successfully played audio file: {audio_file}"
    except Exception as e:
        return False, f"Failed to play audio: {e}" 