# Voice Cloning Implementation Plan

## 🎯 **Objective**
Add voice cloning capability to the simplified audio service while maintaining the clean, single-process architecture.

## 📋 **Current Status**
- ✅ Git repository initialized with initial commit (95441cf)
- ✅ Basic TTS/STT functionality working
- ✅ OpenAI Chat Completions API compatibility
- ❌ Voice cloning not implemented yet

## 🔍 **Technical Analysis**

### What We Have
- **Higgs Audio Model**: Supports in-context voice cloning (confirmed in `boson_multimodal/model/higgs_audio/utils.py`)
- **Audio Processing**: Can handle input audio and convert to tokens
- **Multimodal Input**: Already processes `input_audio` in messages
- **Base64 Audio Handling**: Working for both input and output

### What's Missing
- **Voice Reference Extraction**: Extract voice sample from input audio
- **ChatML Voice Integration**: Include voice reference in ChatML sample for generation
- **Audio Tokenization**: Convert voice reference audio to tokens for the model
- **Generation Configuration**: Pass voice tokens to the generation process

## 🛠️ **Implementation Plan**

### Phase 1: Voice Reference Processing (Est: 2-3 hours)

#### 1.1 Add Voice Reference Extraction
```python
def extract_voice_reference(audio_bytes: bytes) -> Optional[torch.Tensor]:
    """Extract voice reference tokens from audio bytes"""
    # Convert audio to format expected by Higgs Audio Tokenizer
    # Return audio tokens for voice cloning
```

#### 1.2 Modify Message Processing
- Update `chat_completions()` endpoint to detect voice cloning requests
- Extract voice reference audio when present in multimodal messages
- Store voice reference for use in TTS generation

#### 1.3 Update Text-to-Speech Function
```python
def text_to_speech(text: str, voice_reference: Optional[torch.Tensor] = None) -> bytes:
    """Convert text to speech with optional voice cloning"""
    # Include voice reference in ChatML sample if provided
    # Configure generation to use voice cloning
```

### Phase 2: ChatML Integration (Est: 1-2 hours)

#### 2.1 Voice-Aware ChatML Construction
- Modify ChatML sample creation to include voice reference audio tokens
- Follow the in-context voice cloning pattern from original service
- Ensure proper token positioning for voice cloning

#### 2.2 Generation Configuration
- Update generation parameters to enable voice cloning mode
- Configure audio tokenizer to use voice reference
- Set appropriate generation flags for voice cloning

### Phase 3: API Enhancement (Est: 1 hour)

#### 3.1 OpenAI API Extension
Support voice cloning through OpenAI-compatible API:
```json
{
  "model": "gpt-4o-audio-preview",
  "modalities": ["text", "audio"],
  "audio": {"voice": "clone", "format": "wav"},
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text", 
          "text": "Say this in my voice: Hello world"
        },
        {
          "type": "input_audio",
          "input_audio": {"data": "base64_voice_sample", "format": "wav"}
        }
      ]
    }
  ]
}
```

#### 3.2 Voice Detection Logic
- Detect when `audio.voice` is set to "clone"
- Automatically use input audio as voice reference
- Fallback to default voice if no reference provided

### Phase 4: Testing & Validation (Est: 1 hour)

#### 4.1 Test Cases
- Voice cloning with different audio samples
- Fallback to default voice when cloning fails
- Quality comparison between cloned and default voices
- Performance impact measurement

#### 4.2 Error Handling
- Graceful degradation when voice cloning fails
- Clear error messages for invalid voice references
- Maintain service stability

## 📁 **File Changes Required**

### Core Files to Modify
1. **`app.py`** (Main changes)
   - Update `chat_completions()` endpoint
   - Modify `text_to_speech()` function
   - Add voice reference extraction logic

2. **`requirements.txt`** (If needed)
   - Add any additional dependencies

3. **`README.md`** 
   - Document voice cloning API usage
   - Add examples and limitations

### New Files to Create
1. **`voice_cloning.py`** (Optional)
   - Separate module for voice cloning logic
   - Keep main app.py clean and focused

2. **`test_voice_cloning.py`**
   - Comprehensive test suite for voice cloning
   - Performance benchmarks

## 🎯 **Implementation Strategy**

### Approach: Incremental & Safe
1. **Branch Creation**: Create `feature/voice-cloning` branch
2. **Incremental Commits**: Small, testable changes
3. **Backward Compatibility**: Ensure existing functionality remains unchanged
4. **Testing**: Test each phase before proceeding
5. **Documentation**: Update docs as features are added

### Key Principles
- **Keep It Simple**: Maintain the simplified architecture
- **Fail Fast**: Clear errors when voice cloning fails
- **No Complexity**: Avoid multiprocessing or complex abstractions
- **OpenAI Compatible**: Extend existing API, don't break it

## 📊 **Expected Outcomes**

### After Implementation
- ✅ Voice cloning from input audio samples
- ✅ OpenAI API compatibility maintained
- ✅ Graceful fallback to default voice
- ✅ Clean, maintainable code (~150 lines total)
- ✅ Single-process architecture preserved

### Performance Expectations
- **Memory**: Slight increase (~0.5-1GB) for voice processing
- **Latency**: Additional 1-2 seconds for voice cloning
- **Quality**: High-quality voice cloning using Higgs Audio capabilities

## 🚀 **Getting Started**

### Next Steps
1. Create feature branch: `git checkout -b feature/voice-cloning`
2. Start with Phase 1.1: Voice reference extraction
3. Test incrementally with `/test_audio.wav`
4. Commit small, working changes
5. Document API usage as you go

### Success Criteria
- [ ] Can clone voice from `/test_audio.wav`
- [ ] Maintains OpenAI API compatibility
- [ ] Graceful error handling
- [ ] No regression in existing functionality
- [ ] Clean, readable code

---

**Estimated Total Time**: 5-7 hours
**Complexity**: Medium (leveraging existing model capabilities)
**Risk**: Low (incremental approach with fallbacks)
