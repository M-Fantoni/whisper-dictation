---
title: 'Whisper Dictation - Outil de dictée vocale local minimaliste'
slug: 'whisper-dictation-local-tool'
created: '2026-01-28'
status: 'Completed'
stepsCompleted: [1, 2, 3, 4, 5, 6]
implementation_date: '2026-01-28'
review_status: 'Adversarial Review Completed - 3 Issues Fixed'
test_status: 'All 37 Tests Passing'
tech_stack:
  - Python 3.11.5
  - faster-whisper (small model, CPU-only)
  - OpenAI API (GPT-4o-mini)
  - sounddevice (audio capture)
  - pynput (hotkey + keyboard simulation)
  - pyperclip (clipboard)
  - tkinter (GUI)
  - pytest (testing)
  - python-dotenv (env vars)
files_to_modify:
  - src/main.py (CREATE)
  - src/hotkey_manager.py (CREATE)
  - src/audio_capture.py (CREATE)
  - src/transcription.py (CREATE)
  - src/text_cleaner.py (CREATE)
  - src/clipboard_manager.py (CREATE)
  - src/gui_feedback.py (CREATE)
  - src/config.py (CREATE)
  - tests/test_hotkey_manager.py (CREATE)
  - tests/test_audio_capture.py (CREATE)
  - tests/test_transcription.py (CREATE)
  - tests/test_text_cleaner.py (CREATE)
  - tests/test_clipboard_manager.py (CREATE)
  - requirements.txt (CREATE)
  - requirements-dev.txt (CREATE)
  - .env.example (CREATE)
  - .gitignore (CREATE)
  - pytest.ini (CREATE)
  - README.md (CREATE)
code_patterns:
  - State-driven architecture (IDLE → LISTENING → PROCESSING → IDLE)
  - Threading model: hotkey listener, audio capture, async processing
  - Modular design: one concern per file
  - Dependency injection ready (easy mocking for tests)
  - Error handling with fallbacks (API fail → use raw transcription)
test_patterns:
  - pytest with unittest.mock for all external dependencies
  - Mock sounddevice, faster-whisper, OpenAI API, pynput, pyperclip
  - Unit tests only (no GUI testing, manual validation for tkinter)
  - Test naming: test_{module}_{function}_{scenario}
---

# Tech-Spec: Whisper Dictation - Outil de dictée vocale local minimaliste

**Created:** 2026-01-28

## Overview

### Problem Statement

L'utilisateur souhaite dicter du texte en français dans n'importe quelle application Windows (incluant VS Code) sans dépendre de services cloud. Les solutions existantes (comme Superwhisper) sont soit payantes, soit nécessitent une connexion cloud permanente. Le besoin est un outil local minimal avec feedback visuel uniquement.

### Solution

Application Python desktop avec hotkey global (Alt+W) en mode toggle :
- Premier appui : démarrage de l'enregistrement audio via le microphone
- Second appui : arrêt de l'enregistrement → transcription locale avec faster-whisper → nettoyage du texte via ChatGPT API → insertion automatique du texte à la position du curseur actif

Interface graphique minimale (tkinter) servant uniquement de feedback visuel avec deux états :
- "🎤 Écoute..." pendant l'enregistrement
- "⏳ Traitement..." pendant transcription/nettoyage/paste

### Scope

**In Scope:**
- Hotkey global Alt+W (toggle on/off)
- Capture audio microphone en temps réel
- Transcription locale avec faster-whisper (modèle small, français forcé)
- Nettoyage du texte transcrit via OpenAI API (suppression mots parasites + correction grammaire)
- Insertion automatique du texte nettoyé à la position curseur (via clipboard + simulation Ctrl+V)
- GUI tkinter minimale (affichage état uniquement : hidden/listening/processing)
- Exécution 100% locale (sauf appel API ChatGPT pour nettoyage)
- Support Windows 10 Famille, CPU uniquement
- Architecture modulaire avec tests unitaires pour chaque composant

