"""
Hotkey manager module using pynput.
Manages global Alt+W hotkey registration and toggle state.
"""

import logging
import threading
from pynput.keyboard import GlobalHotKeys

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Manages global hotkey registration with debouncing and thread safety."""
    
    def __init__(self, hotkey_combo="<alt>+w", callback=None):
        """
        Initialize hotkey manager.
        
        Args:
            hotkey_combo: Hotkey combination string (default: "<alt>+w")
            callback: Callable to invoke when hotkey is pressed
        """
        self._hotkey_combo = hotkey_combo
        self._callback = callback
        self._listener = None
        self._lock = threading.RLock()  # Changed to RLock to prevent deadlock with callback re-entry
        self._state = None  # Will be set by orchestrator
    
    def register(self, callback):
        """Register hotkey callback."""
        self._callback = callback
    
    def set_state(self, state):
        """Set current application state for debouncing."""
        with self._lock:
            self._state = state
    
    def start(self):
        """Start listening for hotkey."""
        try:
            # Create listener with hotkey mapping
            self._listener = GlobalHotKeys({
                self._hotkey_combo: self._handle_hotkey
            })
            self._listener.start()
            logger.info(f"Hotkey listener started: {self._hotkey_combo}")
        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            raise
    
    def stop(self):
        """Stop listening for hotkey."""
        try:
            if self._listener:
                self._listener.stop()
                logger.info("Hotkey listener stopped")
        except Exception as e:
            logger.error(f"Error stopping hotkey listener: {e}")
    
    def _handle_hotkey(self):
        """Internal handler for hotkey press with debouncing."""
        print("DEBUG: Hotkey callback triggered!")  # Direct console output for debugging
        with self._lock:
            # Debounce: ignore hotkey if processing
            if self._state == "PROCESSING":
                logger.debug("Hotkey ignored - processing in progress")
                return
            
            # Invoke callback if registered
            if self._callback:
                try:
                    self._callback()
                except Exception as e:
                    logger.error(f"Error in hotkey callback: {e}")
