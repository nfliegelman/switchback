@echo off
REM ====================================================================
REM  Double-click THIS. Switchback opens in your web browser.
REM  Same app as the phone, with the full engine behind it.
REM ====================================================================
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Python is not installed yet. One-time setup:
    echo  1. Go to https://www.python.org/downloads/ and install it.
    echo  2. During setup, CHECK the box "Add python.exe to PATH".
    echo  3. Double-click this file again.
    echo.
    pause
    exit /b
)

python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo First run only: setting up the local map, about thirty seconds...
    python -m pip install --user --quiet fastapi uvicorn
)

start "" pythonw -m uvicorn switchback.web:app --port 8756
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8756