**Out of Scope:**
- Support macOS/Linux (bien que pynput soit cross-platform, focus Windows uniquement)
- Configuration GUI (pas de settings, tout hardcodé ou via fichier config simple)
- Multi-langues (français uniquement)
- GPU acceleration
- Historique des transcriptions
- Export/sauvegarde des enregistrements audio
- Édition du texte avant insertion
- Support de commandes vocales
- Modèles Whisper autres que small (évolutif mais pas dans scope initial)

## Context for Development

### Codebase Patterns

**✅ Confirmed Clean Slate** - Investigation technique complète effectuée, aucun code existant détecté.

**Environnement détecté :**
- Python 3.11.5 (système + venv)
- `.venv/` créé mais vide (aucune dépendance installée)
- `.vscode/` vide (pas de settings spécifiques)
- `.github/agents/` présent (config future GitHub Actions)
- **Pas de `.gitignore`** (à créer pour `.env`, `__pycache__`, `.venv`)
- **Pas de `requirements.txt`** (à créer)
- **Pas de conventions héritées** → liberté totale sur architecture

**Architecture adoptée :**

```
State Machine Pattern (Event-Driven)
─────────────────────────────────────
IDLE → (Alt+W pressed) → LISTENING
LISTENING → (Alt+W pressed) → PROCESSING
PROCESSING → (completion) → IDLE

Threading Model:
├── Main Thread: tkinter GUI loop
├── Thread 1: pynput hotkey listener (global keyboard hook)
├── Thread 2: sounddevice audio capture (blocking read)
└── AsyncIO: transcription + API call + paste (non-blocking)
```

**Modular Design:**
- **1 module = 1 responsabilité** (SOLID principe)
- Communication via événements/callbacks (découplage)
- Injection de dépendances pour testabilité
- Configuration centralisée dans `config.py`

**Code Conventions (à établir):**
```python
# Naming
- Classes: PascalCase (AudioCapture, HotkeyManager)
- Functions: snake_case (start_recording, clean_text)
- Constants: UPPER_SNAKE_CASE (WHISPER_MODEL, SAMPLE_RATE)
- Private methods: _leading_underscore (_handle_error)

# File structure par module
class ModuleName:
    def __init__(self, dependencies):
        """Initialize with dependencies for DI"""
    
    def public_method(self):
        """Public API"""
    
    def _private_helper(self):
        """Internal logic"""

# Error handling
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Context: {e}")
    fallback_behavior()
```

**Structure cible finale :**
```
whisper-dictation/
├── src/
│   ├── main.py                 # Point d'entrée + state machine orchestration
│   ├── hotkey_manager.py       # pynput global hotkey (Alt+W toggle)
│   ├── audio_capture.py        # sounddevice recording (16kHz mono WAV)
│   ├── transcription.py        # faster-whisper wrapper (small model, fr)
│   ├── text_cleaner.py         # OpenAI API call (GPT-4o-mini)
│   ├── clipboard_manager.py    # pyperclip + pynput paste simulation
│   ├── gui_feedback.py         # tkinter window (borderless, always-on-top)
│   └── config.py               # Constants (API key from .env, model settings)
├── tests/
│   ├── test_hotkey_manager.py  # Mock pynput, test state transitions
│   ├── test_audio_capture.py   # Mock sounddevice, verify 16kHz mono format
│   ├── test_transcription.py   # Mock WhisperModel, verify language="fr"
│   ├── test_text_cleaner.py    # Mock OpenAI client, test fallback logic
│   └── test_clipboard_manager.py # Mock pyperclip + pynput, test paste sequence
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies (pytest, black, flake8)
├── .env.example                # Template: OPENAI_API_KEY=your_key_here
├── .env                        # User's actual API key (GITIGNORED)
├── .gitignore                  # Ignore: .env, .venv/, __pycache__/, *.pyc, .pytest_cache/
├── pytest.ini                  # Pytest configuration
└── README.md                   # Setup instructions + usage
```

### Files to Reference

| File | Purpose |
| ---- | ------- |
| N/A | **Clean slate confirmé** - aucun fichier existant à référencer. Tous les fichiers listés dans `files_to_modify` doivent être créés from scratch. |

### Technical Decisions

