@echo off
REM ====================================================================
REM  Double-click THIS to search for bookable trips.
REM  It's a thin wrapper around: python -m switchback trips ...
REM  Your saved effort limits (miles/gain) live in profile.json, editable
REM  in Notepad. This window is a stopgap for M6; it will be replaced by
REM  a real button in the GUI and eventually the web UI.
REM ====================================================================

python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed, or not on your PATH.
    pause
    exit /b
)

echo ====================================================================
echo  Switchback Trip Finder
echo ====================================================================
echo.
echo  Park slugs available: check the parks folder for ^<slug^>.json
echo  Right now that means: glacier, rainier
echo.
set /p PARK="Park slug: "
set /p STARTD="Start date, earliest you could leave (YYYY-MM-DD): "
set /p ENDD="End date, latest you could leave (YYYY-MM-DD): "
set /p NIGHTS="Nights (blank = 3): "
if "%NIGHTS%"=="" set NIGHTS=3
echo.
echo  Leave blank to search EVERY camp in the park (can be slow).
echo  Or list camp codes to narrow it, comma separated, e.g. ELF,COS,GLF
set /p CODES="Camp codes (blank = all): "
echo.
echo Searching, this can take a minute or two...
echo.

if "%CODES%"=="" (
    python -m switchback trips %PARK% --start %STARTD% --end %ENDD% --nights %NIGHTS%
) else (
    python -m switchback trips %PARK% --start %STARTD% --end %ENDD% --nights %NIGHTS% --codes %CODES%
)

echo.
pause
