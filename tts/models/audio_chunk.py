from dataclasses import dataclass
import numpy as np

@dataclass
class AudioChunk:
    """Container for generated audio chunks and their metadata."""
    text: str
    phonemes: str
    audio: np.ndarray
    index: int 