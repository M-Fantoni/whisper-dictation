"""
Transcription module using faster-whisper.
Converts audio to text using Whisper model with optional download progress callback.
"""

import logging
import time
from faster_whisper import WhisperModel
from src.config import WHISPER_MODEL, WHISPER_LANGUAGE

logger = logging.getLogger(__name__)


class Transcriber:
    """Wraps faster-whisper WhisperModel for audio transcription."""
    
    def __init__(self, download_callback=None):
        """
        Initialize transcriber with optional download progress callback.
        
        Args:
            download_callback: Optional callable(progress_percent) for model download progress.
        """
        self._model = None
        self._download_callback = download_callback
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Whisper model, calling download callback during first load."""
        try:
            logger.info(f"Loading Whisper model: {WHISPER_MODEL}")
            
            # Loading model with cpu_threads for better performance
            self._model = WhisperModel(
                WHISPER_MODEL,
                device="cpu",
                compute_type="float32",
                download_root=None,  # Use default cache directory
                num_workers=1
            )
            logger.info(f"Model loaded successfully: {WHISPER_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe(self, audio_data):
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: numpy array of audio samples at SAMPLE_RATE
            
        Returns:
            Transcribed text string
        """
        if self._model is None:
            raise RuntimeError("Model not initialized")
        
        try:
            start_time = time.time()
            logger.info(f"Transcribing audio ({len(audio_data)/16000:.2f}s)")
            
            # Transcribe with language constraint
            segments, info = self._model.transcribe(
                audio_data,
                language=WHISPER_LANGUAGE,
                beam_size=5,
                temperature=0
            )
            
            # Collect all segments
            text = " ".join(segment.text for segment in segments).strip()
            
            elapsed = time.time() - start_time
            logger.info(f"Transcription complete ({elapsed:.2f}s): '{text[:100]}...'")
            
            return text
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
