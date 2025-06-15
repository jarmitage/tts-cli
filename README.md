# TTS CLI tool

A simple command-line interface for text-to-speech conversion, supporting both Kokoro and Chatterbox TTS engines.

## Installation

```bash
git clone git@github.com:jarmitage/kokoro-tts-cli.git
cd kokoro-tts-cli
pip install -e .
```

## Usage

Basic usage with Kokoro:
```bash
tts --text 'This text is speaking!' --language en-gb
```

Basic usage with Chatterbox:
```bash
tts --text 'This text is speaking!' --engine chatterbox
```

## Command Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--text` | None | Direct input text to convert to speech |
| `--input_file` | None | Path to input file (.txt or .md) |
| `--output_dir` | "." | Directory path for output files |
| `--filename` | "output" | Base filename for output (without extension) |
| `--language` | "en-gb" | Language code (see supported languages below) |
| `--voice` | "bf_isabella" | Voice ID to use (e.g. bf_alice) |
| `--speed` | 1.0 | Speech speed multiplier |
| `--split_pattern` | "\n+" | Regex pattern for splitting text into chunks |
| `--sample_rate` | 24000 | Output audio sample rate in Hz |
| `--mode` | "both" | Output mode ('play', 'save', or 'both') |
| `--wait_after_play` | True | Wait for audio to finish before processing next chunk |
| `--stitch` | False | Combine all audio chunks into a single file (only in save modes) |
| `--engine` | "kokoro" | TTS engine to use ('kokoro' or 'chatterbox') |
| `--device` | None | Device to use for Chatterbox ('cuda', 'mps', or 'cpu'). If None, automatically selects the best available device. |
| `--audio_prompt_path` | None | Path to audio file for voice cloning (Chatterbox only) |
| `--exaggeration` | 0.5 | Emotion exaggeration control (Chatterbox only, 0.0-1.0) |
| `--cfg_weight` | 0.5 | Configuration weight (Chatterbox only, 0.0-1.0) |

### Supported Languages

#### Kokoro Engine
- `en-us`: American English
- `en-gb`: British English
- `es`: Spanish
- `fr`: French
- `hi`: Hindi
- `it`: Italian
- `ja`: Japanese
- `pt-br`: Brazilian Portuguese
- `zh`: Mandarin Chinese

#### Chatterbox Engine
- Currently only supports English (`en-gb`)

## Examples

1. Convert text to speech using Kokoro:
```bash
tts --text 'This text is speaking!' --language en-gb
```

2. Convert text to speech using Chatterbox with voice cloning:
```bash
tts --text 'This text is speaking!' --engine chatterbox --audio_prompt_path reference.wav
```

3. Convert text with Chatterbox's emotion control:
```bash
tts --text 'This text is speaking!' --engine chatterbox --exaggeration 0.7 --cfg_weight 0.3
```

4. Use Chatterbox with specific device:
```bash
# Use NVIDIA GPU
tts --text "Hello" --engine chatterbox --device cuda

# Use Apple Silicon GPU
tts --text "Hello" --engine chatterbox --device mps

# Use CPU
tts --text "Hello" --engine chatterbox --device cpu

# Auto-select best available device
tts --text "Hello" --engine chatterbox
```

5. Convert a markdown file to speech and save it:
```bash
tts --input_file document.md --mode save --output_dir output/
```

6. Install it locally in development mode:
```bash
cd tts
pip install -e .
```

After installation, you can use the command `tts` from anywhere in your terminal. For example:
```bash
tts --text 'This text is speaking!' --language en-gb
```

## Device Support

The Chatterbox engine supports multiple devices for inference:

- **CUDA**: For NVIDIA GPUs
- **MPS**: For Apple Silicon Macs (M1/M2/M3)
- **CPU**: As a fallback option

The CLI will automatically select the best available device if none is specified. You can override this by explicitly setting the `--device` parameter.
