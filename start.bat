@echo off
REM ###########################################################################
REM
REM            CFA Prep Tool - Quick Start Script (Windows)
REM
REM     Activates virtual environment and starts the application
REM
REM ###########################################################################

echo.
echo [START] Starting CFA Prep Tool...
echo.

REM Check if virtual environment exists
if not exist "cfa-venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo [OK] Activating virtual environment...
call cfa-venv\Scripts\activate.bat

REM Check if Ollama is running
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if errorlevel 1 (
    echo [WARNING] Ollama is not running!
    echo Starting Ollama...
    start "" "ollama" serve
    timeout /t 2 /nobreak >nul
    echo [OK] Ollama started
)

REM Navigate to backend
cd cfa-prep-tool\backend

REM Start the application
echo [OK] Starting CFA Prep Tool...
echo.
echo ===================================================================
echo Application will start on: http://localhost:8000
echo ===================================================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the app
python app.py
