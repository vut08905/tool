import re
import os

file_path = r"d:\webtruong4.1\final\complete_gui.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# We need to find `    def start_automation(self):` and replace it entirely.
# It ends right before `    def run_automation_direct(self):`

start_idx = content.find("    def start_automation(self):")
end_idx = content.find("    def run_automation_direct(self):")

if start_idx != -1 and end_idx != -1:
    old_method = content[start_idx:end_idx]
    
    new_method = """    def start_automation(self):
        \"\"\"Bắt đầu automation và phân luồng kiểm tra môi trường chạy tránh freeze\"\"\"
        import threading
        
        # 1. Kiểm tra cấu hình trước khi chạy
        if not os.path.exists(self.config_file):
            from tkinter import messagebox
            messagebox.showwarning("Chưa có cấu hình", "Vui lòng lưu cấu hình trước khi chạy!", parent=self.root)
            return
            
        # Khóa nút bấm và báo hiệu
        self.start_btn.config(state='disabled')
        self.log_message("⏳ Phân tích môi trường...")
        self.root.update()

        def _run_env_checks_thread():
            try:
                # ── Kiểm tra bản quyền Online ──
                import license_manager
                res = license_manager.check_license()
                if not res.get("valid", False):
                    self.root.after(0, lambda: _handle_invalid_license(res))
                    return
                
                # ── Kiểm tra mức độ sẵn sàng của Google Chrome ──
                chrome_version = None
                chrome_needs_install = False
                chrome_error = None
                try:
                    import winreg as _winreg
                    def _get_chrome_ver():
                        for key_path in [r"SOFTWARE\\Google\\Chrome\\BLBeacon", r"SOFTWARE\\WOW6432Node\\Google\\Chrome\\BLBeacon"]:
                            try:
                                key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, key_path)
                                ver, _ = _winreg.QueryValueEx(key, "version")
                                _winreg.CloseKey(key)
                                return ver
                            except Exception:
                                pass
                        for c_path in [r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"]:
                            if os.path.exists(c_path):
                                return "đã cài"
                        return None
                    chrome_version = _get_chrome_ver()
                    if not chrome_version:
                        chrome_needs_install = True
                except Exception as e:
                    chrome_error = str(e)

                # ── Ra quyết định tiếp diễn ──
                if chrome_error:
                    self.root.after(0, lambda: self.log_message(f"⚠️ Lỗi kiểm tra Chrome: {chrome_error}"))
                    self.root.after(0, _proceed)
                elif chrome_needs_install:
                    self.root.after(0, lambda: self.log_message("⚠️ Chưa phát hiện Google Chrome! Đang tự động tải & Cài đặt..."))
                    _download_and_install_chrome_blocking()
                else:
                    self.root.after(0, lambda: self.log_message(f"✅ Google Chrome đã sẵn sàng (version: {chrome_version})"))
                    self.root.after(0, _proceed)
                    
            except Exception as e:
                self.root.after(0, lambda e=e: self.log_message(f"❌ Lỗi phân tích môi trường: {str(e)}"))
                self.root.after(0, lambda: self.start_btn.config(state='normal'))

        def _download_and_install_chrome_blocking():
            import urllib.request, tempfile, subprocess
            try:
                self.root.after(0, lambda: self.log_message("📥 Bắt đầu tải Google Chrome từ máy chủ... (vui lòng chờ)"))
                url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
                tmp_dir = tempfile.gettempdir()
                save_path = os.path.join(tmp_dir, "chrome_installer.exe")
                
                def _progress(count, block_size, total_size):
                    if total_size > 0:
                        pct = min(int(count * block_size * 100 / total_size), 100)
                        if pct % 25 == 0:
                            self.root.after(0, lambda p=pct: self.log_message(f"  ↓ Đang tải Chrome: {p}%"))
                            
                urllib.request.urlretrieve(url, save_path, _progress)
                self.root.after(0, lambda: self.log_message("⚙️ Đã tải xong! Đang tự động cài ẩn Google Chrome (khoảng 30-60s)..."))
                subprocess.run([save_path, "/silent", "/install"], check=False)
                self.root.after(0, lambda: self.log_message("✅ Cài đặt Google Chrome hoàn tất!"))
                self.root.after(0, _proceed)
            except Exception as e:
                self.root.after(0, lambda e=e: self.log_message(f"❌ Lỗi khi tự cài Chrome: {e}"))
                self.root.after(0, lambda: self.log_message("⚠️ Tiến trình vẫn sẽ tiếp tục mở automation..."))
                self.root.after(0, _proceed)

        def _handle_invalid_license(res):
            from tkinter import messagebox
            messagebox.showerror(
                "❌ Bản quyền đã hết hạn",
                f"Bản quyền của bạn đã hết hạn!\\nChi tiết: {res.get('reason', '')}\\n\\n"
                "Hệ thống sẽ Đăng xuất để bạn vào màn hình Kích hoạt gia hạn.", parent=self.root
            )
            import os
            try:
                import license_manager
                if os.path.exists(license_manager.LICENSE_FILE):
                    os.remove(license_manager.LICENSE_FILE)
            except:
                pass
            
            self.root.withdraw()
            from final.complete_gui import LicenseWindow, CompleteGUI
            import license_manager
            
            def on_reactivated(masv: str):
                res2 = license_manager.check_license()
                exp = res2.get("expire_date", "N/A")
                days = res2.get("days_left", 0)
                self.root.deiconify()
                # Remove all old widgets to prevent duplicates
                for widget in self.root.winfo_children():
                    widget.destroy()
                CompleteGUI(self.root, licensed_masv=masv, expire_date=exp, days_left=days)

            LicenseWindow(self.root, on_reactivated)
            self.start_btn.config(state='normal')
            
        def _proceed():
            import sys
            self.log_message("🚀 ĐANG KHỞI ĐỘNG AUTOMATION...")
            self.status_label.config(text="📢 Trạng thái: ▶️ ĐANG CHẠY", foreground="green")
            self.step_label.config(text="🔄 Bước hiện tại: Khởi động")
            self.progress['value'] = 10
            self.progress_label.config(text="10%")
            self.pause_btn.config(state='normal')
            self.resume_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            if getattr(sys, 'frozen', False):
                self.log_message("🎯 Chạy từ file .exe")
                self.run_automation_direct()
            else:
                self.log_message("🐍 Chạy từ Python source")
                self.run_automation_subprocess()

        # ── Kickoff the background thread ──
        threading.Thread(target=_run_env_checks_thread, daemon=True).start()

"""
    
    content = content[:start_idx] + new_method + content[end_idx:]
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("REWRITE SUCCESSFUL")
else:
    print("COULD NOT FIND TARGET INDICES")

