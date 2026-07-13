@echo off
cd /d "%~dp0"
python -m pip show fastapi >nul 2>&1 || python -m pip install fastapi uvicorn
start "" http://localhost:8756
python -m uvicorn switchback.web:app --port 8756
