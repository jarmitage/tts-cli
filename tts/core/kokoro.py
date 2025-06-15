from typing import Optional, Tuple, Dict
import numpy as np
from kokoro import KPipeline
from .engine import TTSEngine

class KokoroEngine(TTSEngine):
    """Kokoro TTS engine implementation.
    """
    
    DEFAULT_SAMPLE_RATE = 24000
    DEFAULT_VOICE = "bm_george"  # Male British English voice
    
    # Available voices by language
    VOICES: Dict[str, Dict[str, str]] = {
        # American English voices
        "af_heart": {"gender": "female", "language": "American English"},
        "af_alloy": {"gender": "female", "language": "American English"},
        "af_aoede": {"gender": "female", "language": "American English"},
        "af_bella": {"gender": "female", "language": "American English"},
        "af_jessica": {"gender": "female", "language": "American English"},
        "af_kore": {"gender": "female", "language": "American English"},
        "af_nicole": {"gender": "female", "language": "American English"},
        "af_nova": {"gender": "female", "language": "American English"},
        "af_river": {"gender": "female", "language": "American English"},
        "af_sarah": {"gender": "female", "language": "American English"},
        "af_sky": {"gender": "female", "language": "American English"},
        "am_adam": {"gender": "male", "language": "American English"},
        "am_echo": {"gender": "male", "language": "American English"},
        "am_eric": {"gender": "male", "language": "American English"},
        "am_fenrir": {"gender": "male", "language": "American English"},
        "am_liam": {"gender": "male", "language": "American English"},
        "am_michael": {"gender": "male", "language": "American English"},
        "am_onyx": {"gender": "male", "language": "American English"},
        "am_puck": {"gender": "male", "language": "American English"},
        "am_santa": {"gender": "male", "language": "American English"},
        
        # British English voices
        "bf_alice": {"gender": "female", "language": "British English"},
        "bf_emma": {"gender": "female", "language": "British English"},
        "bf_isabella": {"gender": "female", "language": "British English"},
        "bf_lily": {"gender": "female", "language": "British English"},
        "bm_daniel": {"gender": "male", "language": "British English"},
        "bm_fable": {"gender": "male", "language": "British English"},
        "bm_george": {"gender": "male", "language": "British English"},
        "bm_lewis": {"gender": "male", "language": "British English"},
        
        # Japanese voices
        "jf_alpha": {"gender": "female", "language": "Japanese"},
        "jf_gongitsune": {"gender": "female", "language": "Japanese"},
        "jf_nezumi": {"gender": "female", "language": "Japanese"},
        "jf_tebukuro": {"gender": "female", "language": "Japanese"},
        "jm_kumo": {"gender": "male", "language": "Japanese"},
        
        # Mandarin Chinese voices
        "zf_xiaobei": {"gender": "female", "language": "Mandarin Chinese"},
        "zf_xiaoni": {"gender": "female", "language": "Mandarin Chinese"},
        "zf_xiaoxiao": {"gender": "female", "language": "Mandarin Chinese"},
        "zf_xiaoyi": {"gender": "female", "language": "Mandarin Chinese"},
        "zm_yunjian": {"gender": "male", "language": "Mandarin Chinese"},
        "zm_yunxi": {"gender": "male", "language": "Mandarin Chinese"},
        "zm_yunxia": {"gender": "male", "language": "Mandarin Chinese"},
        "zm_yunyang": {"gender": "male", "language": "Mandarin Chinese"},
        
        # Spanish voices
        "ef_dora": {"gender": "female", "language": "Spanish"},
        "em_alex": {"gender": "male", "language": "Spanish"},
        "em_santa": {"gender": "male", "language": "Spanish"},
        
        # French voices
        "ff_siwis": {"gender": "female", "language": "French"},
        
        # Hindi voices
        "hf_alpha": {"gender": "female", "language": "Hindi"},
        "hf_beta": {"gender": "female", "language": "Hindi"},
        "hm_omega": {"gender": "male", "language": "Hindi"},
        "hm_psi": {"gender": "male", "language": "Hindi"},
        
        # Italian voices
        "if_sara": {"gender": "female", "language": "Italian"},
        "im_nicola": {"gender": "male", "language": "Italian"},
        
        # Brazilian Portuguese voices
        "pf_dora": {"gender": "female", "language": "Brazilian Portuguese"},
        "pm_alex": {"gender": "male", "language": "Brazilian Portuguese"},
        "pm_santa": {"gender": "male", "language": "Brazilian Portuguese"},
    }
    
    def __init__(self, language_code: str):
        self.pipeline = KPipeline(lang_code=language_code)
        self._sample_rate = self.DEFAULT_SAMPLE_RATE
    
    def generate(
        self,
        text: str,
        voice: str = DEFAULT_VOICE,
        speed: float = 1.0,
        audio_prompt_path: Optional[str] = None,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        **kwargs
    ) -> Tuple[str, str, np.ndarray]:
        """Generate speech using Kokoro TTS."""
        if voice not in self.VOICES:
            raise ValueError(
                f"Voice '{voice}' not found. Available voices: {', '.join(sorted(self.VOICES.keys()))}"
            )
            
        # Call the pipeline directly with a list of texts
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