1. **faster-whisper avec modèle `small`** : Bon compromis vitesse/qualité pour transcription française sur CPU (~460 MB, quantized). Modèle téléchargé automatiquement au premier lancement.

2. **OpenAI API (GPT-4o-mini)** : Nettoyage du texte transcrit (suppression "euh", "hum", correction grammaire/ponctuation). Nécessite clé API fournie par utilisateur via fichier `.env`.

3. **sounddevice pour capture audio** : API moderne Python pour enregistrement microphone en temps réel. Format audio : 16kHz mono WAV (optimal pour Whisper).

4. **pynput pour hotkey + paste** : Cross-platform (bien que focus Windows), gestion hotkey global Alt+W + simulation Ctrl+V pour insertion texte.

5. **pyperclip pour clipboard** : Copie du texte nettoyé dans le presse-papiers avant simulation Ctrl+V (compatible toutes applications).

6. **tkinter pour GUI** : Inclus dans Python standard, zéro configuration. Fenêtre sans bordures, toujours au premier plan, petite taille (~200x80px), apparaît uniquement pendant recording/processing.

7. **Architecture état-driven** : 
   - États : `IDLE` → `LISTENING` → `PROCESSING` → `IDLE`
   - Transitions déclenchées par hotkey et completion des tâches async
   - GUI se synchronise sur les changements d'état

8. **Threading/Async** : 
   - Hotkey listener sur thread séparé (pynput requirement)
   - Audio capture sur thread dédié
   - Transcription + nettoyage + paste en async pour ne pas bloquer GUI
   - tkinter mainloop sur thread principal

9. **Gestion erreurs** :
   - Microphone indisponible → afficher erreur GUI temporaire
   - API OpenAI timeout/erreur → fallback texte transcrit brut sans nettoyage
   - Whisper crash → logger erreur et retour état IDLE

10. **Configuration** :
    - `config.py` : constantes (langue="fr", modèle="small", hotkey="<alt>+w")
    - `.env` : `OPENAI_API_KEY=sk-...`
    - Pas de GUI settings (KISS principle)

11. **Python 3.11.5** : Version détectée dans l'environnement. Compatible avec toutes les dépendances (faster-whisper nécessite Python ≥ 3.8). Pas de contrainte de rétrocompatibilité.

12. **Clean Architecture from Scratch** : 
    - Pas de legacy code → liberté totale sur patterns et conventions
    - Adopter PEP 8 (style guide Python standard)
    - Type hints optionnels mais recommandés pour clarté (Python 3.11 supporte bien)
    - Logging avec module `logging` standard (pas de lib externe)

13. **Test Strategy** :
    - pytest comme framework (standard de facto Python)
    - unittest.mock pour mocker dépendances externes (sounddevice, WhisperModel, OpenAI, pynput, pyperclip)
    - Pas de tests GUI tkinter (validation manuelle suffisante pour MVP)
    - Coverage target : 80%+ pour modules core (audio, transcription, cleaner, clipboard)

14. **Dependencies Management** :
    - `requirements.txt` pour prod dependencies
    - `requirements-dev.txt` pour dev dependencies (pytest, black, flake8)
    - `.env` pour secrets (gitignored)
    - `.env.example` pour documenter les variables d'environnement nécessaires

## Implementation Plan

### Tasks

**Phase 1: Project Setup & Configuration**

- [ ] Task 1: Setup project structure and configuration files
  - File: `.gitignore`
  - Action: Create gitignore with entries for `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.log`, `.DS_Store`
  - Notes: Essential avant tout commit

- [ ] Task 2: Create environment configuration template
  - File: `.env.example`
  - Action: Create template with `OPENAI_API_KEY=your_api_key_here` and usage instructions
  - Notes: Documenter comment obtenir une clé API OpenAI

- [ ] Task 3: Define project dependencies
  - File: `requirements.txt`
  - Action: List production dependencies with versions:
    ```
    faster-whisper>=1.0.0
    openai>=1.0.0
    sounddevice>=0.4.6
    pynput>=1.7.6
    pyperclip>=1.8.2
    python-dotenv>=1.0.0
    numpy>=1.24.0
    ```
  - Notes: Versions minimales pour compatibilité Python 3.11.5

