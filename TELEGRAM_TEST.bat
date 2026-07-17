@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed yet. Open START_HERE.txt and do Step 1 first.
  pause
  exit /b
)
if not exist telegram.json (
  copy telegram.json.example telegram.json >nul
  echo Notepad will open telegram.json. Replace the two placeholder
  echo values with your bot token and chat id, the same two things you
  echo pasted into GitHub secrets. Then File, Save, close Notepad,
  echo and double-click this file AGAIN.
  notepad telegram.json
  exit /b
)
echo Sending one test alert to your Telegram...
python -m switchback watch glacier --inject --once
echo If a Telegram message just arrived, this test passed.
pause
