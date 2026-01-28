"""
Tests for transcription module.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.transcription import Transcriber
from src.config import WHISPER_MODEL, WHISPER_LANGUAGE, SAMPLE_RATE


class TestTranscriber:
    """Test Transcriber class."""
    
    @patch('src.transcription.WhisperModel')
    def test_initialization(self, mock_model_class):
        """Test Transcriber initializes WhisperModel correctly."""
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        transcriber = Transcriber()
        
        assert transcriber._model is not None
        mock_model_class.assert_called_once()
    
    @patch('src.transcription.WhisperModel')
    def test_initialization_with_callback(self, mock_model_class):
        """Test Transcriber calls download callback during initialization."""
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_callback = Mock()
        
        transcriber = Transcriber(download_callback=mock_callback)
        
        assert transcriber._download_callback is mock_callback
    
    @patch('src.transcription.WhisperModel')
    def test_transcribe_success(self, mock_model_class):
        """Test transcribe returns text from Whisper model."""
        mock_segment1 = Mock(text="Hello ")
        mock_segment2 = Mock(text="world")
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment1, mock_segment2], Mock())
        mock_model_class.return_value = mock_model
        
        transcriber = Transcriber()
        
        # Create test audio data
        audio_data = np.random.randint(-32768, 32767, (SAMPLE_RATE * 2,), dtype='int16')
        
        result = transcriber.transcribe(audio_data)
        
        # Verify the text contains expected parts (may have extra spaces)
        assert "Hello" in result
        assert "world" in result
        mock_model.transcribe.assert_called_once()
    
    @patch('src.transcription.WhisperModel')
    def test_transcribe_empty(self, mock_model_class):
        """Test transcribe with no segments returns empty string."""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([], Mock())
        mock_model_class.return_value = mock_model
        
        transcriber = Transcriber()
        audio_data = np.random.randint(-32768, 32767, (SAMPLE_RATE,), dtype='int16')
        
        result = transcriber.transcribe(audio_data)
        
        assert result == ""
    
    @patch('src.transcription.WhisperModel')
    def test_transcribe_language_constraint(self, mock_model_class):
        """Test transcribe enforces French language."""
        mock_segment = Mock(text="Bonjour")
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], Mock())
        mock_model_class.return_value = mock_model
        
        transcriber = Transcriber()
        audio_data = np.random.randint(-32768, 32767, (SAMPLE_RATE,), dtype='int16')
        
        transcriber.transcribe(audio_data)
        
        # Verify language parameter is passed to transcribe
        call_kwargs = mock_model.transcribe.call_args[1]
        assert call_kwargs['language'] == WHISPER_LANGUAGE
    
    @patch('src.transcription.WhisperModel')
    def test_transcribe_device_cpu(self, mock_model_class):
        """Test Transcriber uses CPU device."""
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        Transcriber()
        
        call_kwargs = mock_model_class.call_args[1]
        assert call_kwargs['device'] == "cpu"
    
    @patch('src.transcription.WhisperModel')
    def test_transcribe_raises_exception(self, mock_model_class):
        """Test transcribe raises exception on model error."""
        mock_model = MagicMock()
        mock_model.transcribe.side_effect = RuntimeError("Model crash")
        mock_model_class.return_value = mock_model
        
        transcriber = Transcriber()
        audio_data = np.random.randint(-32768, 32767, (SAMPLE_RATE,), dtype='int16')
        
        with pytest.raises(RuntimeError):
            transcriber.transcribe(audio_data)