- [ ] Task 4: Define development dependencies
  - File: `requirements-dev.txt`
  - Action: List dev dependencies:
    ```
    -r requirements.txt
    pytest>=7.4.0
    pytest-asyncio>=0.21.0
    pytest-mock>=3.11.0
    black>=23.0.0
    flake8>=6.0.0
    ```
  - Notes: Include requirements.txt via `-r` directive

- [ ] Task 5: Configure pytest
  - File: `pytest.ini`
  - Action: Create pytest config with test discovery patterns, markers, and asyncio mode
  - Notes: `testpaths = tests`, `python_files = test_*.py`, `asyncio_mode = auto`

- [ ] Task 6: Create application configuration module with logging setup
  - File: `src/config.py`
  - Action: Define constants (WHISPER_MODEL="small", WHISPER_LANGUAGE="fr", SAMPLE_RATE=16000, HOTKEY="<alt>+w", MAX_RECORDING_SECONDS=300, MIN_RECORDING_SECONDS=0.5), load OPENAI_API_KEY from .env via python-dotenv. Setup logging configuration with logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('whisper-dictation.log'), logging.StreamHandler()])
  - Notes: Use os.getenv() with error handling for missing API key. Log to both file and console, INFO level for production. MIN_RECORDING_SECONDS prevents Whisper crash on very short audio

**Phase 2: Core Modules (Bottom-Up)**

- [ ] Task 7: Implement audio capture module
  - File: `src/audio_capture.py`
  - Action: Create `AudioCapture` class with methods `start_recording()`, `stop_recording()`, `get_audio_data()` using sounddevice. Configure 16kHz mono format. Implement buffer size limit checking (MAX_RECORDING_SECONDS from config) and raise BufferOverflowError if exceeded. In `get_audio_data()`, validate duration >= MIN_RECORDING_SECONDS and raise InsufficientAudioError if too short.
  - Notes: Store audio in memory buffer (list of numpy arrays), thread-safe access with threading.Lock. Check buffer size on each append, calculate duration = total_samples / SAMPLE_RATE, raise error if duration > MAX_RECORDING_SECONDS. Validate minimum duration on stop to prevent Whisper crash on <0.5s audio

- [ ] Task 8: Implement transcription module
  - File: `src/transcription.py`
  - Action: Create `Transcriber` class wrapping faster-whisper `WhisperModel`. Constructor accepts optional `download_callback(progress_percent)` parameter. Method `transcribe(audio_data)` returns text string. Force language="fr", device="cpu", model="small". Check if model is cached before initialization, if not call download_callback during model loading if provided.
  - Notes: Handle model download on first run with callback to GUI (if provided) for progress updates. Use faster_whisper's download hooks if available, or wrap initialization in thread that polls download status. Log transcription time

- [ ] Task 9: Implement text cleaner module
  - File: `src/text_cleaner.py`
  - Action: Create `TextCleaner` class with `clean(raw_text)` method calling OpenAI API (gpt-4o-mini). Use exact prompt: "Tu es un assistant de correction de texte français. Supprime les mots de remplissage (euh, hum, ben, voilà, etc.), corrige la grammaire, ajoute la ponctuation appropriée et les majuscules. Garde le sens exact du texte original. Ne traduis pas, ne résume pas. Retourne uniquement le texte corrigé sans commentaire.\n\nTexte à corriger: {raw_text}". Implement fallback returning raw text if API fails.
  - Notes: Timeout 10s, catch openai.APIError, log API calls with sanitized text (first 50 chars), use temperature=0 for deterministic results

- [ ] Task 10: Implement clipboard manager module
  - File: `src/clipboard_manager.py`
  - Action: Create `ClipboardManager` class with `paste_text(text)` method. Use pyperclip to copy text, then pynput.keyboard.Controller to simulate Ctrl+V.
  - Notes: Add small delay (0.1s) between copy and paste for reliability

