@echo off
echo Starting ExconAI RAG Chatbot...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install requirements if needed
if not exist "requirements_installed.flag" (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 0 (
        echo. > requirements_installed.flag
    ) else (
        echo Failed to install requirements
        pause
        exit /b 1
    )
)

REM Start the application
echo Starting Streamlit application...
echo The application will open in your web browser
echo Press Ctrl+C to stop the application
echo.
python run_chatbot.py

pause
