@echo off
cd /d "F:\src\whisper-dictation"
set PYTHONPATH=%cd%
echo Lancement de Whisper Dictation...
echo Appuyez sur Alt+W pour enregistrer
echo Fermer cette fenetre pour quitter l'application
echo.
call .venv\Scripts\python.exe src\main.py
echo.
echo Application fermee.
pause
