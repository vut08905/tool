# Uninstall Python and reinstall with tkinter
# Run: .\reinstall_python_with_tkinter.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " REINSTALL PYTHON WITH TKINTER SUPPORT" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Find Python installation
$pythonPath = Join-Path $env:LOCALAPPDATA "Programs\Python\Python311"

if (Test-Path $pythonPath) {
    Write-Host "[1] Uninstalling Python 3.11.9..." -ForegroundColor Yellow
    
    $uninstallExe = Join-Path $pythonPath "python-3.11.9-amd64.exe"
    
    # Download uninstaller if not exists  
    if (-not (Test-Path $uninstallExe)) {
        Write-Host "   [*] Downloading Python installer for uninstall..." -ForegroundColor Gray
        $pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        $installerPath = Join-Path $env:TEMP "python_installer.exe"
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
        $uninstallExe = $installerPath
    }
    
    # Uninstall
    Start-Process -FilePath $uninstallExe -ArgumentList "/uninstall", "/quiet" -Wait -NoNewWindow
    Write-Host "   [OK] Uninstalled" -ForegroundColor Green
    
    # Clean up
    Start-Sleep -Seconds 3
    Remove-Item -Path $pythonPath -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "[2] Installing Python with tkinter..." -ForegroundColor Yellow

$pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
$installerPath = Join-Path $env:TEMP "python_installer.exe"

if (-not (Test-Path $installerPath)) {
    Write-Host "   [*] Downloading..." -ForegroundColor Gray
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
}

$installArgs = @(
    "/quiet",
    "InstallAllUsers=0",
    "PrependPath=1",
    "Include_test=0",
    "Include_doc=0",
    "Include_dev=0",
    "Include_tcltk=1"
)

Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait -NoNewWindow

Write-Host "   [OK] Python installed with tkinter!" -ForegroundColor Green

# Verify tkinter
Start-Sleep -Seconds 5
$pythonExe = Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"

if (Test-Path $pythonExe) {
    Write-Host ""
    Write-Host "[3] Verifying tkinter..." -ForegroundColor Yellow
    $result = & $pythonExe -c "import tkinter; print('OK')" 2>&1
    if ($result -match "OK") {
        Write-Host "   [SUCCESS] Tkinter is working!" -ForegroundColor Green
    } else {
        Write-Host "   [WARNING] Tkinter test failed: $result" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[*] Now you can run: .\CLICK_ME_TO_BUILD.bat" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close"
