# PowerShell script to run automation
Write-Host "🚀 Starting ULSA Automation with improved B2 logic..." -ForegroundColor Green
Write-Host "📁 Changing to directory..." -ForegroundColor Yellow

Set-Location $PSScriptRoot
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan

$pythonPath = ".\automation\.venv\Scripts\python.exe"
$scriptPath = ".\automation\auto_login_with_title_check.py"

Write-Host "🐍 Python path: $pythonPath" -ForegroundColor Yellow
Write-Host "📄 Script path: $scriptPath" -ForegroundColor Yellow

if (Test-Path $pythonPath) {
    Write-Host "✅ Python executable found!" -ForegroundColor Green
} else {
    Write-Host "❌ Python executable not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (Test-Path $scriptPath) {
    Write-Host "✅ Script file found!" -ForegroundColor Green
} else {
    Write-Host "❌ Script file not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🚀 Starting automation..." -ForegroundColor Green
try {
    & $pythonPath $scriptPath
    Write-Host "✅ Script completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error running script: $_" -ForegroundColor Red
}

Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host
