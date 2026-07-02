import os

file_path = r"d:\webtruong4.1\final\complete_gui.py"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Lấy đến đoạn return False của save_config
marker = """            self.log_message(f"❌ Lỗi lưu file: {os.path.abspath(self.config_file)}: {e}")
            return False"""

if marker in content:
    idx = content.find(marker) + len(marker)
    
    # Prefix: the content before the cut
    prefix = content[:idx] + "\n\n"
    
    # Suffix: We need to find the definition after the corrupted start_automation, e.g., stop_automation
    suffix_idx = content.find("    def stop_automation(self):")
    if suffix_idx == -1:
        print("Không tìm thấy stop_automation!")
        suffix_idx = len(content) # fallback
        
    suffix = "\n" + content[suffix_idx:]
    
    injected_code = """    def load_config(self):
        \"\"\"Load cấu hình từ file\"\"\"
        self.load_existing_config()
    
    def load_existing_config(self):
        \"\"\"Load cấu hình hiện có (login_info, course_selections) và tự động load vào Treeview\"\"\"
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = __import__('json').load(f)
                login_info = config_data.get('login_info', {})
                import tkinter as tk
                self.student_id_entry.delete(0, tk.END)
                self.student_id_entry.insert(0, login_info.get('student_id', ''))
                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, login_info.get('password', ''))
                
                excel_path = config_data.get('excel_file_path', os.path.join(self.application_path if hasattr(self, 'application_path') else '', 'lophoc.xlsx'))
                self.excel_path_entry.delete(0, tk.END)
                self.excel_path_entry.insert(0, excel_path)
                self.course_tree.delete(*self.course_tree.get_children())
                course_selections = config_data.get('course_selections', {})
                subject_names = course_selections.get('subject_names_b1', [])
                class_names = course_selections.get('class_names_b2', [])
                for i, (subject, class_name) in enumerate(zip(subject_names, class_names)):
                    self.course_tree.insert('', 'end', values=(i + 1, subject, class_name))
                self.log_message(f"📂 Đã load cấu hình: {len(subject_names)} lớp")
        except Exception as e:
            self.log_message(f"⚠️ Không thể load cấu hình: {e}")
    
    def update_title(self):
        \"\"\"Cập nhật tiêu đề cửa sổ với tên thư mục và mã sinh viên\"\"\"
        try:
            student_id = self.student_id_entry.get().strip()
            if student_id:
                self.root.title(f"🎯 {self.folder_name} : {student_id}")
            else:
                self.root.title(f"🎯 {self.folder_name}")
        except Exception as e:
            print(f"⚠️ Lỗi cập nhật tiêu đề: {e}")
    
    def update_time(self):
        \"\"\"Cập nhật thời gian real-time\"\"\"
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=f"⏰ Thời gian: {current_time}")
        self.root.after(1000, self.update_time)
    
    def log_message(self, message):
        \"\"\"Thêm message vào log nếu widget đã khởi tạo\"\"\"
        import tkinter as tk
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\\n"
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            self.root.update()
        else:
            print(log_entry)
            
    def start_automation(self):
        \"\"\"Bắt đầu automation và log real-time ra giao diện\"\"\"
        import threading
        import traceback
        import sys
        
        # Tự động lưu cấu hình ẩn trước khi bắt đầu
        if not self.save_config(silent=True):
            self.log_message("⚠️ Thiếu thông tin! Vui lòng điền mã SV, Mật khẩu và chọn danh sách lớp học ở Tab cấu hình!")
            return

        self.start_btn.config(state='disabled')
        self.log_message("⏳ Phân tích môi trường...")
        self.root.update()

        try:
            # Chạy kiểm tra môi trường trực tiếp trên Main Thread (Rất nhanh vì check offline)
            res = license_manager.check_license()
            self.log_message(f"⏳ [DEBUG] license_manager valid = {res.get('valid')}")

            chrome_version = None
            chrome_error = None
            chrome_needs_install = False
            try:
                import winreg as _winreg
                def _get_chrome_ver():
                    keys = [
                        r"SOFTWARE\\Google\\Chrome\\BLBeacon",
                        r"SOFTWARE\\WOW6432Node\\Google\\Chrome\\BLBeacon",
                    ]
                    for key_path in keys:
                        try:
                            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, key_path)
                            ver, _ = _winreg.QueryValueEx(key, "version")
                            _winreg.CloseKey(key)
                            return ver
                        except Exception:
                            pass
                    for chrome_path in [
                        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                    ]:
                        if os.path.exists(chrome_path):
                            return "đã cài"
                    return None
                
                chrome_version = _get_chrome_ver()
                if not chrome_version:
                    chrome_needs_install = True
            except Exception as e:
                chrome_error = str(e)

            def _proceed_to_automation():
                \"\"\"Thực sự khởi chạy automation sau khi Chrome đã sẵn sàng.\"\"\"
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

            def _download_chrome_and_proceed():
                \"\"\"Tải Chrome trong background và tiếp tục sau khi xong.\"\"\"
                import urllib.request, tempfile
                url = "https://dl.google.com/chrome/install/ChromeSetup.exe"
                try:
                    self.root.after(0, lambda: self.log_message("📥 Đang tải Google Chrome..."))
                    tmp_dir = tempfile.gettempdir()
                    save_path = os.path.join(tmp_dir, "ChromeSetup.exe")

                    def _progress(count, block_size, total_size):
                        if total_size > 0:
                            pct = int(count * block_size * 100 / total_size)
                            pct = min(pct, 100)
                            if pct % 10 == 0:
                                self.root.after(0, lambda p=pct: self.log_message(f"  ↓ Đang tải Chrome: {p}%"))

                    urllib.request.urlretrieve(url, save_path, _progress)
                    self.root.after(0, lambda: self.log_message("✅ Tải xong! Đang mở trình cài đặt Chrome..."))
                    self.root.after(0, lambda: self.log_message("⚠️ Hãy cài Chrome xong rồi bấm Bắt đầu lại!"))
                    os.startfile(save_path)
                    self.root.after(0, lambda: self.start_btn.config(state='normal'))
                except Exception as e:
                    self.root.after(0, lambda: self.log_message(f"❌ Tải Chrome thất bại: {e}"))
                    self.root.after(0, lambda: self.log_message("💡 Tải thủ công: https://www.google.com/intl/vi/chrome/"))
                    self.root.after(0, lambda: self.start_btn.config(state='normal'))

            self.log_message("⏳ [DEBUG] Bắt đầu gọi _post_check")

            # Gọi _post_check trực tiếp (không qua after)
            if not res.get("valid", False):
                self.log_message("❌ [DEBUG] Bản quyền đã hết hạn, mở messagebox...")
                self.root.update()
                from tkinter import messagebox
                messagebox.showerror(
                    "❌ Bản quyền đã hết hạn",
                    f"Bản quyền của bạn đã hết hạn!\\nChi tiết: {res.get('reason', '')}\\n\\n"
                    "Hệ thống sẽ Đăng xuất để bạn vào màn hình Kích hoạt gia hạn.", parent=self.root
                )
                import os
                if os.path.exists(license_manager.LICENSE_FILE):
                    try: os.remove(license_manager.LICENSE_FILE)
                    except: pass
                
                self.root.withdraw()
                def on_reactivated(masv: str):
                    res2 = license_manager.check_license()
                    exp   = res2.get("expire_date", "N/A")
                    days  = res2.get("days_left", 0)

                    # Đóng hết widget cũ và tạo lại GUI mới trên cùng root
                    self.root.deiconify()
                    for widget in self.root.winfo_children():
                        widget.destroy()
                    new_app = CompleteGUI(self.root, licensed_masv=masv, expire_date=exp, days_left=days)
                    new_app.log_message(f"✅ Đăng nhập lại thành công | Mã SV: {masv} | Hết hạn: {exp}")
                
                LicenseWindow(self.root, on_reactivated)
                self.start_btn.config(state='normal')
                return

            self.log_message("⏳ [DEBUG] Kiểm tra self.config_file")
            if not os.path.exists(self.config_file):
                self.log_message("❌ [DEBUG] Không thấy config file, mở messagebox...")
                self.root.update()
                from tkinter import messagebox
                messagebox.showwarning("Chưa có cấu hình", "Vui lòng lưu cấu hình trước khi chạy!", parent=self.root)
                self.start_btn.config(state='normal')
                return

            self.log_message("⏳ [DEBUG] Xử lý tình trạng Chrome...")

            # ── Xử lý tình trạng Chrome ──
            if chrome_error:
                self.log_message(f"⚠️ Lỗi kiểm tra Chrome: {chrome_error}")
                _proceed_to_automation()
            elif chrome_needs_install:
                self.log_message("⚠️ Chưa phát hiện Google Chrome trên máy! Tự động bắt đầu tải...")
                threading.Thread(target=_download_chrome_and_proceed, daemon=True).start()
            else:
                self.log_message(f"✅ Google Chrome đã cài: phiên bản {chrome_version}")
                _proceed_to_automation()
                
        except Exception as full_e:
            self.log_message(f"❌ [LỖI NGHIÊM TRỌNG]: {full_e}")
            self.log_message(traceback.format_exc())
            self.start_btn.config(state='normal')
"""

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(prefix + injected_code + suffix)
    print("DONE FIXING!")
else:
    print("MARKER NOT FOUND")

