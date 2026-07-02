# 🧪 HƯỚNG DẪN TEST PHẦN MỀM TRONG SANDBOX

## ✅ Phương án 1: VirtualBox (Windows Home - KHUYÊN DÙNG)

### **Bước 1: Cài VirtualBox**
1. Download: https://www.virtualbox.org/wiki/Downloads
2. Cài đặt VirtualBox
3. Download Windows 10/11 ISO: https://www.microsoft.com/software-download/windows11

### **Bước 2: Tạo Virtual Machine**
1. Mở VirtualBox → New
2. Setup:
   - Name: `Test_Sandbox`
   - Type: `Microsoft Windows`
   - Version: `Windows 10/11 (64-bit)`
   - RAM: `4096 MB` (nếu laptop có 8GB+)
   - Disk: `50 GB` (dynamic)
3. Start VM → Mount Windows ISO → Cài Windows
4. **KHÔNG CẦN KEY**, chọn "I don't have a product key"

### **Bước 3: Tạo Snapshot "Clean"**
- Sau khi cài Windows xong
- VirtualBox menu: `Machine` → `Take Snapshot...`
- Name: `Fresh Windows Install`
- Để restore lại môi trường sạch mỗi lần test

### **Bước 4: Test phần mềm**
```
1. Copy ULSA_EXE_DEPLOY folder vào VM
   - Dùng Shared Folder hoặc
   - Drag & Drop (bật trong Settings → General → Advanced)

2. Chạy ULSA_DangKyTinChi.exe

3. Kiểm tra:
   ✅ Phần mềm tự cài Chrome chưa?
   ✅ Phần mềm tự tải ChromeDriver chưa?
   ✅ Có lỗi gì không?

4. Sau test xong:
   - VirtualBox: Machine → Restore Snapshot...
   - Chọn "Fresh Windows Install"
   - Môi trường quay về trạng thái sạch ngay lập tức!
```

---

## 🥉 Phương án 2: Sandboxie-Plus (Nhẹ hơn VM)

### **Ưu điểm:**
- Nhẹ hơn VirtualBox (không cần cài cả Windows)
- Chạy app trong sandbox isolated
- Miễn phí, open-source

### **Nhược điểm:**
- KHÔNG cô lập 100% (vẫn dùng chung Windows host)
- Có thể không catch hết lỗi thiếu dependencies

### **Setup:**
```
1. Download: https://sandboxie-plus.com/downloads/
2. Cài Sandboxie-Plus
3. Right-click ULSA_DangKyTinChi.exe
   → "Run Sandboxed"
4. Test xem chạy được không
```

---

## 🎯 SO SÁNH

| Tính năng | VirtualBox | Sandboxie-Plus | Windows Sandbox |
|-----------|------------|----------------|-----------------|
| **Miễn phí** | ✅ | ✅ | ✅ |
| **Windows Home** | ✅ | ✅ | ❌ (Cần Pro) |
| **Cô lập 100%** | ✅ | ⚠️ Một phần | ✅ |
| **Tốc độ** | Chậm hơn | Nhanh | Nhanh nhất |
| **Dễ setup** | Trung bình | Dễ | Rất dễ |
| **RAM cần** | 4GB+ | <1GB | 2GB+ |
| **Snapshot/Reset** | ✅ | ✅ (Delete sandbox) | ✅ (Auto) |

---

## 💡 KHUYẾN NGHỊ

**Cho máy Windows Home → Dùng VirtualBox**
- Môi trường test chính xác nhất
- Giả lập máy khách thật sự (không có Python, Chrome, etc.)
- Có thể test nhiều lần với snapshot

**Nếu cần test nhanh → Sandboxie-Plus**
- Setup 5 phút
- Nhưng không chắc chắn 100%

---

## 🚀 QUICK START với VirtualBox

```powershell
# Copy folder test vào VM:
# 1. VirtualBox: Settings → Shared Folders → Add
#    Folder Path: D:\webtruong4.1\ULSA_EXE_DEPLOY
#    Folder Name: ULSA_Test
#    Auto-mount: ✅

# 2. Trong VM Windows:
#    Shared folder sẽ xuất hiện tại \\VBOXSVR\ULSA_Test
#    Copy ra Desktop và chạy thử

# 3. Sau test xong:
#    Machine → Restore Snapshot → Fresh Windows Install
#    → Môi trường sạch lại ngay lập tức!
```

---

## ⚠️ LƯU Ý

1. **VirtualBox cần Virtualization (VT-x/AMD-V) bật trong BIOS**
   - Kiểm tra: Task Manager → Performance → CPU
   - Phải thấy "Virtualization: Enabled"
   - Nếu Disabled: Vào BIOS bật Intel VT-x hoặc AMD-V

2. **RAM:** 
   - Laptop có 8GB → Cho VM 4GB
   - Laptop có 16GB+ → Cho VM 6-8GB

3. **Storage:**
   - Dynamic disk không chiếm 50GB ngay
   - Chỉ tăng dần khi VM sử dụng
   - Thực tế ~15-20GB cho Windows + test

4. **Network:**
   - Mặc định VM có internet qua NAT
   - Phần mềm sẽ tự tải Chrome/ChromeDriver được

---

## 🎬 VIDEO HƯỚNG DẪN (Nếu cần)

- VirtualBox setup: https://www.youtube.com/results?search_query=virtualbox+windows+11+setup
- Sandboxie: https://www.youtube.com/results?search_query=sandboxie+plus+tutorial

