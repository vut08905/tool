# ULSA Login Automation PowerShell Script
# Run with: powershell -ExecutionPolicy Bypass -File run.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   ULSA UNIVERSITY LOGIN AUTOMATION        " -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Set location to script directory
Set-Location $PSScriptRoot

# Check if Python virtual environment exists
$pythonPath = "..\\.venv\\Scripts\\python.exe"
if (Test-Path $pythonPath) {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    $python = $pythonPath
} else {
    Write-Host "! Using system Python" -ForegroundColor Yellow
    $python = "python"
}

# Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Blue

try {
    & $python -c "import selenium, webdriver_manager; print('✓ All packages ready')"
    Write-Host "✓ Dependencies OK" -ForegroundColor Green
} catch {
    Write-Host "! Installing missing packages..." -ForegroundColor Yellow
    & $python -m pip install -r requirements.txt
}

Write-Host ""
Write-Host "Starting ULSA Automation..." -ForegroundColor Blue
Write-Host ""

# Run the automation script
try {
    & $python ulsa_auto_login.py
} catch {
    Write-Host "Error running automation: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   AUTOMATION COMPLETED                    " -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
