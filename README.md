# Simple Audio Service

A streamlined audio processing service that provides OpenAI Chat Completions API compatibility with multimodal audio support. This service eliminates complexity while maintaining core functionality for text-to-speech (TTS) and speech-to-text (STT) capabilities.

## Philosophy

This service follows the principle of **radical simplification**:
- **No conditional logic**: Either all dependencies work or the service fails to start
- **No graceful degradation**: Don't handle missing dependencies - require them
- **Fail fast**: Clear error messages on startup if anything is missing
- **Direct calls**: No queues, processes, or service abstractions
- **Single process**: Everything runs in one process
- **OpenAI Compatible**: Drop-in replacement for OpenAI's Chat Completions API with audio

## Features

- **OpenAI Chat Completions API Compatible**: Use with existing OpenAI client libraries
- **Multimodal Audio Support**: Text and audio input/output like `gpt-4o-audio-preview`
- **Text-to-Speech**: Convert text to natural-sounding speech
- **Speech-to-Text**: Transcribe audio to text using Whisper
- **Simple Architecture**: Clean, straightforward implementation

## Architecture

```
Request → Flask → Direct Model Call → Response
```

Instead of the complex original:
```
Request → Flask → Queue → Worker → Model Server → Queue → Cache Worker → Response
```

## Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- ~2-4GB RAM (vs 14GB+ in the original complex system)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd simple-audio-service
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install boson-multimodal  # Required for TTS
   ```

3. **Run the service:**
   ```bash
   python app.py
   ```

The service will start on `http://localhost:8000` and fail immediately if any required dependencies are missing.

## API Endpoints

### Health Check
```http
GET /health
```

Returns service health status.

### Chat Completions (OpenAI Compatible)
```http
POST /v1/chat/completions
```

**Parameters:**
- `messages` (required): Array of message objects
- `model` (optional): Model name (ignored, we use our fixed model)
- `modalities` (optional): Array of modalities, e.g., `["text", "audio"]`
- `audio` (optional): Audio configuration object

**Examples:**

**Text-only Chat:**
```json
{
  "model": "gpt-4o-audio-preview",
  "modalities": ["text"],
  "messages": [
    {
      "role": "user",
      "content": "Hello, can you tell me about golden retrievers?"
    }
  ]
}
```

**Text Input with Audio Output:**
```json
{
  "model": "gpt-4o-audio-preview",
  "modalities": ["text", "audio"],
  "audio": {"voice": "alloy", "format": "wav"},
  "messages": [
    {
      "role": "user",
      "content": "Please tell me a joke about programming."
    }
  ]
}
```

**Audio Input Processing:**
```json
{
  "model": "gpt-4o-audio-preview",
  "modalities": ["text", "audio"],
  "audio": {"voice": "alloy", "format": "wav"},
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What is in this recording?"},
        {"type": "input_audio", "input_audio": {"data": "<base64-audio>", "format": "wav"}}
      ]
    }
  ]
}
```

## Using with OpenAI Client Libraries

You can use this service as a drop-in replacement for OpenAI's API:

**Python:**
```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # We don't require API keys
)

response = client.chat.completions.create(
    model="gpt-4o-audio-preview",
    modalities=["text", "audio"],
    audio={"voice": "alloy", "format": "wav"},
    messages=[
        {"role": "user", "content": "Tell me a joke"}
    ]
)
```

**JavaScript/Node.js:**
```javascript
import OpenAI from 'openai';

const openai = new OpenAI({
    baseURL: 'http://localhost:8000/v1',
    apiKey: 'not-needed'
});

const response = await openai.chat.completions.create({
    model: 'gpt-4o-audio-preview',
    modalities: ['text', 'audio'],
    audio: { voice: 'alloy', format: 'wav' },
    messages: [
        { role: 'user', content: 'Tell me a joke' }
    ]
});
```

## Testing

Run the test client to verify functionality:

```bash
python test_client.py
```

This will test all endpoints and save audio files for verification.

## Comparison with Original System

| Aspect | Original Complex System | Simple Service |
|--------|------------------------|----------------|
| Memory Usage | 14GB+ | 2-4GB |
| Processes | Multiple (multiprocessing) | Single |
| Architecture | Queue-based with workers | Direct function calls |
| Error Handling | Complex, often silent failures | Simple, fail-fast |
| Dependencies | Many unnecessary packages | Essential only |
| Startup Time | Slow (process coordination) | Fast |
| Debugging | Difficult (cross-process) | Easy (single process) |
| API Compatibility | Custom endpoints | OpenAI Chat Completions API |
| Client Integration | Custom client code needed | Use existing OpenAI libraries |

## Configuration

The service uses minimal configuration:
- Host: `0.0.0.0` (configurable in code)
- Port: `8000` (configurable in code)
- Models: Fixed to proven, working models

## Troubleshooting

Simple, direct error handling:
- Invalid input data returns 400 with clear error message
- Processing failures return 500 with error details
- All errors are logged for debugging

## Limitations

- No caching (generates fresh audio each time)
- No external API integration for advanced features
- Simplified intent detection (keyword-based)
- No complex voice processing pipelines

## Future Enhancements (Optional)

If needed, these can be added back selectively:
- Simple file-based caching
- More sophisticated intent detection
- Additional audio format support
- Rate limiting
- Authentication

## Deployment

For production deployment:
1. Use a production WSGI server (gunicorn, uwsgi)
2. Add environment-based configuration
3. Implement proper logging
4. Add health checks and monitoring
5. Consider containerization with Docker

This simplified service provides the same core functionality as the original system while being much more maintainable, reliable, and resource-efficient.
