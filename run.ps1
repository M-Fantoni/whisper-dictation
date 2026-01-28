#!/usr/bin/env pwsh
# Whisper Dictation Launcher for PowerShell
# This script starts the app without needing VS Code

$scriptPath = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

# Activate virtual environment
& ".\\.venv\Scripts\Activate.ps1"

# Set Python path
$env:PYTHONPATH = $pwd.Path

# Run the app
Write-Host "Starting Whisper Dictation..." -ForegroundColor Green
Write-Host "Press Alt+W to start recording" -ForegroundColor Cyan
python src/main.py

# Keep window open on error
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: App exited with code $LASTEXITCODE" -ForegroundColor Red
    Read-Host "Press Enter to close..."
}
