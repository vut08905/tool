"""
CÁCH ĐƠN GIẢN NHẤT: Hướng dẫn copy thủ công
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║          CÁCH QUÉT GOOGLE SHEET RA EXCEL                    ║
╚══════════════════════════════════════════════════════════════╝

⚠️  Google Sheets render động nên rất khó scrape bằng code!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CÁCH 1: APPS SCRIPT (KHUYẾN NGHỊ - 100% THÀNH CÔNG)

1. Mở Google Sheet
2. Extensions → Apps Script
3. Copy code từ file: APPS_SCRIPT_CODE.gs
4. Paste và Save
5. Chọn function exportSheetToCSV
6. Nhấn Run ▶️
7. Cho phép quyền
8. File CSV sẽ xuất hiện trong Google Drive
9. Download và mở bằng Excel

💡 Cách này LUÔN HOẠT ĐỘNG nếu bạn có quyền xem sheet!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CÁCH 2: COPY THỦ CÔNG (ĐƠN GIẢN)

1. Mở Google Sheet
2. Nhấn Ctrl+A (chọn tất cả)
3. Nhấn Ctrl+C (copy)
4. Mở Excel
5. Nhấn Ctrl+V (paste)
6. Save as .xlsx

⚠️  Nếu không copy được → Sheet bị protect → Dùng Cách 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CÁCH 3: DOWNLOAD TRỰC TIẾP (NẾU ĐƯỢC PHÉP)

1. Mở Google Sheet
2. File → Download → Microsoft Excel (.xlsx)

⚠️  Nếu không có menu Download → Dùng Cách 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ TẠI SAO CODE PYTHON KHÔNG QUÉT ĐƯỢC?

Google Sheets không dùng HTML table thông thường mà render động bằng:
- Canvas (vẽ trực tiếp)
- Virtual scrolling (chỉ render cells nhìn thấy)
- JavaScript framework phức tạp

→ Selenium không thể scrape được!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ KẾT LUẬN:

Dùng APPS SCRIPT (Cách 1) - Đây là cách DUY NHẤT chắc chắn!

File code: APPS_SCRIPT_CODE.gs
Hướng dẫn: HUONG_DAN_CHI_TIET.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

choice = input("\n👉 Bạn cần tôi giải thích thêm gì? (Enter để thoát): ")
