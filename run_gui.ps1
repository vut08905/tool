# Chay GUI tu source - PowerShell version
# Run: .\run_gui.ps1

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " CHAY GUI TU SOURCE" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Tim Python
$pythonExe = $null

$locations = @(
    ".venv\Scripts\python.exe",
    "python",
    "py",
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe")
)

foreach ($loc in $locations) {
    try {
        if (Test-Path $loc -ErrorAction SilentlyContinue) {
            $ver = & $loc --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $pythonExe = $loc
                Write-Host "[OK] Tim thay Python: $ver" -ForegroundColor Green
                break
            }
        } elseif ($loc -in @("python", "py")) {
            $ver = & $loc --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $pythonExe = $loc
                Write-Host "[OK] Tim thay Python: $ver" -ForegroundColor Green
                break
            }
        }
    } catch {
        continue
    }
}

if (-not $pythonExe) {
    Write-Host "[ERROR] Khong tim thay Python!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vui long cai Python hoac tao venv!" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[*] Khoi dong GUI..." -ForegroundColor Cyan
Write-Host ""

& $pythonExe complete_gui.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Co loi khi chay!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
