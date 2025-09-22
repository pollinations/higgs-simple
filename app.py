
import os
import base64
import tempfile
import logging
import io
import time
import requests
from typing import Optional, List, Dict, Any
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Required imports - fail fast if not available
from boson_multimodal.serve.serve_engine import HiggsAudioServeEngine
from boson_multimodal.data_types import ChatMLSample, Message, AudioContent
import whisper
import torch
import torchaudio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global model instances
tts_model = None
stt_model = None

def load_models():
    """Load models - fail fast if any dependency is missing"""
    global tts_model, stt_model
    
    logger.info("Loading TTS model...")
    tts_model = HiggsAudioServeEngine(
        "bosonai/higgs-audio-v2-generation-3B-base", 
        "bosonai/higgs-audio-v2-tokenizer"
    )
    logger.info("TTS model loaded successfully")
    
    logger.info("Loading STT model...")
    stt_model = whisper.load_model("small")
    logger.info("STT model loaded successfully")

def decode_base64_audio(b64_string: str) -> bytes:
    """Decode base64 audio data"""
    try:
        # Remove data URL prefix if present
        if b64_string.startswith('data:audio'):
            b64_string = b64_string.split(',')[1]
        
        # Fix padding if needed
        missing_padding = len(b64_string) % 4
        if missing_padding:
            b64_string += '=' * (4 - missing_padding)
        
        return base64.b64decode(b64_string)
    except Exception as e:
        raise ValueError(f"Invalid base64 audio data: {e}")

def text_to_speech(text: str, voice: str = "alloy", voice_reference_audio: Optional[bytes] = None) -> bytes:
    """Convert text to speech with specified voice or voice cloning"""
    try:
        # Voice-specific system prompts to simulate different voices
        voice_prompts = {
            "alloy": (
                "You are a voice synthesis engine. Speak the user's text naturally and expressively. "
                "Generate audio following instruction.\n"
                "<|scene_desc_start|>\n"
                "Speak with natural conversational warmth and genuine human connection. "
                "Use a balanced, expressive voice with organic pacing and authentic emotional undertones.\n"
                "<|scene_desc_end|>"
            ),
            "echo": (
                "You are a voice synthesis engine. Speak the user's text naturally and expressively. "
                "Generate audio following instruction.\n"
                "<|scene_desc_start|>\n"
                "Speak with a clear, resonant voice that has depth and authority. "
                "Use confident pacing with strong articulation and professional tone.\n"
                "<|scene_desc_end|>"
            ),
            "fable": (
                "You are a voice synthesis engine. Speak the user's text naturally and expressively. "
                "Generate audio following instruction.\n"
                "<|scene_desc_start|>\n"
                "Speak with a storytelling voice that is engaging and narrative. "
                "Use expressive intonation with dramatic pauses and captivating delivery.\n"
                "<|scene_desc_end|>"
            ),
            "onyx": (
                "You are a voice synthesis engine. Speak the user's text naturally and expressively. "
                "Generate audio following instruction.\n"
                "<|scene_desc_start|>\n"
                "Speak with a deep, rich voice that conveys strength and reliability. "
                "Use steady pacing with authoritative tone and grounded delivery.\n"
                "<|scene_desc_end|>"
            ),
            "nova": (
                "You are a voice synthesis engine. Speak the user's text naturally and expressively. "
                "Generate audio following instruction.\n"
                "<|scene_desc_start|>\n"
                "Speak with a bright, energetic voice that is youthful and dynamic. "
                "Use lively pacing with enthusiastic tone and vibrant delivery.\n"
                "<|scene_desc_end|>"
            ),
            "shimmer": (
                "You are a voice synthesis engine. Speak the user's text naturally and expressively. "
                "Generate audio following instruction.\n"
                "<|scene_desc_start|>\n"
                "Speak with a gentle, melodic voice that is soothing and harmonious. "
                "Use flowing pacing with soft tone and graceful delivery.\n"
                "<|scene_desc_end|>"
            )
        }
        
        # Handle voice cloning if reference audio is provided
        if voice_reference_audio:
            logger.info(f"Using voice cloning with {len(voice_reference_audio)} bytes of reference audio")
            
            # Convert reference audio to base64
            reference_audio_b64 = base64.b64encode(voice_reference_audio).decode('utf-8')
            
            # Create voice cloning system prompt
            system_prompt = (
                "Generate audio following instruction.\n"
                "<|scene_desc_start|>\n"
                "Clone the voice characteristics from the provided reference audio. "
                "Match the speaker's tone, accent, speaking style, and vocal qualities. "
                "Maintain natural expression while preserving the unique voice identity.\n"
                "<|scene_desc_end|>"
            )
            
            # Create messages following the correct voice cloning pattern
            messages = [
                Message(role="system", content=system_prompt),
                Message(role="user", content="Please clone this voice."),
                Message(role="assistant", content=[AudioContent(raw_audio=reference_audio_b64, audio_url="")]),
                Message(role="user", content=text)
            ]
        else:
            # Use the specified voice prompt, fallback to alloy if voice not found
            system_prompt = voice_prompts.get(voice, voice_prompts["alloy"])
            logger.info(f"Generating TTS with voice: {voice}")
            
            messages = [
                Message(role="system", content=system_prompt),
                Message(role="user", content=text)
            ]
        
        # Create chat template
        chat_template = ChatMLSample(messages=messages)
        
        # Generate audio
        response = tts_model.generate(
            chat_ml_sample=chat_template,
            max_new_tokens=1024,
            temperature=0.7,
            force_audio_gen=True,
            top_k=50,
            top_p=0.95
        )
        
        if response.audio is None:
            raise RuntimeError("No audio generated by model")
        
        # Convert to WAV bytes
        audio_tensor = torch.from_numpy(response.audio).unsqueeze(0)
        sample_rate = getattr(response, 'sampling_rate', 24000)
        
        buffer = io.BytesIO()
        torchaudio.save(buffer, audio_tensor, sample_rate, format="WAV")
        audio_bytes = buffer.getvalue()
        
        logger.info(f"Generated audio: {len(audio_bytes)} bytes at {sample_rate}Hz")
        return audio_bytes
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise RuntimeError(f"Text-to-speech failed: {e}")

