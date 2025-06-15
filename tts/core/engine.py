from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Tuple
import numpy as np

class TTSEngineType(Enum):
    KOKORO = "kokoro"
    CHATTERBOX = "chatterbox"

class TTSEngine(ABC):
    """Base class for TTS engines."""
    
    @abstractmethod
    def generate(
        self,
        text: str,
        voice: str,
        speed: float = 1.0,
        audio_prompt_path: Optional[str] = None,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        **kwargs
    ) -> Tuple[str, str, np.ndarray]:
        """Generate speech from text.
        
        Args:
            text: Input text to synthesize
            voice: Voice to use for synthesis
            speed: Speech rate multiplier
            audio_prompt_path: Optional path to audio prompt file
            exaggeration: Emotion exaggeration factor
            cfg_weight: Classifier-free guidance weight
            
        Returns:
            Tuple of (graphemes, phonemes, audio_data)
        """
        pass
    
    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """Get the sample rate of the engine."""
        pass 