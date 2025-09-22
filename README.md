# Simple Audio Service

**OpenAI-compatible audio API** with voice cloning, speech-to-text, and intelligent responses.

## Features

- 🔄 **Drop-in OpenAI replacement** - Compatible with `/v1/chat/completions`
- 🎤 **Audio input support** - Process speech in chat messages (`input_audio`)
- 🎭 **Voice cloning** - Clone any voice from reference audio
- 🗣️ **Text-to-speech** - 6 built-in voices (alloy, echo, fable, onyx, nova, shimmer)
- 🧠 **Smart responses** - Powered by Higgs Audio v2
- 🏠 **Self-hosted** - No API keys, completely private
- ⚡ **High quality** - 24kHz WAV output

## Quick Start

```bash
# Install and run
pip install -r requirements.txt
python3 app.py

# Or install as system service
sudo ./install-service.sh
```

Service runs on `http://localhost:8000`

## Usage Examples

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

### Audio Input (Speech-to-Text)
```bash
# Process audio input with text response
curl "http://localhost:8000/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "gpt-4o-audio-preview",
      "modalities": ["text", "audio"],
      "audio": {"voice": "alloy"},
      "messages": [{
        "role": "user",
        "content": [
          {"type": "text", "text": "What did I say?"},
          {"type": "input_audio", "input_audio": {"data": "<base64>", "format": "wav"}}
        ]
      }]
    }'
```

## Testing

```bash
# Test voice cloning
python3 test_voice_cloning_simple.py voice.mp3 "Hello from my cloned voice!"

# Test input audio functionality
python3 test_input_audio.py
```

## Built-in Voices

`alloy` • `echo` • `fable` • `onyx` • `nova` • `shimmer`

## System Service

```bash
# Install as systemd service (runs in background)
sudo ./install-service.sh

# Service commands
sudo systemctl start simple-audio-service
sudo systemctl stop simple-audio-service
sudo journalctl -u simple-audio-service -f  # View logs
```

## Requirements

- Python 3.8+
- CUDA GPU (recommended)
- 8GB+ RAM

## API Compatibility

Fully compatible with OpenAI's `/v1/chat/completions` endpoint:
- ✅ Text-only conversations (`modalities: ["text"]`)
- ✅ Text-to-speech (`modalities: ["text", "audio"]`)
- ✅ Voice cloning (reference audio in `audio.data`)
- ✅ Audio input processing (`input_audio` type in messages)
- ✅ Combined audio input + voice cloning output
