# 🎯 HƯỚNG DẪN QUÉT GOOGLE SHEET BỊ KHÓA

## ✅ CÁCH DUY NHẤT HIỆU QUẢ: GOOGLE APPS SCRIPT

### Bước 1: Mở Google Sheet
- Đăng nhập bằng email được cấp quyền
- Mở link Google Sheet cần quét

### Bước 2: Mở Apps Script Editor
- Trong Google Sheet, vào menu: **Extensions** → **Apps Script**
- Sẽ mở tab mới với code editor

### Bước 3: Paste Code
- Xóa hết code mẫu có sẵn
- Copy toàn bộ code trong file `APPS_SCRIPT_CODE.gs`
- Paste vào Apps Script Editor

### Bước 4: Lưu Project
- Nhấn biểu tượng 💾 (Save) hoặc Ctrl+S
- Đặt tên project (vd: "Export Sheet Data")

### Bước 5: Chạy Function
**CÁCH 1: Chạy trực tiếp**
- Chọn function `exportSheetToCSV` trong dropdown
- Nhấn nút Run ▶️
- Lần đầu sẽ hỏi cấp quyền → Nhấn "Review permissions"
- Chọn tài khoản Google của bạn
- Nhấn "Advanced" → "Go to ... (unsafe)" → "Allow"
- File CSV sẽ xuất hiện trong Google Drive

**CÁCH 2: Dùng Menu (Tiện hơn)**
- Chọn function `onOpen` và chạy (chỉ 1 lần đầu)
- Quay lại Google Sheet
- Refresh trang (F5)
- Sẽ thấy menu mới: **📥 Export Data**
- Click menu → Chọn "Export to CSV" hoặc "Export to JSON"

### Bước 6: Download File
- Vào Google Drive: https://drive.google.com
- Tìm file vừa export (tên có dạng: Sheet1_export_xxxxx.csv)
- Click phải → Download
- Mở bằng Excel

---

## 📋 MẸO:

### Nếu Sheet có nhiều tabs:
- Script sẽ export sheet đang active
- Muốn export sheet khác: Click vào sheet đó trước khi chạy script

### Nếu muốn gửi email:
Thêm vào cuối function `exportSheetToCSV`:

```javascript
MailApp.sendEmail(
  'email_cua_ban@gmail.com',
  'Google Sheet Export',
  'File đã export xong!',
  {
    attachments: [file.getAs(MimeType.CSV)]
  }
);
```

### Nếu muốn tự động chạy:
- Apps Script Editor → Click biểu tượng đồng hồ ⏰ (Triggers)
- Nhấn "Add Trigger"
- Chọn function: `exportSheetToCSV`
- Chọn thời gian (vd: mỗi ngày lúc 9h sáng)

---

## ⚠️ LƯU Ý:

1. ✅ Email của bạn PHẢI được owner cấp quyền "Viewer" trở lên
2. ✅ Apps Script chạy với quyền của tài khoản bạn
3. ✅ File export sẽ được lưu vào Google Drive của bạn
4. ✅ Bypass hoàn toàn mọi hạn chế copy/download của sheet
5. ⏱️ Giới hạn chạy: 6 phút/lần (đủ cho hầu hết sheet)

---

## 🔧 TROUBLESHOOTING:

### "Script function not found: exportSheetToCSV"
→ Bạn chưa save code. Nhấn Ctrl+S để save

### "Exception: You do not have permission to call DriveApp.createFile"
→ Chưa cấp quyền. Chạy lại và cho phép quyền truy cập

### "ReferenceError: SpreadsheetApp is not defined"
→ Code không chạy trong Apps Script. Phải mở từ Extensions → Apps Script

### File CSV mở lỗi font trong Excel:
→ Mở Excel → Data → From Text/CSV → Chọn encoding UTF-8

---

## 💡 TẠI SAO CÁCH NÀY HIỆU QUẢ:

- ✅ Apps Script chạy **BÊN TRONG** Google Sheets
- ✅ Có quyền truy cập trực tiếp vào data
- ✅ Không bị block bởi cơ chế bảo vệ
- ✅ Không cần cài đặt gì
- ✅ Hoạt động 100% nếu bạn có quyền xem sheet

---

## 📞 NẾU VẪN KHÔNG ĐƯỢC:

Có thể owner đã tắt Apps Script cho sheet này. Trong trường hợp đó:

**CÁCH CUỐI CÙNG: Screenshot + OCR**
1. Mở sheet
2. Zoom out để thấy nhiều data
3. Chụp màn hình (hoặc Print to PDF)
4. Dùng OCR để convert ảnh thành text
5. Paste vào Excel

Nhưng cách này rất tốn công và dễ sai sót.

---

🎉 **CHÚC THÀNH CÔNG!**
