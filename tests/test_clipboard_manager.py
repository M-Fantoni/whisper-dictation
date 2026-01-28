"""
Tests for clipboard manager module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.clipboard_manager import ClipboardManager


class TestClipboardManager:
    """Test ClipboardManager class."""
    
    @patch('src.clipboard_manager.Controller')
    def test_initialization(self, mock_controller_class):
        """Test ClipboardManager initializes correctly."""
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        
        manager = ClipboardManager()
        
        assert manager._keyboard is not None
        assert manager._paste_delay == 0.1
    
    @patch('src.clipboard_manager.pyperclip.copy')
    @patch('src.clipboard_manager.Controller')
    def test_paste_text_success(self, mock_controller_class, mock_copy):
        """Test paste_text copies and simulates Ctrl+V."""
        mock_keyboard = MagicMock()
        mock_controller_class.return_value = mock_keyboard
        
        manager = ClipboardManager()
        manager.paste_text("Hello world")
        
        # Verify copy was called
        mock_copy.assert_called_once_with("Hello world")
        
        # Verify keyboard was used
        mock_keyboard.pressed.assert_called()
    
    @patch('src.clipboard_manager.pyperclip.copy')
    @patch('src.clipboard_manager.Controller')
    def test_paste_text_empty(self, mock_controller_class, mock_copy):
        """Test paste_text handles empty text gracefully."""
        mock_keyboard = MagicMock()
        mock_controller_class.return_value = mock_keyboard
        
        manager = ClipboardManager()
        manager.paste_text("")
        
        # Should not attempt paste for empty text
        mock_copy.assert_not_called()
    
    @patch('src.clipboard_manager.pyperclip.copy')
    @patch('src.clipboard_manager.Controller')
    def test_paste_text_none(self, mock_controller_class, mock_copy):
        """Test paste_text handles None gracefully."""
        mock_keyboard = MagicMock()
        mock_controller_class.return_value = mock_keyboard
        
        manager = ClipboardManager()
        manager.paste_text(None)
        
        # Should not attempt paste for None
        mock_copy.assert_not_called()
    
    @patch('src.clipboard_manager.pyperclip.copy')
    @patch('src.clipboard_manager.Controller')
    def test_paste_text_ctrl_v_combination(self, mock_controller_class, mock_copy):
        """Test paste_text simulates Ctrl+V correctly."""
        mock_keyboard = MagicMock()
        mock_keyboard.pressed.return_value.__enter__ = Mock()
        mock_keyboard.pressed.return_value.__exit__ = Mock(return_value=False)
        mock_controller_class.return_value = mock_keyboard
        
        manager = ClipboardManager()
        manager.paste_text("Test text")
        
        # Verify Ctrl is pressed
        from pynput.keyboard import Key
        mock_keyboard.pressed.assert_called_with(Key.ctrl)
        
        # Verify v key is pressed and released
        mock_keyboard.press.assert_called_with('v')
        mock_keyboard.release.assert_called_with('v')
