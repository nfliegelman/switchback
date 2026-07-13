@echo off
REM ====================================================================
REM  Double-click THIS for the classic window: the availability grid
REM  and the styled Excel export. The map app is Switchback.bat.
REM ====================================================================
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Python is not installed, or not on your PATH.
    echo  Install from https://www.python.org/downloads/  and during setup
    echo  CHECK the box "Add python.exe to PATH", then try again.
    echo.
    pause
    exit /b
)

start "" pythonw "%~dp0switchback_gui.py"
