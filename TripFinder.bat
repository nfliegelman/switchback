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
echo  Only show routes passing through one specific camp?
set /p VIA="Via camp code or name (blank = anywhere): "
echo.
echo Searching, this can take a minute or two...
echo.

set ARGS=--start %STARTD% --end %ENDD% --nights %NIGHTS%
if not "%CODES%"=="" set ARGS=%ARGS% --codes %CODES%
if not "%VIA%"=="" set ARGS=%ARGS% --via "%VIA%"
python -m switchback trips %PARK% %ARGS%
echo.
set /p GPXN="Export a listed route to GPX? Enter its number (blank = skip): "
if not "%GPXN%"=="" (
    echo Re-running to export route %GPXN% (refetches availability, about a minute^)...
    python -m switchback trips %PARK% %ARGS% --gpx %GPXN% > nul 2>&1 || python -m switchback trips %PARK% %ARGS% --gpx %GPXN%
    echo GPX saved in the permit_exports folder.
)

echo.
pause
