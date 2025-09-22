#!/usr/bin/env python3

import requests
import base64
import json
import sys
import argparse
import os

def test_voice_cloning(voice_file_path, text_to_say):
    print("🎤 Voice Cloning Test")
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
    
    # Load and encode voice file
    try:
        if not os.path.exists(voice_file_path):
            print(f"❌ Voice file not found: {voice_file_path}")
            return False
            
        with open(voice_file_path, "rb") as f:
            voice_data = f.read()
        voice_base64 = base64.b64encode(voice_data).decode('utf-8')
        voice_filename = os.path.basename(voice_file_path)
        print(f"✅ Loaded voice file '{voice_filename}': {len(voice_data)} bytes")
        print(f"✅ Base64 encoded: {len(voice_base64)} characters")
    except Exception as e:
        print(f"❌ Failed to load voice file: {e}")
        return False
    
    # Test voice cloning
    print("\n🧪 Testing voice cloning...")
    payload = {
        "model": "gpt-4o-audio-preview",
        "modalities": ["text", "audio"],
        "audio": {
            "data": voice_base64,
            "format": "wav"
        },
        "messages": [
            {
                "role": "user",
                "content": f"Please say exactly: {text_to_say}"
            }
        ]
    }
    
    try:
        print("📤 Sending request...")
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
        
        print(f"📝 Text Response: {message['content'][:100]}...")
        
        if 'audio' in message:
            print("🎵 Audio generated successfully!")
            audio_data = message['audio']['data']
            audio_format = message['audio']['format']
            print(f"📊 Audio format: {audio_format}")
            print(f"📊 Audio data length: {len(audio_data)} characters (base64)")
            
            # Save audio to file
            audio_bytes = base64.b64decode(audio_data)
            voice_name = os.path.splitext(os.path.basename(voice_file_path))[0]
            output_file = f"{voice_name}_clone_test.{audio_format}"
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test voice cloning with custom voice file and text")
    parser.add_argument("voice_file", help="Path to the voice file to clone (e.g., /thomash_voice.mp3)")
    parser.add_argument("text", help="Text to say in the cloned voice")
    
    args = parser.parse_args()
    
    print(f"🎯 Voice file: {args.voice_file}")
    print(f"💬 Text to say: '{args.text}'")
    print()
    
    success = test_voice_cloning(args.voice_file, args.text)
    if success:
        voice_name = os.path.splitext(os.path.basename(args.voice_file))[0]
        print(f"\n🎉 Voice cloning test completed successfully!")
        print(f"🎧 You can now play the generated audio file to hear {voice_name}'s cloned voice!")
    else:
        print("\n❌ Voice cloning test failed.")
        sys.exit(1)
