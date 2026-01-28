"""
Application configuration module.
Loads environment variables and sets up logging.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration Constants
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "fr")
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
HOTKEY = os.getenv("HOTKEY", "<alt>+w")
MAX_RECORDING_SECONDS = int(os.getenv("MAX_RECORDING_SECONDS", "300"))
MIN_RECORDING_SECONDS = float(os.getenv("MIN_RECORDING_SECONDS", "0.5"))

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found in environment. "
        "Please set it in .env file or as environment variable."
    )

OPENAI_MODEL = "gpt-4o-mini"
OPENAI_TIMEOUT = 10

# GUI Configuration
GUI_WINDOW_WIDTH = 200
GUI_WINDOW_HEIGHT = 80
GUI_ERROR_DISPLAY_MS = 3000

# Audio Configuration
AUDIO_CHANNELS = 1
AUDIO_DTYPE = "int16"

# Logging Configuration
def setup_logging():
    """Configure logging to file and console."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler("whisper-dictation.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Add handlers to logger
    if not logger.handlers:  # Avoid duplicate handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Initialize logging on module import
logger = setup_logging()
logger.info(f"Whisper Dictation initialized - Model: {WHISPER_MODEL}, Language: {WHISPER_LANGUAGE}")
