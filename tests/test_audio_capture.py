"""
Tests for audio capture module.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.audio_capture import AudioCapture, InsufficientAudioError, BufferOverflowError
from src.config import SAMPLE_RATE, MIN_RECORDING_SECONDS, MAX_RECORDING_SECONDS


class TestAudioCapture:
    """Test AudioCapture class."""
    
    def test_initialization(self):
        """Test AudioCapture initializes correctly."""
        audio = AudioCapture()
        assert audio._buffer == []
        assert audio._is_recording is False
        assert audio._sample_count == 0
    
    @patch('sounddevice.InputStream')
    def test_start_recording(self, mock_stream_class):
        """Test starting recording initializes stream correctly."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        audio = AudioCapture()
        audio.start_recording()
        
        assert audio._is_recording is True
        mock_stream.start.assert_called_once()
    
    @patch('sounddevice.InputStream')
    def test_stop_recording(self, mock_stream_class):
        """Test stopping recording closes stream and returns audio data."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        audio = AudioCapture()
        audio.start_recording()
        
        # Add some audio data
        audio._buffer = [np.array([[100], [200], [300]], dtype='int16')]
        
        result = audio.stop_recording()
        
        assert audio._is_recording is False
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()
        assert result is not None
        assert len(result) == 3
    
    def test_get_audio_data_empty_buffer(self):
        """Test get_audio_data raises error with empty buffer."""
        audio = AudioCapture()
        
        with pytest.raises(InsufficientAudioError):
            audio.get_audio_data()
    
    def test_get_audio_data_too_short(self):
        """Test get_audio_data raises error when audio is too short."""
        audio = AudioCapture()
        
        # Create audio shorter than MIN_RECORDING_SECONDS
        short_duration_samples = int(SAMPLE_RATE * (MIN_RECORDING_SECONDS - 0.1))
        audio._buffer = [np.zeros((short_duration_samples, 1), dtype='int16')]
        
        with pytest.raises(InsufficientAudioError):
            audio.get_audio_data()
    
    def test_get_audio_data_valid(self):
        """Test get_audio_data returns audio when duration is valid."""
        audio = AudioCapture()
        
        # Create audio longer than MIN_RECORDING_SECONDS
        valid_duration_samples = int(SAMPLE_RATE * 1.0)  # 1 second
        audio._buffer = [np.random.randint(-32768, 32767, (valid_duration_samples, 1), dtype='int16')]
        
        result = audio.get_audio_data()
        assert result is not None
        assert len(result) >= valid_duration_samples
    
    @patch('sounddevice.InputStream')
    def test_buffer_overflow_protection(self, mock_stream_class):
        """Test BufferOverflowError raised when recording exceeds max duration."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        audio = AudioCapture()
        audio.start_recording()
        
        # Simulate adding audio that exceeds MAX_RECORDING_SECONDS
        # Each frame is 4096 samples at 16000 Hz = 0.256 seconds
        samples_per_frame = 4096
        
        # Create mock indata to simulate frames
        mock_indata = np.zeros((samples_per_frame, 1), dtype='int16')
        
        # Calculate frames needed to exceed MAX_RECORDING_SECONDS
        frames_to_overflow = int((MAX_RECORDING_SECONDS + 1) * SAMPLE_RATE / samples_per_frame) + 1
        
        # Add frames until overflow - this should stop recording internally
        for i in range(frames_to_overflow):
            audio._audio_callback(mock_indata, samples_per_frame, None, None)
        
        # After overflow, recording should be stopped
        assert audio._is_recording is False