- [ ] Task 11: Implement GUI feedback module
  - File: `src/gui_feedback.py`
  - Action: Create `FeedbackWindow` class (tkinter.Tk subclass) with methods `show_listening()`, `show_processing()`, `show_downloading(progress_percent)`, `show_error(message, duration_ms=3000)`, `hide()`. Borderless window, always on top, 200x80px, centered, large emoji + text. Error state auto-hides after duration_ms.
  - Notes: Use `overrideredirect(True)`, `attributes('-topmost', True)`, `withdraw()` to hide. Use tkinter.after() for auto-hide error. Store timer_id to cancel if new state change occurs.

- [ ] Task 12: Implement hotkey manager module
  - File: `src/hotkey_manager.py`
  - Action: Create `HotkeyManager` class using pynput.keyboard.GlobalHotKeys. Register Alt+W with callback. Track toggle state (listening on/off) with threading.Lock. Callback should check current state and ignore hotkey press if app is in PROCESSING state (debouncing).
  - Notes: Run listener on separate thread, use threading.Lock for ALL state access (read and write). Implement state debouncing: if state==PROCESSING, log "Hotkey ignored, processing in progress" and return immediately

**Phase 3: Integration & Orchestration**

- [ ] Task 13: Implement main application orchestrator
  - File: `src/main.py`
  - Action: Create `WhisperDictationApp` class managing state machine (IDLE/LISTENING/PROCESSING). Wire all modules together via callbacks. Implement state transitions with threading.Lock protection:
    - IDLE → LISTENING: acquire lock, check state==IDLE, transition to LISTENING, release lock, start audio capture, show GUI listening
    - LISTENING → PROCESSING: acquire lock, check state==LISTENING, transition to PROCESSING, release lock, stop audio, show GUI processing, spawn background thread for transcription → cleaning → paste
    - PROCESSING → IDLE: acquire lock (in background thread after completion), transition to IDLE, release lock, hide GUI, reset state
  - Notes: Use threading.Thread ONLY (no asyncio) for background processing. tkinter.after() for GUI updates from background thread (thread-safe). Graceful shutdown on Ctrl+C. ALL state reads/writes MUST be protected by self._state_lock. Implement _transition_state(from_state, to_state) helper that validates transitions. Pass download_callback=lambda p: self.gui.show_downloading(p) to Transcriber for model download progress.

- [ ] Task 14: Add application entry point
  - File: `src/main.py`
  - Action: Add `if __name__ == "__main__":` block that loads config, initializes app, starts hotkey listener, runs tkinter mainloop
  - Notes: Wrap in try/except for clean error messages, log startup info

**Phase 4: Testing**

- [ ] Task 15: Write audio capture tests
  - File: `tests/test_audio_capture.py`
  - Action: Mock sounddevice.InputStream, test start/stop recording, verify 16kHz mono format, test thread-safety. Test BufferOverflowError raised when duration > MAX_RECORDING_SECONDS. Test InsufficientAudioError raised when duration < MIN_RECORDING_SECONDS in get_audio_data().
  - Notes: Use pytest-mock, verify callback invocations. Use pytest.raises() to verify exceptions. Simulate long/short recordings by mocking buffer append with known sample counts

- [ ] Task 16: Write transcription tests
  - File: `tests/test_transcription.py`
  - Action: Mock faster_whisper.WhisperModel, test transcribe() with sample audio data, verify language="fr" and device="cpu" passed to model
  - Notes: Mock model loading to avoid downloading during tests

- [ ] Task 17: Write text cleaner tests
  - File: `tests/test_text_cleaner.py`
  - Action: Mock openai.ChatCompletion, test clean() with sample text, test fallback when API fails (raises exception)
  - Notes: Verify prompt content, test timeout handling

- [ ] Task 18: Write clipboard manager tests
  - File: `tests/test_clipboard_manager.py`
  - Action: Mock pyperclip.copy and pynput.keyboard.Controller, test paste_text() sequence (copy then Ctrl+V)
  - Notes: Verify correct key combination sent

- [ ] Task 19: Write hotkey manager tests
  - File: `tests/test_hotkey_manager.py`
  - Action: Mock pynput.keyboard.GlobalHotKeys, test callback registration, test toggle state transitions. Test debouncing: mock callback with state=PROCESSING, verify hotkey press is ignored (callback returns immediately, no state change). Test that callback succeeds when state=IDLE or LISTENING.
  - Notes: Verify thread safety with threading.Lock. Use unittest.mock.patch to control state attribute during tests

