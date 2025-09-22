#!/usr/bin/env python3
"""
Test client for the Simple Audio Service - OpenAI Chat Completions API compatible
"""

import requests
import base64
import json
import os

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_text_only_chat():
    """Test text-only chat completion"""
    print("Testing text-only chat completion...")
    
    data = {
        "model": "gpt-4o-audio-preview",
        "modalities": ["text"],
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you tell me about golden retrievers?"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_text_with_audio_output():
    """Test text input with audio output"""
    print("Testing text input with audio output...")
    
    data = {
        "model": "gpt-4o-audio-preview",
        "modalities": ["text", "audio"],
        "audio": {"voice": "alloy", "format": "wav"},
        "messages": [
            {
                "role": "user",
                "content": "Please tell me a short joke about programming."
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Text response: {result['choices'][0]['message']['content']}")
        
        # Save audio if present
        if 'audio' in result['choices'][0]['message']:
            audio_data = result['choices'][0]['message']['audio']['data']
            audio_bytes = base64.b64decode(audio_data)
            with open("chat_response.wav", "wb") as f:
                f.write(audio_bytes)
            print("Audio response saved to chat_response.wav")
    else:
        print(f"Error: {response.json()}")
    print()

def test_audio_input():
    """Test audio input processing"""
    print("Testing audio input processing...")
    
    # First create a test audio file if it doesn't exist
    if not os.path.exists("chat_response.wav"):
        print("Creating test audio first...")
        test_text_with_audio_output()
    
    # Read audio file and encode as base64
    with open("chat_response.wav", "rb") as f:
        audio_data = f.read()
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    
    data = {
        "model": "gpt-4o-audio-preview",
        "modalities": ["text", "audio"],
        "audio": {"voice": "alloy", "format": "wav"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in this audio recording?"},
                    {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "wav"}}
                ]
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Text response: {result['choices'][0]['message']['content']}")
        
        # Save audio response if present
        if 'audio' in result['choices'][0]['message']:
            audio_data = result['choices'][0]['message']['audio']['data']
            audio_bytes = base64.b64decode(audio_data)
            with open("audio_analysis_response.wav", "wb") as f:
                f.write(audio_bytes)
            print("Audio response saved to audio_analysis_response.wav")
    else:
        print(f"Error: {response.json()}")
    print()

if __name__ == "__main__":
    print("Simple Audio Service Test Client")
    print("OpenAI Chat Completions API Compatible")
    print("=" * 50)
    
    try:
        test_health()
        test_text_only_chat()
        # test_text_with_audio_output()
        # test_audio_input()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the service. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")
