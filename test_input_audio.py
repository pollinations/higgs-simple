#!/usr/bin/env python3

import requests
import base64
import json
import sys
import os

def test_input_audio_functionality():
    """Test the new input_audio functionality with OpenAI format"""
    print("🎤 Testing Input Audio Functionality")
    print("=" * 50)
    
    # Check if service is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Service health check failed")
            return False
        print("✅ Service is running")
    except Exception as e:
        print(f"❌ Cannot connect to service: {e}")
        return False
    
    # Create a simple test audio file (you can replace this with actual audio)
    print("\n📝 Note: This test uses a placeholder for audio data.")
    print("In a real test, you would provide actual base64-encoded audio.")
    
    # Test payload matching your curl example format
    payload = {
        "model": "gpt-4o-audio-preview",
        "modalities": ["text", "audio"],
        "audio": { 
            "voice": "alloy", 
            "format": "wav" 
        },
        "messages": [
            {
                "role": "user",
                "content": [
                    { 
                        "type": "text", 
                        "text": "What is in this recording?" 
                    },
                    { 
                        "type": "input_audio", 
                        "input_audio": { 
                            "data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",  # Minimal WAV header
                            "format": "wav" 
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        print("\n📤 Sending test request...")
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print("✅ Request completed successfully")
        
        # Parse response
        data = response.json()
        message = data['choices'][0]['message']
        
        print(f"📝 Text Response: {message['content']}")
        
        if 'audio' in message:
            print("🎵 Audio generated successfully!")
            audio_format = message['audio']['format']
            audio_data_length = len(message['audio']['data'])
            print(f"📊 Audio format: {audio_format}")
            print(f"📊 Audio data length: {audio_data_length} characters (base64)")
            
            # Save audio to file
            audio_bytes = base64.b64decode(message['audio']['data'])
            os.makedirs("outputs", exist_ok=True)
            output_file = f"outputs/input_audio_test.{audio_format}"
            with open(output_file, 'wb') as af:
                af.write(audio_bytes)
            print(f"💾 Audio saved to {output_file}")
            print(f"📊 Audio file size: {len(audio_bytes)} bytes")
            
            return True
        else:
            print("❌ No audio data found in response")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_voice_cloning_with_input_audio():
    """Test combining voice cloning with input audio"""
    print("\n🎭 Testing Voice Cloning + Input Audio")
    print("=" * 50)
    
    # This would test both voice cloning AND input audio together
    payload = {
        "model": "gpt-4o-audio-preview",
        "modalities": ["text", "audio"],
        "audio": { 
            "data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",  # Voice to clone
            "format": "wav" 
        },
        "messages": [
            {
                "role": "user",
                "content": [
                    { 
                        "type": "text", 
                        "text": "Please respond to what I said in the recording using the cloned voice." 
                    },
                    { 
                        "type": "input_audio", 
                        "input_audio": { 
                            "data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",  # Input audio
                            "format": "wav" 
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        print("📤 Sending combined test request...")
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Combined functionality works!")
            data = response.json()
            message = data['choices'][0]['message']
            print(f"📝 Response: {message['content'][:100]}...")
            if 'audio' in message:
                print("🎵 Audio with cloned voice generated!")
            return True
        else:
            print(f"❌ Combined test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Combined test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple Audio Service - Input Audio Test Suite")
    print("=" * 60)
    
    # Test 1: Basic input audio functionality
    success1 = test_input_audio_functionality()
    
    # Test 2: Combined voice cloning + input audio
    success2 = test_voice_cloning_with_input_audio()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All tests passed! Input audio functionality is working correctly.")
        print("✅ The service now supports the OpenAI input_audio format.")
    else:
        print("❌ Some tests failed. Check the service implementation.")
        sys.exit(1)
