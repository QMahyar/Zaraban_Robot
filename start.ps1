#!/usr/bin/env pwsh
# Zaraban Bot Launcher for PowerShell

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "   Starting Zaraban Bot" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and add your BOT_TOKEN" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if dependencies are installed
try {
    python -c "import telegram" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw
    }
} catch {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host ""
}

# Run the bot
Write-Host "Starting bot..." -ForegroundColor Green
python bot.py

Read-Host "Press Enter to exit"
