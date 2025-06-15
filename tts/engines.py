from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
import numpy as np
from kokoro import KPipeline
from chatterbox.tts import ChatterboxTTS
import torchaudio as ta
import torch
from enum import Enum

class TTSEngineType(Enum):
    KOKORO = "kokoro"
    CHATTERBOX = "chatterbox"

class TTSEngine(ABC):
    """Base class for TTS engines."""
    
    @abstractmethod
    def generate(self, text: str, **kwargs) -> Tuple[str, str, np.ndarray]:
        """Generate speech from text.
        
        Returns:
            Tuple of (graphemes, phonemes, audio_data)
        """
        pass
    
    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """Get the sample rate of the engine."""
        pass

class KokoroEngine(TTSEngine):
    """Kokoro TTS engine implementation."""
    
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
    
    DEFAULT_VOICE = "bf_isabella"
    DEFAULT_SAMPLE_RATE = 24000
    
    def __init__(self, language_code: str):
        self.pipeline = KPipeline(lang_code=language_code)
        self._sample_rate = self.DEFAULT_SAMPLE_RATE
    
    def generate(self, text: str, voice: str = "bf_isabella", speed: float = 1.0, **kwargs) -> Tuple[str, str, np.ndarray]:
        generator = self.pipeline(
            [text],
            voice=voice,
            speed=speed,
            split_pattern=None
        )
        graphemes, phonemes, audio = next(generator)
        return graphemes, phonemes, audio
    
    @property
    def sample_rate(self) -> int:
        return self._sample_rate

def get_available_device() -> str:
    """Get the best available device for PyTorch."""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"

class ChatterboxEngine(TTSEngine):
    """Chatterbox TTS engine implementation."""
    
    def __init__(self, device: str = None):
        if device is None:
            device = get_available_device()
        self.model = ChatterboxTTS.from_pretrained(device=device)
        self._sample_rate = self.model.sr
        self.device = device
    
    def generate(
        self,
        text: str,
        audio_prompt_path: Optional[str] = None,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        **kwargs
    ) -> Tuple[str, str, np.ndarray]:
        wav = self.model.generate(
            text,
            audio_prompt_path=audio_prompt_path,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight
        )
        # Convert torch tensor to numpy array, keeping it on the same device
        audio = wav.squeeze().detach().numpy()
        # Return empty strings for graphemes/phonemes as Chatterbox doesn't provide these
        return text, "", audio
    
    @property
    def sample_rate(self) -> int:
        return self._sample_rate 