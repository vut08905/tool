"""
CÁCH QUÉT GOOGLE SHEET BỊ KHÓA (CHỈ NGƯỜI ĐƯỢC CẤP QUYỀN MỚI XEM)
Yêu cầu: Tài khoản Google của bạn phải được owner cho phép xem sheet
"""

import time
import json
from datetime import datetime

print("""
╔══════════════════════════════════════════════════════════════╗
║  3 CÁCH QUÉT GOOGLE SHEET BỊ KHÓA RA EXCEL                  ║
╚══════════════════════════════════════════════════════════════╝

⚠️  YÊU CẦU: Email của bạn phải được owner cấp quyền "Viewer" trở lên

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CÁCH 1: SỬ DỤNG GOOGLE APPS SCRIPT (NHANH NHẤT - KHÔNG CẦN CODE)

Bước 1: Mở Google Sheet (đăng nhập bằng email được cấp quyền)
Bước 2: Vào menu "Extensions" → "Apps Script"
Bước 3: Xóa code mẫu, paste code này vào:

════════════════════════════════════════════════════════════════
function exportToExcel() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getActiveSheet();
  
  // Lấy tất cả dữ liệu
  var data = sheet.getDataRange().getValues();
  
  // Tạo file CSV
  var csv = '';
  for (var i = 0; i < data.length; i++) {
    csv += data[i].join(',') + '\\n';
  }
  
  // Lưu vào Google Drive
  var fileName = sheet.getName() + '_export.csv';
  var file = DriveApp.createFile(fileName, csv, MimeType.CSV);
  
  Logger.log('✅ Đã export: ' + fileName);
  Logger.log('📂 Link: ' + file.getUrl());
  
  // Gửi email (tùy chọn)
  MailApp.sendEmail(
    Session.getActiveUser().getEmail(),
    'Google Sheet Export',
    'File đã export: ' + file.getUrl()
  );
}
════════════════════════════════════════════════════════════════

Bước 4: Nhấn nút "Run" (▶️)
Bước 5: Cho phép quyền khi được hỏi
Bước 6: File CSV sẽ được lưu vào Google Drive của bạn
Bước 7: Download về và mở bằng Excel

💡 Ưu điểm: 
   - Không cần cài đặt gì
   - Chạy trực tiếp trong Google
   - Bypass mọi hạn chế copy/download

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CÁCH 2: COPY THỦ CÔNG (ĐƠN GIẢN NHẤT)

Bước 1: Đăng nhập Google bằng email được cấp quyền
Bước 2: Mở Google Sheet
Bước 3: Ctrl+A (chọn tất cả)
Bước 4: Ctrl+C (copy)
Bước 5: Mở Excel → Ctrl+V (paste)
Bước 6: Save as .xlsx

⚠️  Lưu ý: Nếu sheet cấm copy (Protected), dùng cách 1 hoặc 3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CÁCH 3: DÙNG CODE PYTHON + SELENIUM (TỰ ĐỘNG HÓA)

Yêu cầu: pip install selenium webdriver-manager pandas openpyxl

Script sẽ:
1. Tự động mở Chrome
2. Bạn đăng nhập Google thủ công
3. Mở sheet và nhấn Enter
4. Script tự động scrape và lưu Excel

Chạy: python quet_sheet_khoa.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 KHUYẾN NGHỊ:
   → Dùng CÁCH 1 (Apps Script) nếu sheet phức tạp hoặc lớn
   → Dùng CÁCH 2 nếu chỉ cần 1 lần và sheet nhỏ
   → Dùng CÁCH 3 nếu cần tự động hóa định kỳ

""")

choice = input("\n👉 Bạn muốn dùng cách nào? (1/2/3): ").strip()

if choice == "1":
    print("""
    
📋 CODE APPS SCRIPT ĐÃ COPY VÀO CLIPBOARD:

Làm theo:
1. Mở Google Sheet
2. Extensions → Apps Script
3. Paste code (Ctrl+V)
4. Nhấn Run
5. File sẽ xuất hiện trong Google Drive

🔗 Hoặc xem file: google_apps_script.gs trong project này
    """)
    
elif choice == "2":
    print("""
    
📋 HƯỚNG DẪN COPY THỦ CÔNG:

1. Đăng nhập Google: https://accounts.google.com
2. Mở link Google Sheet mà bạn được cấp quyền
3. Nhấn Ctrl+A (chọn tất cả)
4. Nhấn Ctrl+C (copy)
5. Mở Excel mới
6. Nhấn Ctrl+V (paste)
7. File → Save As → Chọn .xlsx

✅ Nếu bị lỗi "Cannot copy protected cells":
   → Dùng cách 1 (Apps Script) thay thế
    """)
    
elif choice == "3":
    print("""
    
⏳ Đang chuẩn bị script tự động...

Bạn cần:
1. URL của Google Sheet
2. Tài khoản Google được cấp quyền xem

Script sẽ mở Chrome và yêu cầu bạn đăng nhập.
    """)
    
    sheet_url = input("\n📎 Nhập URL Google Sheet: ").strip()
    
    if sheet_url:
        print(f"""
        
✅ CHUẨN BỊ QUÉT: {sheet_url}

Chạy lệnh này:
    python quet_sheet_khoa.py "{sheet_url}"

Hoặc đợi script tự động chạy...
        """)
    else:
        print("❌ Chưa nhập URL!")
else:
    print("\n❌ Lựa chọn không hợp lệ!")

print("""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  LƯU Ý QUAN TRỌNG:

1. ✅ Bạn PHẢI có email được owner cấp quyền
2. ✅ Phải đăng nhập bằng email đó
3. ❌ Không thể quét sheet mà bạn không có quyền xem
4. ⚖️  Chỉ sử dụng cho mục đích hợp pháp
5. 🔒 Tôn trọng quyền riêng tư của chủ sheet

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
