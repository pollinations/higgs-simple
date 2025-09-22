"""
Configuration settings for the Simple Audio Service
"""

import os

# Model Configuration
TTS_MODEL_PATH = "bosonai/higgs-audio-v2-generation-3B-base"
TTS_TOKENIZER_PATH = "bosonai/higgs-audio-v2-tokenizer"
STT_MODEL_SIZE = "small"  # whisper model size: tiny, base, small, medium, large

# Audio Configuration
SAMPLE_RATE = 24000
MAX_AUDIO_DURATION = 60  # seconds
MAX_FILE_SIZE_MB = 10

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000
DEBUG = False

# Generation Parameters
TTS_TEMPERATURE = 0.7
TTS_TOP_K = 50
TTS_TOP_P = 0.95
TTS_MAX_TOKENS = 1024

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Environment Variables (optional overrides)
HOST = os.getenv("HOST", HOST)
PORT = int(os.getenv("PORT", PORT))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", LOG_LEVEL)
