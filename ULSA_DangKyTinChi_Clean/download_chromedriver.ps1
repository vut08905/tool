# Script tự động tải ChromeDriver phù hợp với Chrome hiện tại
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "📥 TỰ ĐỘNG TẢI CHROMEDRIVER" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Tìm Chrome
$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$chromePath = $null
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        $chromePath = $path
        break
    }
}

if (-not $chromePath) {
    Write-Host "❌ Không tìm thấy Chrome!" -ForegroundColor Red
    Write-Host "📥 Hãy tải Chrome tại: https://www.google.com/chrome/" -ForegroundColor Yellow
    pause
    exit 1
}

# Lấy phiên bản Chrome
$version = (Get-Item $chromePath).VersionInfo.FileVersion
Write-Host "✅ Tìm thấy Chrome version: $version" -ForegroundColor Green

# Lấy major version (VD: 145 từ 145.0.7632.117)
$majorVersion = $version.Split('.')[0]
Write-Host "📌 Major version: $majorVersion" -ForegroundColor Cyan
Write-Host ""

# Tạo thư mục drivers
if (-not (Test-Path "drivers")) {
    New-Item -ItemType Directory -Path "drivers" | Out-Null
    Write-Host "✅ Đã tạo thư mục drivers/" -ForegroundColor Green
}

# URL tải ChromeDriver
$url = "https://storage.googleapis.com/chrome-for-testing-public/$version/win64/chromedriver-win64.zip"
$output = "drivers\chromedriver.zip"

Write-Host "📥 Đang tải ChromeDriver $version..." -ForegroundColor Yellow
Write-Host "🔗 URL: $url" -ForegroundColor Gray
Write-Host ""

try {
    # Tải file
    Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
    Write-Host "✅ Đã tải xong chromedriver.zip" -ForegroundColor Green
    
    # Giải nén
    Write-Host "📦 Đang giải nén..." -ForegroundColor Yellow
    Expand-Archive -Path $output -DestinationPath "drivers\temp" -Force
    
    # Di chuyển file
    if (Test-Path "drivers\chromedriver.exe") {
        Remove-Item "drivers\chromedriver.exe" -Force
    }
    Move-Item -Path "drivers\temp\chromedriver-win64\chromedriver.exe" -Destination "drivers\chromedriver.exe" -Force
    
    # Dọn dẹp
    Remove-Item -Path "drivers\temp" -Recurse -Force
    Remove-Item -Path $output -Force
    
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host "✅ CÀI ĐẶT THÀNH CÔNG!" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host ""
    Write-Host "📁 Vị trí: $PWD\drivers\chromedriver.exe" -ForegroundColor Cyan
    
    # Test ChromeDriver
    $testVersion = & ".\drivers\chromedriver.exe" --version
    Write-Host "🔧 Version: $testVersion" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💡 Bây giờ bạn có thể chạy lại ứng dụng!" -ForegroundColor Yellow
    
} catch {
    Write-Host ""
    Write-Host "❌ LỖI: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Hãy thử:" -ForegroundColor Yellow
    Write-Host "   1. Cập nhật Chrome lên phiên bản mới nhất" -ForegroundColor White
    Write-Host "   2. Hoặc tải ChromeDriver thủ công tại:" -ForegroundColor White
    Write-Host "      https://googlechromelabs.github.io/chrome-for-testing/" -ForegroundColor Cyan
    Write-Host "   3. Giải nén và đặt chromedriver.exe vào thư mục drivers/" -ForegroundColor White
}

Write-Host ""
pause
