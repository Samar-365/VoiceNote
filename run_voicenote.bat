@echo off
cd /d "%~dp0"
title VoiceNote Desktop Application
echo Starting VoiceNote...
call .venv\Scripts\activate.bat
python main.py
pause
