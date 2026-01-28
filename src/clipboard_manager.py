"""
Clipboard manager module.
Copies text to clipboard and simulates paste (Ctrl+V) at current cursor position.
"""

import logging
import time
import pyperclip
from pynput.keyboard import Controller, Key

logger = logging.getLogger(__name__)


class ClipboardManager:
    """Manages clipboard operations and text pasting."""
    
    def __init__(self):
        """Initialize keyboard controller."""
        self._keyboard = Controller()
        self._paste_delay = 0.1  # Delay between copy and paste for reliability
    
    def paste_text(self, text):
        """
        Copy text to clipboard and simulate Ctrl+V paste at cursor position.
        
        Args:
            text: Text to paste
        """
        if not text:
            logger.warning("Empty text provided to paste")
            return
        
        try:
            logger.info(f"Pasting text (length: {len(text)}): '{text[:50]}...'")
            
            # Copy text to clipboard
            pyperclip.copy(text)
            logger.debug("Text copied to clipboard")
            
            # Wait for clipboard to be ready
            time.sleep(self._paste_delay)
            
            # Simulate Ctrl+V
            with self._keyboard.pressed(Key.ctrl):
                self._keyboard.press('v')
                self._keyboard.release('v')
            
            logger.info("Paste operation completed")
        except Exception as e:
            logger.error(f"Failed to paste text: {e}")
            raise
