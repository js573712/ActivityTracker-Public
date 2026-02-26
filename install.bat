@echo off
echo ==============================================
echo Activity Tracker ^& Summarizer Installer
echo ==============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.8 or newer from https://www.python.org/
    pause
    exit /b
)

echo [OK] Python is installed.
echo.
echo Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
    echo [OK] Virtual environment created.
) else (
    echo [INFO] Virtual environment already exists.
)

echo.
echo Installing requirements...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b
)
echo [OK] Requirements installed successfully.

if not exist ".env" (
    echo.
    echo Creating placeholder .env file...
    (
        echo GOOGLE_API_KEY=your_gemini_api_key_here
        echo # Optional: Configure polling interval in seconds (default: 60^)
        echo # POLL_INTERVAL_SECONDS=60
        echo # Optional: Configure custom database location
        echo # DB_PATH=C:\path\to\custom\activity.db
    ) > .env
    echo [INFO] Please open the .env file and add your Google Gemini API key!
) else (
    echo.
    echo [INFO] .env file already exists.
)

echo.
echo ==============================================
echo Installation Complete!
echo ==============================================
echo See README.md for instructions on how to use the tracker.
pause
