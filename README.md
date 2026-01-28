# Whisper Dictation - Local Voice Dictation Tool

A minimalist local voice-to-text dictation tool for Windows. Press Alt+W to record audio, and your speech is transcribed, cleaned, and automatically pasted at your cursor position.

## Features

- **🎤 Local Processing**: Audio is transcribed locally using OpenAI's Whisper model (small, CPU-only)
- **🧹 Smart Cleanup**: Text is automatically corrected using OpenAI API (GPT-4o-mini) to remove filler words and fix grammar
- **⌨️ Global Hotkey**: Alt+W toggle to start/stop recording from anywhere
- **🎯 Minimal GUI**: Simple feedback window shows recording and processing states
- **💻 Cross-App Paste**: Works in any Windows application (VS Code, Notepad, browsers, etc.)
- **🇫🇷 French Optimized**: Whisper model forced to French transcription with context-aware cleaning

## Prerequisites

- **Python 3.11.5+** (Python 3.11.5 recommended, as it is the tested version)
- **Microphone**: Any working microphone supported by your system
- **Windows 10+**: Currently Windows-only (pynput and sounddevice are cross-platform, but testing is Windows-only)
- **Internet Connection**: Required for:
  - Whisper model download on first run (~460 MB)
  - OpenAI API calls for text cleaning (optional fallback if unavailable)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd whisper-dictation
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# or on PowerShell: .\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For development (running tests):

```bash
pip install -r requirements-dev.txt
```

### 4. Set Up API Key

1. Copy the example environment file:

```bash
copy .env.example .env
```

2. Open `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your_actual_api_key_here
```

Get your API key from: https://platform.openai.com/api-keys

**Important:** Keep your `.env` file secret. It is already in `.gitignore` and will not be committed.

## Usage

### Starting the Application

```bash
python -m src.main
```

Or directly:

```bash
python src/main.py
```

The application will:
1. Initialize all modules
2. Start listening for the Alt+W hotkey
3. Hide the GUI window (shown only during recording/processing)

### Recording and Dictating

1. **Press Alt+W** to start recording
   - Microphone indicator appears: **🎤 Écoute...**
   - Start speaking in French

2. **Press Alt+W again** to stop recording
   - Processing indicator appears: **⏳ Traitement...**
   - Audio is transcribed locally
   - Text is cleaned via OpenAI API
   - Cleaned text is automatically pasted at cursor

3. **Done!** The window hides and app returns to IDLE, ready for next recording

### Troubleshooting

#### "OPENAI_API_KEY not found in environment"

**Cause:** The `.env` file is missing or doesn't have OPENAI_API_KEY set.

**Solution:**
1. Create `.env` file from `.env.example`
2. Add your valid OpenAI API key
3. Restart the application

#### "GUI window doesn't appear"

**Cause:** The window only appears during recording/processing. It's hidden in IDLE state.

**Solution:** Press Alt+W to start recording and the window should appear.

#### "Microphone not detected"

**Cause:** Microphone is not available or not properly detected.

**Solution:**
1. Check Windows sound settings
2. Verify microphone is connected
3. Check if another application is using the microphone
4. Restart the application

#### "Recording too short" error

**Cause:** You released Alt+W too quickly (less than 0.5 seconds of audio).

**Solution:** Press and hold Alt+W for at least half a second while speaking.

#### "Enregistrement trop long" (Recording too long)

**Cause:** Recording exceeded 5 minutes (300 seconds).

**Solution:** Release Alt+W to stop recording earlier, or modify `MAX_RECORDING_SECONDS` in `src/config.py`.

#### "No text pasted after recording"

**Cause:** Transcription resulted in empty/no speech detected.

**Solutions:**
1. Record in a quieter environment (high background noise interferes)
2. Speak louder and more clearly
3. Check microphone levels in Windows sound settings

#### API Fails - Text Not Cleaned

**Behavior:** If OpenAI API fails (timeout, rate limit, invalid key), the app falls back to raw transcribed text without cleaning.

**Solution:** Check API key validity and OpenAI account balance.

#### "Whisper model download" hangs

**Cause:** First-time model download is taking time. Model size: ~460 MB.

**Solution:** This is normal. Let the app download the model (5-15 minutes depending on internet speed). You should see "📥 Téléchargement..." in the GUI.

## Architecture

### State Machine

The application uses a simple state machine:

```
IDLE
  ├─→ (Alt+W pressed) → LISTENING
       ├─→ (Alt+W pressed) → PROCESSING
            └─→ (done) → IDLE
```

**IDLE**: No recording, GUI hidden, listening for hotkey
**LISTENING**: Recording audio, GUI shows 🎤 Écoute...
**PROCESSING**: Transcribing and cleaning, GUI shows ⏳ Traitement...

### Module Architecture

