from typing import Optional, Tuple
import numpy as np
import torch
from chatterbox.tts import ChatterboxTTS
from .engine import TTSEngine

def get_available_device() -> str:
    """Get the best available device for model inference."""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"

class ChatterboxEngine(TTSEngine):
    """Chatterbox TTS engine implementation."""
    
    def __init__(self, device: Optional[str] = None):
        if device is None:
            device = get_available_device()
        self.model = ChatterboxTTS.from_pretrained(device=device)
        self._sample_rate = self.model.sr
        self.device = device
    
    def generate(
        self,
        text: str,
        voice: str = None,  # Not used by Chatterbox
        speed: float = 1.0,  # Not used by Chatterbox
        audio_prompt_path: Optional[str] = None,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        **kwargs
    ) -> Tuple[str, str, np.ndarray]:
        """Generate speech using Chatterbox TTS."""
        wav = self.model.generate(
            text,
            audio_prompt_path=audio_prompt_path,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight
        )
        # Convert torch tensor to numpy array
        audio = wav.squeeze().detach().numpy()
        # Return empty strings for graphemes/phonemes as Chatterbox doesn't provide these
        return text, "", audio
    
    @property
    def sample_rate(self) -> int:
        return self._sample_rate 