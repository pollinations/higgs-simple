# Higgs Simple Audio Service

OpenAI-compatible audio service with text-to-speech, speech-to-text, and voice cloning capabilities.

## Features

- **OpenAI Chat Completions API compatibility** - Drop-in replacement
- **Intelligent Text Generation** - Powered by Higgs Audio v2's advanced language model
- **Text-to-Speech** - 6 built-in voices + voice cloning
- **Speech-to-Text** - Whisper-powered transcription  
- **Voice Cloning** - Clone any voice from reference audio
- **High Quality** - 24kHz WAV output
- **Fully Self-hosted** - No external API dependencies, complete privacy control
- **Single Model Architecture** - Higgs Audio v2 handles both text and audio generation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start service
python3 app.py
```

Service runs on `http://localhost:8000`

## Usage

### Text-to-Speech
```python
import requests

response = requests.post("http://localhost:8000/v1/chat/completions", json={
    "model": "gpt-4o-audio-preview",
    "modalities": ["text", "audio"],
    "audio": {"voice": "alloy"},
    "messages": [{"role": "user", "content": "Hello world!"}]
})

audio_data = response.json()["choices"][0]["message"]["audio"]["data"]
```

### Voice Cloning
```python
import base64

# Load reference voice
with open("voice.mp3", "rb") as f:
    voice_b64 = base64.b64encode(f.read()).decode()

response = requests.post("http://localhost:8000/v1/chat/completions", json={
    "model": "gpt-4o-audio-preview", 
    "modalities": ["text", "audio"],
    "audio": {"data": voice_b64},  # Reference audio for cloning
    "messages": [{"role": "user", "content": "Clone this voice!"}]
})
```

### Speech-to-Text
```python
response = requests.post("http://localhost:8000/v1/audio/transcriptions",
    files={"file": ("audio.wav", open("audio.wav", "rb"))},
    data={"model": "whisper-1"}
)

text = response.json()["text"]
```

## Testing Tool

Test voice cloning with the included CLI tool:

```bash
# Clone a voice and make it say something
python3 test_voice_cloning_simple.py /path/to/voice.mp3 "Hello from my cloned voice!"

# Test different voices
python3 test_voice_cloning_simple.py voice1.mp3 "Testing voice 1"
python3 test_voice_cloning_simple.py voice2.mp3 "Testing voice 2"
```

## Available Voices

| Voice | Style |
|-------|-------|
| `alloy` | Natural, conversational |
| `echo` | Clear, authoritative |
| `fable` | Storytelling, engaging |
| `onyx` | Deep, reliable |
| `nova` | Bright, energetic |
| `shimmer` | Gentle, melodic |

## API Endpoints

- **POST** `/v1/chat/completions` - Text generation with optional audio
- **POST** `/v1/audio/transcriptions` - Speech-to-text
- **GET** `/health` - Service status

## Requirements

- Python 3.8+
- CUDA GPU (recommended)
- 8GB+ RAM

## Why This Service?

- ✅ **No API keys** - Self-hosted, completely private
- ✅ **No external dependencies** - Higgs Audio v2 handles everything locally
- ✅ **OpenAI compatible** - Use existing code/libraries  
- ✅ **Voice cloning** - Clone any voice from audio
- ✅ **High quality** - Professional 24kHz output with advanced language understanding
- ✅ **Simple setup** - One command to start
- ✅ **Free** - No usage limits, costs, or internet required
- ✅ **Unified architecture** - Single model for both text and audio generation