**Phase 5: Documentation**

- [ ] Task 20: Write README with setup and usage instructions
  - File: `README.md`
  - Action: Document:
    - Project description and features
    - Prerequisites (Python 3.11+, microphone, Windows 10)
    - Installation steps (clone, create venv, pip install -r requirements.txt, setup .env)
    - Usage (run python src/main.py, use Alt+W to toggle)
    - Troubleshooting (API key, microphone permissions, Whisper model download)
    - Architecture overview
    - Testing instructions (pytest)
  - Notes: Include screenshots or ASCII art of GUI states

### Acceptance Criteria

**AC1 - Project Setup:** Given the repository is cloned, when dependencies are installed via `pip install -r requirements.txt` and `.env` file is created with valid OPENAI_API_KEY, then the application can be launched without errors.

**AC2 - Audio Capture:** Given the microphone is available, when user presses Alt+W for the first time, then audio recording starts at 16kHz mono format and GUI shows "🎤 Écoute...".

**AC3 - Recording Stop:** Given audio recording is active, when user presses Alt+W a second time, then recording stops and captured audio data is available for transcription.

**AC4 - Transcription:** Given audio data is captured (minimum 1 second), when transcription is triggered, then faster-whisper transcribes the audio in French and returns text string.

**AC5 - Text Cleaning:** Given raw transcribed text contains filler words or grammar errors, when text cleaning is triggered with valid API key, then cleaned text is returned with filler words removed and grammar corrected.

**AC6 - Text Cleaning Fallback:** Given OpenAI API is unavailable or returns error, when text cleaning is triggered, then raw transcribed text is used without throwing exception.

**AC7 - Clipboard Paste:** Given cleaned text is ready, when paste operation is triggered, then text is copied to clipboard and Ctrl+V is simulated at cursor position.

**AC8 - State Machine - Idle to Listening:** Given application is in IDLE state, when Alt+W is pressed, then state transitions to LISTENING, audio recording starts, and GUI shows listening indicator.

**AC9 - State Machine - Listening to Processing:** Given application is in LISTENING state, when Alt+W is pressed again, then state transitions to PROCESSING, audio recording stops, and GUI shows processing indicator.

**AC10 - State Machine - Processing to Idle:** Given application is in PROCESSING state, when transcription, cleaning, and paste complete successfully, then state returns to IDLE and GUI is hidden.

**AC11 - Error Handling - Microphone Unavailable:** Given no microphone is detected, when Alt+W is pressed to start recording, then error message is logged, GUI shows error briefly, and state returns to IDLE.

**AC12 - Error Handling - Whisper Failure:** Given transcription fails (model crash or invalid audio), when transcription is attempted, then error is logged, state returns to IDLE, and no paste occurs.

**AC13 - Error Handling - Missing API Key:** Given OPENAI_API_KEY is not set in .env, when application starts, then clear error message is displayed and application exits gracefully.

**AC14 - GUI Visibility:** Given application is running, when state is IDLE, then GUI window is hidden. When state is LISTENING or PROCESSING, then GUI is visible, borderless, always on top, and centered on screen.

**AC15 - GUI Content:** Given GUI is visible in LISTENING state, then it displays "🎤 Écoute..." in large text. Given GUI is visible in PROCESSING state, then it displays "⏳ Traitement..." in large text.

**AC16 - Hotkey Global Registration:** Given application is running, when Alt+W is pressed from any application (including VS Code, Notepad, browser), then hotkey is detected and appropriate action is triggered.

**AC17 - End-to-End Happy Path:** Given application is running and microphone is available, when user presses Alt+W, speaks "Bonjour euh je teste la dictation vocale", presses Alt+W again, then "Bonjour, je teste la dictation vocale." (cleaned) is pasted at cursor position within 15 seconds.

**AC18 - Threading Safety:** Given multiple threads access shared state (audio buffer, state machine), when concurrent operations occur, then no race conditions or deadlocks occur and state remains consistent.

