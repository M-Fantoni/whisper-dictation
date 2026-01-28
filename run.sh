#!/bin/bash
# Whisper Dictation Launcher for Linux/macOS
# This script starts the app without needing VS Code

cd "$(dirname "$0")"
source .venv/bin/activate
export PYTHONPATH="$(pwd)"
python src/main.py
