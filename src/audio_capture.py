"""
Audio capture module using sounddevice.
Handles recording from microphone with thread-safe buffer management.
"""

import logging
import threading
import numpy as np
import sounddevice as sd
from src.config import SAMPLE_RATE, AUDIO_CHANNELS, AUDIO_DTYPE, MAX_RECORDING_SECONDS, MIN_RECORDING_SECONDS

logger = logging.getLogger(__name__)


class InsufficientAudioError(Exception):
    """Raised when recorded audio is shorter than minimum duration."""
    pass


class BufferOverflowError(Exception):
    """Raised when audio buffer exceeds maximum recording time."""
    pass


class AudioCapture:
    """Captures audio from microphone with thread-safe buffer management."""
    
    def __init__(self):
        """Initialize audio capture with thread lock for safety."""
        self._buffer = []
        self._stream = None
        self._is_recording = False
        self._lock = threading.Lock()
        self._sample_count = 0
    
    def start_recording(self):
        """Start recording audio from microphone at specified sample rate."""
        with self._lock:
            if self._is_recording:
                logger.warning("Recording already in progress")
                return
            
            try:
                self._buffer = []
                self._sample_count = 0
                self._is_recording = True
                
                # Create stream with callback for continuous recording
                self._stream = sd.InputStream(
                    samplerate=SAMPLE_RATE,
                    channels=AUDIO_CHANNELS,
                    dtype=AUDIO_DTYPE,
                    blocksize=4096,
                    callback=self._audio_callback
                )
                self._stream.start()
                logger.info(f"Recording started - Sample rate: {SAMPLE_RATE}, Channels: {AUDIO_CHANNELS}")
            except Exception as e:
                self._is_recording = False
                logger.error(f"Failed to start recording: {e}")
                raise
    
    def stop_recording(self):
        """Stop recording and return audio data."""
        with self._lock:
            if not self._is_recording:
                logger.warning("No recording in progress")
                return None
            
            try:
                self._stream.stop()
                self._stream.close()
                self._is_recording = False
                
                # Convert buffer to numpy array
                if not self._buffer:
                    logger.warning("No audio data captured")
                    return None
                
                audio_data = np.concatenate(self._buffer, axis=0)
                logger.info(f"Recording stopped - Captured {len(audio_data)} samples ({len(audio_data)/SAMPLE_RATE:.2f}s)")
                return audio_data
            except Exception as e:
                logger.error(f"Error stopping recording: {e}")
                raise
    
    def get_audio_data(self):
        """Get the captured audio data and validate minimum duration."""
        with self._lock:
            if not self._buffer:
                raise InsufficientAudioError("No audio data available")
            
            audio_data = np.concatenate(self._buffer, axis=0)
            duration = len(audio_data) / SAMPLE_RATE
            
            if duration < MIN_RECORDING_SECONDS:
                raise InsufficientAudioError(
                    f"Recording too short ({duration:.2f}s < {MIN_RECORDING_SECONDS}s)"
                )
            
            return audio_data
    
    def _audio_callback(self, indata, frames, time, status):
        """Internal callback for continuous audio stream (runs in stream thread)."""
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        with self._lock:
            if not self._is_recording:
                return
            
            try:
                # Check buffer overflow before appending
                self._sample_count += frames
                duration = self._sample_count / SAMPLE_RATE
                
                if duration > MAX_RECORDING_SECONDS:
                    self._is_recording = False
                    logger.error(f"Recording exceeded maximum duration ({duration:.0f}s > {MAX_RECORDING_SECONDS}s)")
                    return
                
                # Copy audio data to buffer
                self._buffer.append(indata.copy())
            except Exception as e:
                logger.error(f"Error in audio callback: {e}")
                self._is_recording = False
