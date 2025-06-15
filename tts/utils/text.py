import re
from typing import List, Optional

def process_text_chunks(text: str, split_pattern: Optional[str], sentences_per_chunk: int = 3) -> List[str]:
    """Process text into chunks for TTS processing.
    
    Args:
        text: The input text to process
        split_pattern: Optional regex pattern for custom splitting
        sentences_per_chunk: Number of sentences to include in each chunk (default: 3)
    """
    if not isinstance(text, str):
        return text if text else []
    
    # Ensure text ends with sentence-ending punctuation
    if text and not text.rstrip()[-1] in '.!?':
        text = text.rstrip() + '.'
    
    if split_pattern:
        texts = [t.strip() for t in re.split(split_pattern, text) if t.strip()]
    else:
        # Split into individual sentences first
        sentences = [t.strip() for t in re.split(r'(?<=[.!?])\s+', text) if t.strip()]
        # Group sentences into chunks
        texts = []
        for i in range(0, len(sentences), sentences_per_chunk):
            chunk = ' '.join(sentences[i:i + sentences_per_chunk])
            texts.append(chunk)
    
    # Ensure each split chunk ends with punctuation
    texts = [t if t.rstrip()[-1] in '.!?' else t.rstrip() + '.' for t in texts]
    
    return texts 