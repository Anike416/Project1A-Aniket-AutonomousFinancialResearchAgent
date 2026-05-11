#!/usr/bin/env pwsh
# PowerShell script to run ARA-1 Streamlit Dashboard

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   ARA-1 Streamlit Dashboard Launcher" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "myenv")) {
    Write-Host "✗ Virtual environment 'myenv' not found" -ForegroundColor Red
    Write-Host "Please run: python -m venv myenv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\myenv\Scripts\Activate.ps1

# Install/update dependencies
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt

# Run Streamlit
Write-Host ""
Write-Host "Starting ARA-1 Dashboard..." -ForegroundColor Green
Write-Host "Dashboard will open at: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

streamlit run app.py `
    --theme.primaryColor="#0D47A1" `
    --theme.backgroundColor="#F5F5F5" `
    --theme.secondaryBackgroundColor="#FFFFFF" `
    --theme.textColor="#262730" `
    --theme.font="sans serif"

Read-Host "Press Enter to exit"