**AC19 - Graceful Shutdown:** Given application is running, when user presses Ctrl+C or closes window, then all threads terminate cleanly, hotkey listener stops, and no resource leaks occur.

**AC20 - Test Coverage:** Given all core modules are implemented, when pytest is run, then all unit tests pass with >80% code coverage on src/audio_capture.py, src/transcription.py, src/text_cleaner.py, src/clipboard_manager.py, src/hotkey_manager.py.

**AC21 - Buffer Overflow Protection:** Given audio recording is active for more than MAX_RECORDING_SECONDS (300s default), when audio buffer check occurs, then BufferOverflowError is raised, error is displayed in GUI, and state returns to IDLE without attempting transcription.

**AC22 - Race Condition Prevention:** Given application is in PROCESSING state, when user presses Alt+W multiple times, then subsequent hotkey presses are ignored (debounced) until state returns to IDLE, preventing state machine corruption.

**AC23 - Logging Configuration:** Given application starts, when any module logs information, then logs are written to both whisper-dictation.log file and console with timestamp, module name, and log level.

**AC24 - Error State Display:** Given an error occurs (microphone unavailable, buffer overflow, Whisper crash), when error is triggered, then GUI displays error message with ❌ emoji for 3 seconds before auto-hiding and returning to IDLE state.

**AC25 - Model Download Progress:** Given Whisper model is not cached and application starts for first time, when model download occurs, then GUI displays "📥 Téléchargement du modèle..." instead of staying hidden, keeping user informed.

**AC26 - OpenAI Prompt Consistency:** Given raw transcribed text is sent to OpenAI API, when clean() is called, then the exact prompt specified in Task 9 is used with temperature=0, ensuring deterministic and consistent text cleaning behavior.

**AC27 - Minimum Audio Duration:** Given user presses Alt+W to stop recording after less than MIN_RECORDING_SECONDS (0.5s default), when audio validation occurs, then InsufficientAudioError is raised, GUI displays error "Enregistrement trop court" for 3 seconds, and state returns to IDLE without attempting transcription.

## Additional Context

### Dependencies

**External Libraries:**
- `faster-whisper` - Whisper model inference (CPU-optimized)
- `openai` - OpenAI API client for GPT-4o-mini
- `sounddevice` - Audio I/O library
- `pynput` - Keyboard/mouse monitoring and control
- `pyperclip` - Cross-platform clipboard access
- `python-dotenv` - Environment variable loading
- `numpy` - Array operations (dependency of sounddevice/whisper)

**System Dependencies:**
- Python 3.11.5+ (detected in environment)
- Microphone access (Windows permissions)
- Internet connection (for OpenAI API calls and Whisper model download on first run)

**No Internal Dependencies:**
- Clean slate project, no other features to depend on
- All modules are independent with clear interfaces

### Testing Strategy

**Unit Tests (pytest + unittest.mock):**

1. **test_audio_capture.py:**
   - Mock `sounddevice.InputStream`
   - Test `start_recording()` initializes stream with correct params (16kHz, 1 channel, dtype=int16)
   - Test `stop_recording()` closes stream and returns audio data
   - Test thread-safe buffer append operations
   - Test error handling for unavailable microphone

2. **test_transcription.py:**
   - Mock `faster_whisper.WhisperModel`
   - Test `transcribe()` passes correct parameters (language="fr", device="cpu")
   - Test model loading doesn't download during tests
   - Test handling of empty audio data
   - Test handling of model crash (exception)

3. **test_text_cleaner.py:**
   - Mock `openai.ChatCompletion.create()`
   - Test `clean()` sends correct prompt to API
   - Test successful cleaning returns modified text
   - Test API timeout triggers fallback to raw text
   - Test API error (invalid key, rate limit) triggers fallback
   - Test fallback preserves original text exactly

4. **test_clipboard_manager.py:**
   - Mock `pyperclip.copy()` and `pynput.keyboard.Controller.press/release()`
   - Test `paste_text()` calls copy() then simulates Ctrl+V (Key.ctrl + 'v')
   - Test delay between copy and paste (0.1s)
   - Test paste with empty string (no-op)

