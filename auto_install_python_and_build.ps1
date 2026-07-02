# Script tu dong: Tai Python va Build .exe
# Chay: .\auto_install_python_and_build.ps1

$ErrorActionPreference = "Continue"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "[*] TU DONG CAI PYTHON VA BUILD .EXE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Cấu hình Python
$pythonVersion = "3.11.9"
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$installerPath = "$env:TEMP\python_installer.exe"

# Buoc 1: Kiem tra Python
Write-Host "[1] Kiem tra Python..." -ForegroundColor Yellow

$pythonExists = $false
$pythonExe = $null

# Thu cac vi tri Python
$pythonDir = Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"
$testLocations = @("python", "py", $pythonDir)

foreach ($loc in $testLocations) {
    try {
        $ver = & $loc --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonExists = $true
            $pythonExe = $l[OK] Da co
            Write-Host "   ✅ Đã có Python: $ver" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}
uoc 2: Tai va cai Python neu chua co
if (-not $pythonExists) {
    Write-Host "   [!] Chua co Python, bat dau tai ve..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[2] Ta
    Write-Host "📥 Bước 2: Tải Python $pythonVersion..." -ForegroundColor Yellow
    
    try {
        # Tải Python installer
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
        $sizeMB = [math]::Round((Get-Item $installerPath).Length / 1MB, 2)
        Write-Host "   [OK] Da tai xong: $sizeMB MB" -ForegroundColor Green
    } catch {
        Write-Host "   [ERROR] Loi khi tai Python: $_" -ForegroundColor Red
        pause
        exit 1
    }
    
    Write-Host "[3] Cai dat Python (tu dong, khong can thao tac)..." -ForegroundColor Yellow
    Write-Host "   [*] Doi khoang 1-2 phuon (tự động, không cần thao tác)..." -ForegroundColor Yellow
    Write-Host "   ⏳ Đợi khoảng 1-2 phút..." -ForegroundColor Gray
    
    try {
        # Cài Python với các tùy chọn:
        # - InstallAllUsers=0: Chỉ cài cho user hiện tại (không cần admin)
        # - PrependPath=1: Thêm Python vào PATH
        # - Include_test=0: Không cài test suite
        # - SimpleInstall=1: Cài đặt đơn giản
        
        $installArgs = @(
            "/quiet",
            "InstallAllUsers=0",
            "PrependPath=1",
            "Include_test=0",
            "Include_doc=0",
            "Include_dev=0",
            "Include_tcltk=0"
        )
        
        Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait -NoNewWindow
        [OK] Cai dat Python hoan tat!" -ForegroundColor Green
        
        # Refresh PATH
        $machinePath = [System.Environment]::GetEnvironmentVariable("Path","Machine")
        $userPath = [System.Environment]::GetEnvironmentVariable("Path","User")
        $env:Path = "$machinePath;$userPath"
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Xóa installer
        Remove-Item $installerPath -Force
        
        # Tìm Python vừa cài
        Start-Sleep -Seconds 3
        
        $pythonExe = "python"
        try {
            $ver = & python --version 2>&1
            Write-Host "   [OK] Python da san sang: $ver" -ForegroundColor Green
        } catch {
            # Thu duong dan mac dinh
            $pythonExe = Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"
            if (Test-Path $pythonExe) {
                Write-Host "   [OK] Python tai: $pythonExe" -ForegroundColor Green
            } else {
                Write-Host "   [!] Cai Python xong nhung chua thay trong PATH" -ForegroundColor Yellow
                Write-Host "   [!] Vui long dong PowerShell nay va mo lai, roi chay: .\build_exe_smart.ps1" -ForegroundColor Cyan
                pause
                exit 0
            }
        }
        
    } catch {
        Write-Host "   [ERROR] Loi khi cai Python: $_" -ForegroundColor Red
        pause
        exit 1
    }
} else {
    Write-Host ""
}

# Buoc 3: Cai pip va dependencies
Write-Host "[4] Cai dat pip va cac thu vien can thiet..." -ForegroundColor Yellow

& $pythonExe -m pip install --upgrade pip --quiet --no-warn-script-location
Write-Host "   [OK] pip" -ForegroundColor Green

& $pythonExe -m pip install pyinstaller --quiet --no-warn-script-location
Write-Host "   [OK] pyinstaller" -ForegroundColor Green

& $pythonExe -m pip install -r requirements_full.txt --quiet --no-warn-script-location
Write-Host "   [OK] selenium, pandas, fuzzywuzzy, etc." -ForegroundColor Green

# Buoc 4: Build .exe
Write-Host ""
Write-Host "[5] Build file .EXE..." -ForegroundColor Yellow
Write-Host "   [*] Qua trinh nay mat 2-5 phut, xin kien nhan..." -ForegroundColor Gray
Write-Host ""

& $pythonExe -m PyInstaller --noconfirm --clean complete_gui.spec

# Buoc 5: Kiem tra ket qua
Write-Host ""

if (Test-Path "dist\ULSA_DangKyTinChi.exe") {
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "[SUCCESS] HOAN THANH!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    
    $exePath = Resolve-Path "dist\ULSA_DangKyTinChi.exe"
    $size = (Get-Item $exePath).Length
    $sizeMB = [math]::Round($size / 1MB, 2)
    
    Write-Host "[OK] File .exe: $exePath" -ForegroundColor Cyan
    Write-Host "[OK] Kich thuoc: $sizeMB MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[!] BAY GIO BAN CO THE:" -ForegroundColor Yellow
    Write-Host "   1. Copy file .exe ra Desktop" -ForegroundColor White
    Write-Host "   2. Gui cho ban be qua Zalo/Email/USB" -ForegroundColor White
    Write-Host "   3. Ho chi can click dup la chay ngay!" -ForegroundColor White
    Write-Host ""
    Write-Host "[!] LUU Y KHI CHIA SE:" -ForegroundColor Yellow
    Write-Host "   - Nguoi dung can co Chrome da cai" -ForegroundColor White
    Write-Host "   - Lan dau khoi dong mat 10-30 giay" -ForegroundColor White
    Write-Host "   - Windows canh bao -> Click 'Run anyway'" -ForegroundColor White
    Write-Host ""
    
    # Mo folder chua file .exe
    Write-Host "[*] Mo folder dist/..." -ForegroundColor Cyan
    Start-Process explorer.exe -ArgumentList "/select,`"$exePath`""
    
} else {
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "[ERROR] BUILD THAT BAI!" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "[!] Kiem tra loi o tren va thu lai" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""
Write-Host "Nhan phim bat ky de dong..." -ForegroundColor Gray
pause
