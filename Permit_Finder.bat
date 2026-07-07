@echo off
REM ====================================================================
REM  Double-click THIS to open the Permit Availability Finder window.
REM  It launches permit_finder_gui.py from the same folder.
REM ====================================================================

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

REM pythonw runs the GUI without a black console window behind it.
start "" pythonw "%~dp0permit_finder_gui.py"
