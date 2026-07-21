@echo off
REM ====================================================================
REM  Double-click THIS. Switchback opens in your web browser.
REM  A second window titled "Switchback server" runs the app;
REM  close that window (or click Quit in the app) to shut it down.
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

REM Run the server with visible python (NOT pythonw): uvicorn needs a
REM console to write to, and a visible window means any error is seen,
REM not swallowed. This window is what keeps Switchback running.
echo Starting Switchback...
start "Switchback server" python -m uvicorn switchback.web:app --port 8756

REM Open the browser only once the server actually answers, instead of
REM guessing with a fixed delay.
echo Waiting for the server to be ready...
set /a _tries=0
:sbwait
timeout /t 1 /nobreak >nul
python -c "import socket,sys; s=socket.socket(); s.settimeout(1); sys.exit(0 if s.connect_ex(('127.0.0.1',8756))==0 else 1)" >nul 2>&1
if not errorlevel 1 goto sbready
set /a _tries+=1
if %_tries% geq 30 goto sbfail
goto sbwait

:sbready
start "" http://127.0.0.1:8756
exit /b

:sbfail
echo.
echo  Switchback did not start in time. Look at the window titled
echo  "Switchback server" for the error message and send it to Claude.
echo.
pause
exit /b
