@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed yet. Open START_HERE.txt and do Step 1 first.
  pause
  exit /b
)
echo Installing the two GUI extras if needed, then launching...
python -m pip install --quiet customtkinter openpyxl
python switchback_gui.py
pause
