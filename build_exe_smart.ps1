# PowerShell Script - Build EXE with automatic Python detection
# Run: .\build_exe_smart.ps1

$scriptRoot = $PSScriptRoot
Set-Location $scriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BUILD FILE .EXE - SMART VERSION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find Python
$pythonExe = $null

$locations = @(
    (Join-Path $scriptRoot ".venv\Scripts\python.exe"),
    (Join-Path $scriptRoot ".venv_build\Scripts\python.exe")
)

foreach ($loc in $locations) {
    try {
        $version = & $loc --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonExe = $loc
            Write-Host "Found Python: $loc" -ForegroundColor Green
            Write-Host "   Version: $version" -ForegroundColor Gray
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonExe) {
    Write-Host "PYTHON NOT FOUND!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Create or restore the project .venv before building." -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow

& $pythonExe -m pip install --upgrade pip --quiet
& $pythonExe -m pip install pyinstaller --quiet
& $pythonExe -m pip install -r (Join-Path $scriptRoot "requirements_full.txt") --quiet

Write-Host ""
Write-Host "Building EXE..." -ForegroundColor Yellow
Write-Host "Please wait 2-5 minutes..." -ForegroundColor Gray
Write-Host ""

& $pythonExe -m PyInstaller --noconfirm --clean (Join-Path $scriptRoot "complete_gui.spec")

Write-Host ""

if (Test-Path "dist\dangkytinchi_baomat.exe") {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "BUILD SUCCESS" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    $exePath = Resolve-Path "dist\dangkytinchi_baomat.exe"
    $size = (Get-Item $exePath).Length
    $sizeMB = [math]::Round($size / 1MB, 2)
    
    Write-Host "EXE file: $exePath" -ForegroundColor Cyan
    Write-Host "Size: $sizeMB MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now:" -ForegroundColor Yellow
    Write-Host "   1. Copy the EXE to Desktop to test"
    Write-Host "   2. Share the file with others"
    Write-Host "   3. Recipients can double-click to run"
    Write-Host ""
    Write-Host "Notes:" -ForegroundColor Yellow
    Write-Host "   - Chrome must be installed"
    Write-Host "   - First launch may take 10-30s"
    Write-Host "   - If Windows warns, click 'Run anyway'"
    Write-Host ""
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "BUILD FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the errors above and try again." -ForegroundColor Yellow
}

pause
