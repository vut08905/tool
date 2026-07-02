# Auto Install Python and Build EXE
# No Unicode characters - ASCII only

$ErrorActionPreference = "Continue"

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host " AUTO INSTALL PYTHON & BUILD EXE" -ForegroundColor Cyan  
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Python config
$pythonVersion = "3.11.9"
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$installerPath = Join-Path $env:TEMP "python_installer.exe"

# Step 1: Check Python
Write-Host "[1] Checking for Python..." -ForegroundColor Yellow

$pythonExists = $false
$pythonExe = $null

$pythonDir = Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"
$testLocations = @("python", "py", $pythonDir)

foreach ($loc in $testLocations) {
    try {
        $ver = & $loc --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonExists = $true
            $pythonExe = $loc
            Write-Host "   [OK] Found Python: $ver" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

# Step 2: Download and install Python if needed
if (-not $pythonExists) {
    Write-Host "   [!] Python not found, downloading..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[2] Downloading Python $pythonVersion..." -ForegroundColor Yellow
    
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
        $sizeMB = [math]::Round((Get-Item $installerPath).Length / 1MB, 2)
        Write-Host "   [OK] Downloaded: $sizeMB MB" -ForegroundColor Green
    } catch {
        Write-Host "   [ERROR] Download failed: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host ""
    Write-Host "[3] Installing Python (automatic, no interaction needed)..." -ForegroundColor Yellow
    Write-Host "   [*] Please wait 1-2 minutes..." -ForegroundColor Gray
    
    try {
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
        
       Write-Host "   [OK] Python installation completed!" -ForegroundColor Green
        
        # Refresh PATH
        $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
        $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
        $env:Path = "$machinePath;$userPath"
        
        # Delete installer
        Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
        
        # Find Python
        Start-Sleep -Seconds 3
        
        $pythonExe = "python"
        try {
            $ver = & python --version 2>&1
            Write-Host "   [OK] Python ready: $ver" -ForegroundColor Green
        } catch {
            $pythonExe = Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"
            if (Test-Path $pythonExe) {
                Write-Host "   [OK] Python at: $pythonExe" -ForegroundColor Green
            } else {
                Write-Host "   [!] Python installed but not in PATH" -ForegroundColor Yellow
                Write-Host "   [!] Please close this PowerShell and run: .\build_exe_smart.ps1" -ForegroundColor Cyan
                Read-Host "Press Enter to exit"
                exit 0
            }
        }
        
    } catch {
        Write-Host "   [ERROR] Installation failed: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host ""
}

# Step 3: Install pip and dependencies
Write-Host "[4] Installing pip and dependencies..." -ForegroundColor Yellow

& $pythonExe -m pip install --upgrade pip --quiet --no-warn-script-location 2>$null
Write-Host "   [OK] pip" -ForegroundColor Green

& $pythonExe -m pip install pyinstaller --quiet --no-warn-script-location 2>$null
Write-Host "   [OK] pyinstaller" -ForegroundColor Green

& $pythonExe -m pip install -r requirements_full.txt --quiet --no-warn-script-location 2>$null
Write-Host "   [OK] selenium, pandas, fuzzywuzzy, etc." -ForegroundColor Green

# Step 4: Build .exe
Write-Host ""
Write-Host "[5] Building .EXE file..." -ForegroundColor Yellow
Write-Host "   [*] This takes 2-5 minutes, please be patient..." -ForegroundColor Gray
Write-Host ""

& $pythonExe -m PyInstaller --noconfirm --clean complete_gui.spec

# Step 5: Check result
Write-Host ""

if (Test-Path "dist\ULSA_DangKyTinChi.exe") {
    Write-Host "===========================================" -ForegroundColor Green
    Write-Host " SUCCESS! BUILD COMPLETED!" -ForegroundColor Green
    Write-Host "===========================================" -ForegroundColor Green
    Write-Host ""
    
    $exePath = Resolve-Path "dist\ULSA_DangKyTinChi.exe"
    $size = (Get-Item $exePath).Length
    $sizeMB = [math]::Round($size / 1MB, 2)
    
    Write-Host "[OK] File .exe: $exePath" -ForegroundColor Cyan
    Write-Host "[OK] Size: $sizeMB MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[!] YOU CAN NOW:" -ForegroundColor Yellow
    Write-Host "   1. Copy the .exe file to Desktop" -ForegroundColor White
    Write-Host "   2. Send it to friends via Zalo/Email/USB" -ForegroundColor White
    Write-Host "   3. They just double-click to run!" -ForegroundColor White
    Write-Host ""
    Write-Host "[!] NOTES FOR SHARING:" -ForegroundColor Yellow
    Write-Host "   -Users need Chrome installed" -ForegroundColor White
    Write-Host "   - First launch takes 10-30 seconds" -ForegroundColor White
    Write-Host "   - Windows warning -> Click 'Run anyway'" -ForegroundColor White
    Write-Host ""
    
    # Open folder
    Write-Host "[*] Opening dist folder..." -ForegroundColor Cyan
    Start-Process explorer.exe -ArgumentList "/select,`"$exePath`""
    
} else {
    Write-Host "===========================================" -ForegroundColor Red
    Write-Host " ERROR! BUILD FAILED!" -ForegroundColor Red
    Write-Host "===========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "[!] Check errors above and try again" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
Read-Host
