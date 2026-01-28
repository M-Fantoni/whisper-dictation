"""
Ollama-based text cleaning implementation.
Cleans transcribed text using local Ollama models.
"""

import logging
import time
import requests
from src.text_cleaner_base import TextCleanerBase

logger = logging.getLogger(__name__)


class OllamaTextCleaner(TextCleanerBase):
    """Cleans transcribed text using local Ollama models with fallback to raw text."""
    
    def __init__(self, model_name: str = "llama3.2:3b", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client.
        
        Args:
            model_name: Name of Ollama model to use (default: llama3.2:3b)
            base_url: Base URL of Ollama server (default: http://localhost:11434)
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
        logger.info(f"Ollama text cleaner initialized with model: {model_name}")
    
    def is_available(self) -> bool:
        """Check if Ollama server is running and model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                is_available = self.model_name in model_names
                
                if not is_available:
                    logger.warning(
                        f"Ollama model '{self.model_name}' not found. "
                        f"Available models: {model_names}. "
                        f"Run: ollama pull {self.model_name}"
                    )
                return is_available
            return False
        except Exception as e:
            logger.warning(f"Ollama server not available: {e}")
            return False
    
    def clean(self, raw_text: str) -> str:
        """
        Clean raw transcribed text using Ollama.
        
        Falls back to raw text if Ollama fails.
        
        Args:
            raw_text: Raw transcribed text from Whisper
            
        Returns:
            Cleaned text (or raw text if Ollama fails)
        """
        if not raw_text or not raw_text.strip():
            logger.warning("Empty text provided to cleaner")
            return raw_text
        
        try:
            start_time = time.time()
            logger.info(f"Cleaning text with Ollama (length: {len(raw_text)})")
            
            # Prompt for French text cleaning (strict format to prevent hallucinations)
            prompt = (
                "Tu es un correcteur de texte. Corrige CE TEXTE EXACTEMENT sans rien inventer.\n\n"
                f"TEXTE ORIGINAL: {raw_text}\n\n"
                "INSTRUCTIONS:\n"
                "1. Supprime uniquement les mots de remplissage (euh, hum, ben, voilà)\n"
                "2. Corrige la ponctuation et les majuscules\n"
                "3. Ne change PAS le sens\n"
                "4. N'invente AUCUN mot nouveau\n"
                "5. Retourne UNIQUEMENT le texte corrigé\n\n"
                "TEXTE CORRIGÉ:"
                "Texte corrigé:"
            )
            
            # Call Ollama API
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,  # Deterministic
                        "num_predict": 500   # Max tokens
                    }
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            result = response.json()
            cleaned_text = result.get("response", "").strip()
            
            if not cleaned_text:
                raise Exception("Empty response from Ollama")
            
            elapsed = time.time() - start_time
            logger.info(f"Text cleaned with Ollama ({elapsed:.2f}s)")
            
            return cleaned_text
        
        except Exception as e:
            logger.error(f"Ollama text cleaning failed: {e}")
            logger.warning("Falling back to raw transcribed text")
            return raw_text
