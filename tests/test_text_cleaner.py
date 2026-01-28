"""
Tests for text cleaner module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.text_cleaner import TextCleaner


class TestTextCleaner:
    """Test TextCleaner class."""
    
    @patch('src.text_cleaner.OpenAI')
    def test_initialization(self, mock_openai_class):
        """Test TextCleaner initializes OpenAI client."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        cleaner = TextCleaner()
        
        assert cleaner._client is not None
        mock_openai_class.assert_called_once()
    
    @patch('src.text_cleaner.OpenAI')
    def test_clean_success(self, mock_openai_class):
        """Test clean returns cleaned text from API."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Bonjour, comment allez-vous?"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        cleaner = TextCleaner()
        result = cleaner.clean("bonjour euh comment allez vous")
        
        assert result == "Bonjour, comment allez-vous?"
    
    @patch('src.text_cleaner.OpenAI')
    def test_clean_empty_text(self, mock_openai_class):
        """Test clean returns empty string for empty input."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        cleaner = TextCleaner()
        result = cleaner.clean("")
        
        assert result == ""
        # Should not call API for empty text
        mock_client.chat.completions.create.assert_not_called()
    
    @patch('src.text_cleaner.OpenAI')
    def test_clean_api_error_fallback(self, mock_openai_class):
        """Test clean falls back to raw text on API error."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai_class.return_value = mock_client
        
        cleaner = TextCleaner()
        raw_text = "bonjour euh comment allez vous"
        result = cleaner.clean(raw_text)
        
        assert result == raw_text
    
    @patch('src.text_cleaner.OpenAI')
    def test_clean_timeout_fallback(self, mock_openai_class):
        """Test clean falls back to raw text on timeout."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Timeout")
        mock_openai_class.return_value = mock_client
        
        cleaner = TextCleaner()
        raw_text = "bonjour euh comment allez vous"
        result = cleaner.clean(raw_text)
        
        assert result == raw_text
    
    @patch('src.text_cleaner.OpenAI')
    def test_clean_temperature_zero(self, mock_openai_class):
        """Test clean uses temperature=0 for deterministic output."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Cleaned text"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        cleaner = TextCleaner()
        cleaner.clean("raw text")
        
        # Verify temperature=0 is passed
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['temperature'] == 0
    
    @patch('src.text_cleaner.OpenAI')
    def test_clean_uses_gpt4o_mini(self, mock_openai_class):
        """Test clean uses gpt-4o-mini model."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Cleaned text"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        cleaner = TextCleaner()
        cleaner.clean("raw text")
        
        # Verify model parameter
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == "gpt-4o-mini"
    
    @patch('src.text_cleaner.OpenAI')
    def test_clean_prompt_content(self, mock_openai_class):
        """Test clean sends correct prompt to API."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Cleaned text"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        cleaner = TextCleaner()
        raw_text = "bonjour euh comment ca va"
        cleaner.clean(raw_text)
        
        # Verify messages
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        messages = call_kwargs['messages']
        
        # Check system message exists
        system_msg = next((m for m in messages if m['role'] == 'system'), None)
        assert system_msg is not None
        assert "correction de texte français" in system_msg['content']
        
        # Check user message contains raw text
        user_msg = next((m for m in messages if m['role'] == 'user'), None)
        assert user_msg is not None
        assert raw_text in user_msg['content']
