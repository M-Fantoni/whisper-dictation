@echo off
REM Whisper Dictation Launcher for Windows
REM This script starts the app without needing VS Code

cd /d "%~dp0"
call .venv\Scripts\activate.bat
set PYTHONPATH=%cd%
python src/main.py
pause
