@echo off
REM Windows Setup Script for Wellbeing AI Companion
REM Run this script after cloning the repository on Windows

echo Setting up Wellbeing AI Companion on Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create data directory
echo Creating data directory...
if not exist "data\memory" mkdir data\memory

REM Check Ollama
echo.
echo Checking Ollama installation...
where ollama >nul 2>&1
if errorlevel 1 (
    echo Ollama is not installed.
    echo.
    echo To install Ollama on Windows:
    echo 1. Download from: https://ollama.com/download/windows
    echo 2. Run the installer
    echo 3. Restart this script
    echo.
    pause
    exit /b 1
) else (
    echo Ollama is installed
)

REM Pull the model
echo.
echo Pulling phi3:mini model (this may take a while)...
ollama pull phi3:mini

REM Display completion message
echo.
echo Setup complete!
echo.
echo To run the terminal version:
echo    venv\Scripts\activate
echo    python main.py
echo.
echo To run the web interface:
echo    venv\Scripts\activate
echo    python web_app.py
echo    Then open: http://localhost:5000
echo.
echo Enjoy your Wellbeing AI Companion!
pause
