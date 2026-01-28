"""
OpenAI-based text cleaning implementation.
Cleans transcribed text using OpenAI GPT models.
"""

import logging
import time
from openai import OpenAI
from src.text_cleaner_base import TextCleanerBase
from src.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TIMEOUT

logger = logging.getLogger(__name__)


class OpenAITextCleaner(TextCleanerBase):
    """Cleans transcribed text using OpenAI API with fallback to raw text."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required for OpenAI text cleaner")
        
        self._client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Validate API key format
        if not OPENAI_API_KEY.startswith("sk-"):
            logger.warning(f"API key may be invalid - should start with 'sk-'")
        
        logger.info(f"OpenAI text cleaner initialized with model: {OPENAI_MODEL}")
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        return bool(OPENAI_API_KEY)
    
    def clean(self, raw_text: str) -> str:
        """
        Clean raw transcribed text using OpenAI API.
        
        Falls back to raw text if API fails.
        
        Args:
            raw_text: Raw transcribed text from Whisper
            
        Returns:
            Cleaned text (or raw text if API fails)
        """
        if not raw_text or not raw_text.strip():
            logger.warning("Empty text provided to cleaner")
            return raw_text
        
        try:
            start_time = time.time()
            logger.info(f"Cleaning text with OpenAI (length: {len(raw_text)})")
            
            # System prompt for consistent French text cleaning
            system_prompt = (
                "Tu es un assistant de correction de texte français. "
                "Supprime les mots de remplissage (euh, hum, ben, voilà, etc.), "
                "corrige la grammaire, ajoute la ponctuation appropriée et les majuscules. "
                "Garde le sens exact du texte original. "
                "Ne traduis pas, ne résume pas. "
                "Retourne uniquement le texte corrigé sans commentaire."
            )
            
            user_prompt = f"Texte à corriger: {raw_text}"
            
            # Call OpenAI API with timeout
            response = self._client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,  # Deterministic output
                timeout=OPENAI_TIMEOUT
            )
            
            cleaned_text = response.choices[0].message.content.strip()
            elapsed = time.time() - start_time
            
            logger.info(f"Text cleaned with OpenAI ({elapsed:.2f}s)")
            return cleaned_text
        
        except Exception as e:
            logger.error(f"OpenAI text cleaning failed: {e}")
            logger.warning("Falling back to raw transcribed text")
            return raw_text
