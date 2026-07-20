@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed yet. Open START_HERE.txt and do Step 1 first.
  pause
  exit /b
)
echo Running three real searches. This takes 2 or 3 minutes. Leave it alone.
python -m switchback calibrate rmnp --start 2026-07-20 --end 2026-07-23
python -m switchback calibrate maroonbells --start 2026-09-22 --end 2026-09-25
python -m switchback calibrate glacier --start 2026-09-08 --end 2026-09-12
echo.
echo Done. Notepad will now open your reaction sheet.
echo Type a few words after every REACTION: line, then File then Save.
notepad docs\CALIBRATION_NOTES.md