5. **test_hotkey_manager.py:**
   - Mock `pynput.keyboard.GlobalHotKeys`
   - Test hotkey registration with correct key combination ("<alt>+w")
   - Test callback is invoked on hotkey press
   - Test toggle state flips correctly (False → True → False)
   - Test thread safety of state access with threading.Lock

**Integration Tests (Manual for MVP):**

1. **End-to-end test:**
   - Start app, verify GUI hidden
   - Press Alt+W, speak "Bonjour, comment ça va ?"
   - Press Alt+W again
   - Verify text pasted in Notepad within 10-15 seconds
   - Verify GUI hidden after paste

2. **Error scenarios:**
   - Disconnect microphone before pressing Alt+W → verify error message
   - Remove .env file → verify startup error message
   - Disable internet → verify transcription works but cleaning uses fallback

3. **Cross-app test:**
   - Test paste in VS Code editor
   - Test paste in browser textarea
   - Test paste in Windows Notepad
   - Verify Alt+W works regardless of focused application

**No GUI Tests:**
- tkinter GUI too complex to mock/automate for MVP
- Manual validation sufficient (visual inspection of states)

**Coverage Target:**
- Core modules: 80%+ (audio, transcription, cleaner, clipboard, hotkey)
- Main orchestrator: 60%+ (harder to test state machine without integration tests)

### Notes

**High-Risk Items (Pre-Mortem):**

1. **Whisper Model Download:** First run downloads ~460 MB model. User might think app is frozen.
   - ✅ Mitigation IMPLÉMENTÉE: Task 11 inclut `show_downloading()` method, GUI affiche "📥 Téléchargement du modèle..." pendant le download

2. **OpenAI API Rate Limits:** Free tier has low rate limits, might fail during testing.
   - ✅ Mitigation IMPLÉMENTÉE: Fallback to raw text in Task 9, core functionality garantie même sans API

3. **Hotkey Conflicts:** Alt+W might conflict with other apps (e.g., browser close tab).
   - Mitigation: Document potential conflicts, suggest remapping in config.py (future enhancement).

4. **Audio Buffer Memory:** Long recordings (>5 minutes) might consume significant memory.
   - ✅ Mitigation IMPLÉMENTÉE: Task 7 inclut buffer size limit (MAX_RECORDING_SECONDS=300s), BufferOverflowError raised si dépassé

5. **State Machine Race Conditions:** Spam Alt+W pendant processing pourrait corrompre l'état.
   - ✅ Mitigation IMPLÉMENTÉE: Task 12 et 13 incluent debouncing avec threading.Lock, hotkey ignoré si state==PROCESSING

5. **pynput Permissions:** Some Windows security tools block global hotkey listeners.
   - Mitigation: Document in README, suggest adding to antivirus whitelist.

6. **Paste Timing:** Ctrl+V simulation might be too fast for some apps to register.
   - Mitigation: 0.1s delay between copy and paste, configurable if needed.

**Known Limitations:**

- **French Only:** Whisper forced to French, no UI to change language (scope decision).
- **No History:** Transcriptions not saved, paste-and-forget model (scope decision).
- **CPU Performance:** Whisper small on CPU takes 5-15s for 30s audio. Acceptable for dictation use case.
- **No Editing:** No preview/edit before paste. If transcription is wrong, user must undo and retry.
- **Windows Focus:** Paste only works if target app accepts clipboard paste (e.g., won't work in some protected fields).
- **Background Noise:** Whisper transcribes all audio including background noise (traffic, fans, keyboard). No Voice Activity Detection (VAD) or noise filtering. User should record in quiet environment or may get "phantom words" from noise. Future enhancement: integrate silero-vad or similar.

**Future Considerations (Out of Scope but Worth Noting):**

- Multi-language support with language detection
- Configurable hotkey via GUI settings
- Transcription history/log viewer
- GPU acceleration for faster transcription
- Local LLM for text cleaning (replace OpenAI API with ollama)
- Voice commands (e.g., "new paragraph", "delete last sentence")
- System tray icon for status indication
- Audio file import for batch transcription
- Export transcriptions to file
