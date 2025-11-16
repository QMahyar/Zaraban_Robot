@echo off
echo ====================================
echo   Starting Zaraban Bot
echo ====================================
echo.

REM Check if .env exists
if not exist .env (
    echo Error: .env file not found!
    echo Please copy .env.example to .env and add your BOT_TOKEN
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import telegram" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Run the bot
python bot.py

pause
