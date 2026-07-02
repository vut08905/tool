import re

file_path = r"d:\webtruong4.1\final\complete_gui.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update _load_cloud_config
old_cfg = """                my_ver = APP_VERSION
                cloud_ver = data.get("version", my_ver)
                update_url = data.get("update_url", "")
                if cloud_ver != my_ver:
                    msg = data.get("thong_bao", f"Đã có phiên bản {cloud_ver}. Vui lòng tải bản mới để dùng tiếp!")
                    self.win.after(0, lambda m=msg, u=update_url: self._show_update_block(m, u))
                    return"""

new_cfg = """                my_ver = APP_VERSION
                cloud_ver = data.get("version", my_ver)
                update_url = data.get("update_url", "")
                excel_url = data.get("excel_url", "")
                if cloud_ver != my_ver:
                    msg = data.get("thong_bao", f"Đã có phiên bản {cloud_ver}. Vui lòng tải bản mới để dùng tiếp!")
                    self.win.after(0, lambda m=msg, u=update_url, e=excel_url: self._show_update_block(m, u, e))
                    return"""
content = content.replace(old_cfg, new_cfg, 1)


# 2. Update _show_update_block signature
old_sig = """    def _show_update_block(self, msg, update_url):"""
new_sig = """    def _show_update_block(self, msg, update_url, excel_url=""):"""
content = content.replace(old_sig, new_sig, 1)

# 3. Add excel download logic inside download_thread
old_bat = """                    # Tạo file bat để thay thế (Mở terminal riêng biệt minh bạch)"""
new_bat = """                    # Tải Excel nếu có URL update song song
                    if excel_url:
                        self.win.after(0, lambda: lbl_status.config(text="Đang tải file lịch học (lophoc.xlsx) mới..."))
                        try:
                            target_excel = os.path.join(os.path.dirname(current_exe), "lophoc.xlsx")
                            with requests.get(excel_url, headers={'User-Agent': 'ULSA/1.0'}, stream=True, timeout=15, verify=False) as rexcel:
                                rexcel.raise_for_status()
                                with open(target_excel, "wb") as fex:
                                    for chunk in rexcel.iter_content(chunk_size=8192):
                                        if chunk: fex.write(chunk)
                        except Exception as excel_err:
                            print(f"Lỗi tải Excel: {excel_err}")

                    # Tạo file bat để thay thế (Mở terminal riêng biệt minh bạch)"""
content = content.replace(old_bat, new_bat, 1)

# 4. Modify load_existing_config to explicitly enforce os.path.join(application_path, "lophoc.xlsx")
# Wait, let's just find the excel_path setup.
old_excel_load = """                # Load Excel file path
                excel_path = config_data.get('excel_file_path', 'lophoc.xlsx')
                self.excel_path_entry.delete(0, tk.END)
                self.excel_path_entry.insert(0, excel_path)"""

new_excel_load = """                # Tuyệt đối ép đường dẫn về lophoc.xlsx cạnh file exe
                excel_path = os.path.join(application_path, 'lophoc.xlsx')
                self.excel_path_entry.delete(0, tk.END)
                self.excel_path_entry.insert(0, excel_path)"""
content = content.replace(old_excel_load, new_excel_load, 1)

# Modify __init__ of CompleteGUI if needed where it creates but load_existing_config runs after creation.
old_btn = """        self.excel_path_entry.insert(0, "lophoc.xlsx")"""
new_btn = """        self.excel_path_entry.insert(0, os.path.join(application_path, "lophoc.xlsx"))"""
content = content.replace(old_btn, new_btn)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("PATCH APPLIED!")

