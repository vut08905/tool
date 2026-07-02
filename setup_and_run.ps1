# Script tự động cài đặt Python và chạy chương trình
Write-Host "=== SETUP AND RUN AUTOMATION ===" -ForegroundColor Green

# Kiểm tra Python
$pythonExists = $false
$pythonPaths = @(
    "C:\Python313\python.exe",
    "C:\Python312\python.exe", 
    "C:\Python311\python.exe",
    "C:\Python310\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
)

$pythonCmd = $null
foreach ($path in $pythonPaths) {
    if (Test-Path $path) {
        $pythonCmd = $path
        $pythonExists = $true
        Write-Host "Found Python at: $path" -ForegroundColor Green
        break
    }
}

if (-not $pythonExists) {
    Write-Host "Python not found! Installing via winget..." -ForegroundColor Yellow
    
    # Cài Python qua winget
    Write-Host "Installing Python 3.13..." -ForegroundColor Yellow
    winget install Python.Python.3.13 -e --silent --accept-source-agreements --accept-package-agreements
    
    # Đợi cài xong và refresh PATH
    Start-Sleep -Seconds 10
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # Tìm lại Python
    foreach ($path in $pythonPaths) {
        if (Test-Path $path) {
            $pythonCmd = $path
            $pythonExists = $true
            Write-Host "Python installed at: $path" -ForegroundColor Green
            break
        }
    }
}

if (-not $pythonExists) {
    Write-Host "ERROR: Cannot find or install Python!" -ForegroundColor Red
    Write-Host "Please download and install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    pause
    exit 1
}

# Kiểm tra và tạo lại virtual environment
$venvPath = "d:\webtruong4.1\.venv"
Write-Host "Setting up virtual environment..." -ForegroundColor Yellow

if (Test-Path $venvPath) {
    Write-Host "Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item -Path $venvPath -Recurse -Force
}

Write-Host "Creating new virtual environment..." -ForegroundColor Yellow
& $pythonCmd -m venv $venvPath

# Activate venv và cài packages
$venvPython = "$venvPath\Scripts\python.exe"
Write-Host "Installing required packages..." -ForegroundColor Yellow

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install selenium webdriver-manager pandas fuzzywuzzy python-Levenshtein openpyxl

Write-Host "`n=== SETUP COMPLETE! ===" -ForegroundColor Green
Write-Host "Running complete_gui.py..." -ForegroundColor Cyan

# Chạy GUI
& $venvPython "d:\webtruong4.1\complete_gui.py"

Write-Host "`nProgram finished." -ForegroundColor Green
pause
