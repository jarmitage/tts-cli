# Kokoro TTS CLI tool

A simple command-line interface for Kokoro TTS.

## Installation

```bash
pip install tts
```

## Usage

Basic usage:
```bash
tts --text "Hello, world!" --language en-gb
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

### Supported Languages

- `en-us`: American English
- `en-gb`: British English
- `es`: Spanish
- `fr`: French
- `hi`: Hindi
- `it`: Italian
- `ja`: Japanese
- `pt-br`: Brazilian Portuguese
- `zh`: Mandarin Chinese

## Examples

1. Convert text to speech and play it:
```bash
tts --text "Hello, world!" --language en-gb
```

2. Convert a markdown file to speech and save it:
```bash
tts --input_file document.md --mode save --output_dir output/
```

3. Convert text with custom speed and voice:
```bash
tts --text "Hello, world!" --speed 1.2 --voice bf_alice
```

4. Install it locally in development mode:
```bash
cd tts
pip install -e .
```

After installation, you can use the command `tts` from anywhere in your terminal. For example:
```bash
tts --text "Hello, world!" --language en-gb
```