```
┌─────────────────────────────────────────────┐
│        WhisperDictationApp (main.py)        │
│  Orchestrates state machine and modules    │
└─────────────────────────────────────────────┘
        ↓         ↓         ↓         ↓
    ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
    │ Audio  │ │Hotkey  │ │ GUI    │ │Clipboard │
    │Capture │ │Manager │ │Feedback│ │ Manager  │
    └────────┘ └────────┘ └────────┘ └──────────┘
        ↓                                  ↓
   ┌──────────────┐            ┌──────────────────┐
   │Transcriber   │            │ Text Cleaner     │
   │(Whisper)     │            │ (OpenAI API)     │
   └──────────────┘            └──────────────────┘
```

### Module Responsibilities

- **audio_capture.py**: Records microphone audio at 16kHz mono
- **transcription.py**: Converts audio to text using faster-whisper (small model, French)
- **text_cleaner.py**: Cleans text via OpenAI API with fallback to raw text
- **clipboard_manager.py**: Copies text to clipboard and simulates Ctrl+V
- **gui_feedback.py**: Displays status window (listening, processing, errors)
- **hotkey_manager.py**: Listens for global Alt+W hotkey with debouncing
- **config.py**: Centralized configuration and logging setup
- **main.py**: State machine orchestration and module coordination

## Testing

### Running All Tests

```bash
pytest
```

### Running Specific Test File

```bash
pytest tests/test_audio_capture.py -v
```

### Running with Coverage

```bash
pytest --cov=src --cov-report=html
```

Test coverage is tracked in `htmlcov/index.html`.

### Test Strategy

- **Unit Tests Only**: Each module is tested in isolation using mocks
- **No GUI Tests**: tkinter GUI is validated manually (too complex to automate)
- **Mocked Dependencies**: All external libraries (sounddevice, Whisper, OpenAI, pynput) are mocked
- **Coverage Target**: 80%+ for core modules

### Test Files

- `tests/test_audio_capture.py` - Audio recording and buffer management
- `tests/test_transcription.py` - Whisper model integration
- `tests/test_text_cleaner.py` - OpenAI API integration with fallback
- `tests/test_clipboard_manager.py` - Paste simulation
- `tests/test_hotkey_manager.py` - Global hotkey registration and debouncing

## Configuration

### Environment Variables (.env)

```
# Required
OPENAI_API_KEY=sk-your_key_here

# Optional (defaults shown)
WHISPER_MODEL=small
WHISPER_LANGUAGE=fr
SAMPLE_RATE=16000
HOTKEY=<alt>+w
MAX_RECORDING_SECONDS=300
MIN_RECORDING_SECONDS=0.5
```

### Application Constants (src/config.py)

Key constants you may want to modify:

- `WHISPER_MODEL = "small"` - Whisper model size (small, medium, large)
- `MAX_RECORDING_SECONDS = 300` - Max recording duration (5 minutes)
- `MIN_RECORDING_SECONDS = 0.5` - Min recording duration (0.5 seconds)
- `GUI_ERROR_DISPLAY_MS = 3000` - Error message display time (3 seconds)
- `OPENAI_TIMEOUT = 10` - OpenAI API timeout (10 seconds)

## Performance Notes

### Transcription Speed

- **Whisper small + CPU**: 5-15 seconds for 30 seconds of audio
- Depends on CPU and system load

### Memory Usage

- **Whisper small model**: ~1.5 GB RAM
- **Audio buffer**: ~30 MB per 5 minutes of recording
- **Total minimum**: ~2 GB free RAM recommended

### Network Requirements

- **Model download** (first run): ~460 MB
- **API call per transcription**: <100 KB
- **Recommended**: 10+ Mbps internet for reasonable API response time

## Known Limitations

- **French Only**: Language is hardcoded to French. Multi-language support is a future enhancement.
- **No Transcription History**: Transcriptions are not saved. This is intentional (paste-and-forget model).
- **No Editing Before Paste**: Text is pasted immediately after cleaning. If transcription is wrong, undo and retry.
- **Background Noise**: Whisper transcribes all audio including background noise. Record in quiet environments for best results.
- **No Voice Commands**: Only dictation is supported. Voice commands like "new paragraph" are not implemented.
- **Paste Timing**: Some protected fields (e.g., password fields) may not accept simulated Ctrl+V.

## Future Enhancements

Ideas for future versions (out of scope for MVP):

- Multi-language support with language detection
- Configurable hotkey via GUI settings
- Transcription history/log viewer
- GPU acceleration (CUDA/ROCm) for faster transcription
- Local LLM for text cleaning (replace OpenAI API with ollama)
- Voice commands for formatting (e.g., "new paragraph", "delete last sentence")
- System tray icon for status
- Audio file import for batch transcription
- Export transcriptions to file

## Development

### Code Style

- **PEP 8** compliance (checked with flake8)
- **Type hints** recommended for clarity
- **Docstrings** for public methods and classes

### Running Code Quality Checks

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Run tests
pytest
```

### Creating New Features

1. Create module in `src/`
2. Write tests in `tests/test_module.py`
3. Integration test in `src/main.py`
4. Update README and docs

## License

[Add your license here]

## Support

For issues, questions, or contributions:
1. Check Troubleshooting section above
2. Review logs in `whisper-dictation.log`
3. Check OpenAI API status at https://status.openai.com

---

**Enjoy hands-free French dictation! 🎤**
