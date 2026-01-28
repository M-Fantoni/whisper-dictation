"""
Main application orchestrator.
Manages state machine, coordinates all modules, and handles hotkey events.
"""

import logging
import threading
import signal
import sys
from src.config import logger, HOTKEY
from src.audio_capture import AudioCapture, InsufficientAudioError, BufferOverflowError
from src.transcription import Transcriber
from src.text_cleaner import TextCleaner
from src.clipboard_manager import ClipboardManager
from src.gui_feedback import FeedbackWindow
from src.hotkey_manager import HotkeyManager

logger = logging.getLogger(__name__)


class WhisperDictationApp:
    """Main application managing state machine and module coordination."""
    
    def __init__(self):
        """Initialize application and all modules."""
        self._state = "IDLE"
        self._state_lock = threading.Lock()
        
        # Initialize modules
        self.gui = FeedbackWindow()
        self.audio = AudioCapture()
        self.transcriber = Transcriber(download_callback=self._on_download_progress)
        self.cleaner = TextCleaner()
        self.clipboard = ClipboardManager()
        self.hotkey = HotkeyManager(hotkey_combo=HOTKEY, callback=self._on_hotkey)
        
        logger.info("WhisperDictationApp initialized")
    
    def run(self):
        """Start the application."""
        try:
            logger.info("Starting Whisper Dictation application")
            self.hotkey.start()
            self.gui.mainloop()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.shutdown()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.shutdown()
            sys.exit(1)
    
    def shutdown(self):
        """Clean shutdown of application."""
        logger.info("Shutting down...")
        self.hotkey.stop()
        self.gui.quit()
        logger.info("Shutdown complete")
    
    def _get_state(self):
        """Get current state (thread-safe)."""
        with self._state_lock:
            return self._state
    
    def _set_state(self, new_state):
        """Set state and update hotkey manager for debouncing."""
        with self._state_lock:
            if self._state != new_state:
                logger.debug(f"State transition: {self._state} → {new_state}")
                self._state = new_state
                self.hotkey.set_state(new_state)
    
    def _transition_state(self, from_state, to_state):
        """Validate and perform state transition."""
        current = self._get_state()
        if current != from_state:
            logger.warning(f"Invalid state transition: expected {from_state}, got {current}")
            return False
        self._set_state(to_state)
        return True
    
    def _on_hotkey(self):
        """Handle hotkey press (Alt+W toggle)."""
        with self._state_lock:
            current_state = self._state
        
        logger.debug(f"Hotkey pressed - current state: {current_state}")
        
        try:
            if current_state == "IDLE":
                self._start_listening()
            elif current_state == "LISTENING":
                self._stop_listening()
            else:
                logger.warning(f"Hotkey ignored in state: {current_state}")
        except Exception as e:
            logger.error(f"Error handling hotkey: {e}")
            self.gui.show_error("Erreur", duration_ms=3000)
            self._set_state("IDLE")
    
    def _start_listening(self):
        """Transition to LISTENING state and start audio capture."""
        if not self._transition_state("IDLE", "LISTENING"):
            return
        
        try:
            self.audio.start_recording()
            self.gui.show_listening()
            logger.info("Listening started")
        except Exception as e:
            logger.error(f"Failed to start listening: {e}")
            self.gui.show_error("Mic indisponible")
            self._set_state("IDLE")
    
    def _stop_listening(self):
        """Stop audio capture and transition to PROCESSING."""
        if not self._transition_state("LISTENING", "PROCESSING"):
            return
        
        try:
            self.gui.show_processing()
            
            # Stop audio in main thread
            audio_data = self.audio.stop_recording()
            
            # Validate audio duration
            try:
                validated_audio = self.audio.get_audio_data()
            except InsufficientAudioError as e:
                logger.warning(f"Insufficient audio: {e}")
                self.gui.show_error("Trop court")
                self._set_state("IDLE")
                return
            
            # Start background processing thread
            process_thread = threading.Thread(
                target=self._process_audio,
                args=(validated_audio,),
                daemon=False
            )
            process_thread.start()
            logger.info("Processing thread started")
        except BufferOverflowError as e:
            logger.error(f"Buffer overflow: {e}")
            self.gui.show_error("Enreg. trop long")
            self._set_state("IDLE")
        except Exception as e:
            logger.error(f"Error stopping listening: {e}")
            self.gui.show_error("Erreur capture")
            self._set_state("IDLE")
    
    def _process_audio(self, audio_data):
        """Background thread: transcribe, clean, and paste audio (runs in separate thread)."""
        try:
            logger.info("Starting audio processing")
            
            # Step 1: Transcribe
            raw_text = self.transcriber.transcribe(audio_data)
            if not raw_text:
                logger.warning("Empty transcription")
                self.gui.show_error("Aucun texte")
                self._set_state("IDLE")
                return
            
            # Step 2: Clean text
            cleaned_text = self.cleaner.clean(raw_text)
            
            # Step 3: Paste to clipboard
            self.clipboard.paste_text(cleaned_text)
            
            logger.info("Audio processing complete")
            self.gui.hide()
            self._set_state("IDLE")
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            self.gui.show_error("Erreur traitement")
            self._set_state("IDLE")
    
    def _on_download_progress(self, progress_percent):
        """Callback for model download progress."""
        self.gui.show_downloading(progress_percent)


def main():
    """Application entry point."""
    try:
        logger.info("=" * 60)
        logger.info("Whisper Dictation - Starting")
        logger.info("=" * 60)
        
        app = WhisperDictationApp()
        
        # Handle Ctrl+C gracefully
        def signal_handler(signum, frame):
            logger.info("Received SIGINT")
            app.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Run application
        app.run()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
