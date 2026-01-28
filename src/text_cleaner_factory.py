"""
Factory for creating text cleaner instances.
Handles backend selection and initialization with proper error handling.
"""

import logging
from src.text_cleaner_base import TextCleanerBase
from src.text_cleaner_openai import OpenAITextCleaner
from src.text_cleaner_ollama import OllamaTextCleaner

logger = logging.getLogger(__name__)


class TextCleanerFactory:
    """Factory for creating text cleaner instances based on configuration."""
    
    @staticmethod
    def create(backend: str, **kwargs) -> TextCleanerBase:
        """
        Create a text cleaner instance based on backend type.
        
        Args:
            backend: Backend type ('openai', 'ollama', or 'disabled')
            **kwargs: Additional arguments for specific backends
                For Ollama:
                    - model_name: Model to use (default: llama3.2:3b)
                    - base_url: Ollama server URL (default: http://localhost:11434)
        
        Returns:
            TextCleanerBase instance
            
        Raises:
            ValueError: If backend is invalid or configuration is missing
        """
        backend = backend.lower().strip()
        
        if backend == "disabled":
            logger.info("Text cleaner disabled")
            return None
        
        elif backend == "openai":
            logger.info("Creating OpenAI text cleaner")
            try:
                cleaner = OpenAITextCleaner()
                if not cleaner.is_available():
                    raise ValueError("OpenAI API key not configured")
                return cleaner
            except Exception as e:
                raise ValueError(f"Failed to initialize OpenAI text cleaner: {e}")
        
        elif backend == "ollama":
            logger.info("Creating Ollama text cleaner")
            try:
                model_name = kwargs.get("model_name", "llama3.2:3b")
                base_url = kwargs.get("base_url", "http://localhost:11434")
                
                cleaner = OllamaTextCleaner(model_name=model_name, base_url=base_url)
                
                if not cleaner.is_available():
                    raise ValueError(
                        f"Ollama not available. Make sure:\n"
                        f"1. Ollama is installed and running\n"
                        f"2. Model '{model_name}' is downloaded: ollama pull {model_name}"
                    )
                return cleaner
            except Exception as e:
                raise ValueError(f"Failed to initialize Ollama text cleaner: {e}")
        
        else:
            raise ValueError(
                f"Invalid TEXT_CLEANER_BACKEND: '{backend}'. "
                f"Valid options: 'openai', 'ollama', 'disabled'"
            )
