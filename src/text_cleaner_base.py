"""
Base interface for text cleaning implementations.
Defines contract for all text cleaner backends.
"""

from abc import ABC, abstractmethod


class TextCleanerBase(ABC):
    """Abstract base class for text cleaning implementations."""
    
    @abstractmethod
    def clean(self, raw_text: str) -> str:
        """
        Clean raw transcribed text.
        
        Args:
            raw_text: Raw transcribed text from Whisper
            
        Returns:
            Cleaned text
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the backend is available and properly configured.
        
        Returns:
            True if backend can be used, False otherwise
        """
        pass