def generate_text_response(messages: List[Dict[str, Any]]) -> str:
    """Generate intelligent text response using Pollinations AI"""
    try:
        # Prepare the request for Pollinations API
        pollinations_url = "https://text.pollinations.ai/openai"
        
        payload = {
            "model": "openai",
            "messages": messages,
            "max_tokens": 1000
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        logger.info(f"Sending request to Pollinations AI with {len(messages)} messages")
        
        # Make request to Pollinations API
        response = requests.post(
            pollinations_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the generated text
            if "choices" in result and len(result["choices"]) > 0:
                generated_text = result["choices"][0].get("message", {}).get("content", "")
                if generated_text:
                    logger.info(f"Generated text response: {len(generated_text)} characters")
                    return generated_text.strip()
            
            logger.warning("No content in Pollinations API response")
            return "I apologize, but I couldn't generate a proper response at the moment."
            
        else:
            logger.error(f"Pollinations API error: {response.status_code} - {response.text}")
            return "I'm having trouble generating a response right now. Please try again."
            
    except requests.exceptions.Timeout:
        logger.error("Pollinations API request timed out")
        return "I'm taking too long to respond. Please try again."
    except requests.exceptions.ConnectionError:
        logger.error("Could not connect to Pollinations API")
        return "I'm having connectivity issues. Please try again later."
    except Exception as e:
        logger.error(f"Text generation error: {e}")
        return "I encountered an error while generating a response. Please try again."

def speech_to_text(audio_bytes: bytes) -> str:
    """Convert speech to text"""
    try:
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_audio_path = temp_file.name
        
        try:
            # Transcribe audio
            result = stt_model.transcribe(temp_audio_path)
            transcription = result["text"].strip()
            logger.info(f"Transcribed: {transcription}")
            return transcription
        finally:
            # Clean up temp file
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
                
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise RuntimeError(f"Speech-to-text failed: {e}")

@app.route("/health", methods=["GET"])
def health():
    """Health endpoint"""
    return jsonify({"status": "ok"})

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """OpenAI Chat Completions API compatible endpoint with multimodal audio support"""
    try:
        data = request.get_json(force=True)
        
        # Extract parameters
        messages = data.get("messages", [])
        model = data.get("model", "gpt-4o-audio-preview")
        modalities = data.get("modalities", ["text"])
        audio_config = data.get("audio", {})
        
        if not messages:
            return jsonify({"error": {"message": "Missing required 'messages' parameter", "type": "invalid_request_error"}}), 400
        
        # Process the conversation and prepare messages for text generation
        processed_messages = []
        
        # Process all messages for context
        for msg in messages:
            processed_msg = {"role": msg.get("role", "user"), "content": ""}
            
            content = msg.get("content")
            if isinstance(content, str):
                # Simple text content
                processed_msg["content"] = content
            elif isinstance(content, list):
                # Multimodal content - extract text and transcribe audio
                content_parts = []
                
                for item in content:
                    if item.get("type") == "text":
                        content_parts.append(item.get("text", ""))
                    elif item.get("type") == "input_audio":
                        # Handle audio input by transcribing it
                        audio_data = item.get("input_audio", {}).get("data")
                        if audio_data:
                            try:
                                audio_bytes = base64.b64decode(audio_data)
                                transcription = speech_to_text(audio_bytes)
                                content_parts.append(transcription)
                                logger.info(f"Transcribed audio: {transcription}")
                            except Exception as e:
                                logger.error(f"Audio processing error: {e}")
                                content_parts.append("[Audio could not be processed]")
                
                processed_msg["content"] = " ".join(content_parts)
            
            if processed_msg["content"].strip():
                processed_messages.append(processed_msg)
        
        # Generate intelligent text response using Pollinations AI
        response_text = generate_text_response(processed_messages)
        
        # Generate response
        response_message = {
            "role": "assistant",
            "content": response_text
        }
        
        # Generate audio if requested
        if "audio" in modalities:
            try:
                # Extract voice and voice cloning data from audio config
                voice = audio_config.get("voice", "alloy")
                voice_reference_audio = None
                
                # Check if voice cloning data is provided in audio.data
                if "data" in audio_config:
                    try:
                        voice_reference_audio = decode_base64_audio(audio_config["data"])
                        logger.info(f"Voice cloning requested with {len(voice_reference_audio)} bytes of reference audio")
                    except Exception as e:
                        logger.error(f"Failed to decode voice reference audio: {e}")
                        # Continue with default voice if reference audio is invalid
                
                # Generate audio with optional voice cloning
                audio_bytes = text_to_speech(response_text, voice=voice, voice_reference_audio=voice_reference_audio)
                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                response_message["audio"] = {
                    "data": audio_b64,
                    "format": audio_config.get("format", "wav")
                }
            except Exception as e:
                logger.error(f"Audio generation error: {e}")
                # Continue without audio if generation fails
        
        # Return OpenAI-compatible response
        return jsonify({
            "id": f"chatcmpl-{os.urandom(16).hex()}",
            "object": "chat.completion",
            "created": int(os.path.getmtime(__file__)),
            "model": model,
            "choices": [{
                "index": 0,
                "message": response_message,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(str(processed_messages)),
                "completion_tokens": len(response_text),
                "total_tokens": len(str(processed_messages)) + len(response_text)
            }
        })
            
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        return jsonify({"error": {"message": str(e), "type": "server_error"}}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info("Starting Simple Audio Service...")
    
    # Load models on startup
    load_models()
    
    # Start server
    host = "0.0.0.0"
    port = 8000
    logger.info(f"Server starting on {host}:{port}")
    
    app.run(host=host, port=port, debug=False, threaded=True)
