"""
Text cleaning module using OpenAI API.
Cleans transcribed text by removing filler words and correcting grammar.
"""

import logging
import time
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TIMEOUT

logger = logging.getLogger(__name__)


class TextCleaner:
    """Cleans transcribed text using OpenAI API with fallback to raw text."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self._client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Validate API key format (should start with sk-)
        if not OPENAI_API_KEY.startswith("sk-"):
            logger.warning(f"API key may be invalid - should start with 'sk-' but got '{OPENAI_API_KEY[:10]}...'")
        
        logger.debug(f"OpenAI client initialized with model: {OPENAI_MODEL}")
    
    def clean(self, raw_text):
        """
        Clean raw transcribed text by removing filler words and fixing grammar.
        
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
            logger.info(f"Cleaning text (length: {len(raw_text)}): '{raw_text[:50]}...'")
            
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
            
            logger.info(f"Text cleaned ({elapsed:.2f}s): '{cleaned_text[:100]}...'")
            return cleaned_text
        
        except Exception as e:
            logger.error(f"Error during text cleaning: {e}")
            logger.warning("Falling back to raw transcribed text")
            return raw_text
