# -*- coding: utf-8 -*-
"""
Xử lý lỗi trùng lịch ở bước B2
Khi web ULSA báo lỗi, tự động tìm lớp thay thế và cho user chọn
"""

import re
import tkinter as tk
from tkinter import ttk
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ScheduleConflictHandler:
    """Xử lý lỗi trùng thời khóa biểu"""
    
    def __init__(self, driver, excel_file="lophoc.xlsx"):
        self.driver = driver
        self.excel_file = excel_file
        self.df = pd.read_excel(excel_file)
        self.selected_class = None
        self.timeout = False
        
    def check_conflict_error(self):
        """
        Kiểm tra có thông báo lỗi trùng lịch không
        
        Returns:
            tuple: (has_error: bool, error_message: str, conflicted_classes: list)
        """
        try:
            # Kiểm tra alert popup
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            
            if "Trùng thời khoá biểu" in alert_text:
                print(f"🚨 Alert: {alert_text}")
                alert.accept()  # Bấm OK
                
                # Parse lớp bị trùng từ alert
                classes = self.parse_conflicted_classes(alert_text)
                return (True, alert_text, classes)
                
        except:
            pass
        
        # Kiểm tra thông báo trên trang
        try:
            error_element = self.driver.find_element(By.ID, "lblThong_bao")
            error_text = error_element.text.strip()
            
            if error_text and "Trùng thời khoá biểu" in error_text:
                print(f"⚠️ Thông báo trên trang: {error_text}")
                classes = self.parse_conflicted_classes(error_text)
                return (True, error_text, classes)
                
        except:
            pass
        
        return (False, "", [])
    
    def parse_conflicted_classes(self, error_text):
        """
        Parse tên 2 lớp bị trùng từ thông báo lỗi
        
        Args:
            error_text: "Trùng thời khoá biểu giữa các lớp sau : GQTC1022H_D19LK.2_LT và LTMQ1022H_D19LK.1_LT Thứ 6 (T7-9);"
        
        Returns:
            list: [class1, class2]
        """
        # Pattern: Tìm 2 tên lớp
        pattern = r':\s*([A-Z0-9_\.]+(?:_LT|_TH|_BT)?)\s*và\s*([A-Z0-9_\.]+(?:_LT|_TH|_BT)?)'
        match = re.search(pattern, error_text)
        
        if match:
            class1 = match.group(1).strip()
            class2 = match.group(2).strip()
            return [class1, class2]
        
        return []
    
    def get_currently_selected_classes(self):
        """
        Lấy danh sách các lớp đang được chọn trên trang B2
        
        Returns:
            list: Danh sách tên lớp đã chọn
        """
        selected = []
        try:
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']:checked")
            
            for cb in checkboxes:
                # Tìm tên lớp trong hàng chứa checkbox
                row = cb.find_element(By.XPATH, "./ancestor::tr")
                cells = row.find_elements(By.TAG_NAME, "td")
                
                for cell in cells:
                    # Tìm cell chứa tên lớp (có dạng XXX_XXX_LT)
                    text = cell.text.strip()
                    if '_LT' in text or '_TH' in text or '_BT' in text:
                        if re.match(r'^[A-Z0-9_\.]+$', text):
                            selected.append(text)
                            break
        except Exception as e:
            print(f"❌ Lỗi lấy danh sách lớp: {e}")
        
        return selected
    
    def find_replacement_classes(self, subject_code, current_selected, exclude_class):
        """
        Tìm các lớp thay thế cùng môn nhưng không trùng lịch
        
        Args:
            subject_code: Mã môn (vd: GQTC1022H)
            current_selected: Danh sách lớp đang chọn
            exclude_class: Lớp cần loại trừ (lớp bị lỗi)
        
        Returns:
            list: [{class_name, schedule, slots, conflict}]
        """
        # Lấy tất cả lớp cùng môn
        same_subject = self.df[self.df['Mã_học_phần'] == subject_code].copy()
        
        if same_subject.empty:
            return []
        
        # Lấy lịch học của các lớp hiện tại (trừ lớp bị loại)
        current_schedules = []
        for cls in current_selected:
            if cls != exclude_class:
                row = self.df[self.df['Tên_lớp_tín_chỉ'] == cls]
                if not row.empty:
                    schedule = row.iloc[0]['Lịch_học']
                    if pd.notna(schedule):
                        current_schedules.append(str(schedule))
        
        # Kiểm tra từng lớp
        replacements = []
        for idx, row in same_subject.iterrows():
            class_name = row['Tên_lớp_tín_chỉ']
            
            # Bỏ qua lớp đang bị loại
            if class_name == exclude_class:
                continue
            
            # Bỏ qua lớp đã chọn
            if class_name in current_selected:
                continue
            
            schedule = str(row['Lịch_học']) if pd.notna(row['Lịch_học']) else "Chưa có lịch"
            slots = row.get('Còn_trống', '?')
            
            # Check trùng lịch
            has_conflict = False
            if pd.notna(row['Lịch_học']):
                for existing_schedule in current_schedules:
                    if self.check_time_overlap(str(row['Lịch_học']), existing_schedule):
                        has_conflict = True
                        break
            
            replacements.append({
                'class_name': class_name,
                'schedule': schedule,
                'slots': slots,
                'conflict': has_conflict
            })
        
        # Sort: Không trùng lịch trước, sau đó sort theo số slot
        replacements.sort(key=lambda x: (x['conflict'], -int(x['slots']) if isinstance(x['slots'], (int, str)) and str(x['slots']).isdigit() else 0))
        
        return replacements
    
    def check_time_overlap(self, schedule1, schedule2):
        """Kiểm tra 2 lịch có trùng không"""
        try:
            parsed1 = self.parse_schedule(schedule1)
            parsed2 = self.parse_schedule(schedule2)
            
            if not parsed1 or not parsed2:
                return False
            
            # Cùng ngày
            if parsed1['day'] != parsed2['day']:
                return False
            
            # Trùng tiết
            return (parsed1['start'] <= parsed2['end']) and (parsed1['end'] >= parsed2['start'])
            
        except:
            return False
    
    def parse_schedule(self, schedule):
        """Parse lịch học từ chuỗi"""
        try:
            parts = schedule.split('\n')
            if len(parts) < 2:
                return None
            
            day_part = parts[1]
            
            day_of_week = None
            if 'Thứ 2' in day_part:
                day_of_week = 2
            elif 'Thứ 3' in day_part:
                day_of_week = 3
            elif 'Thứ 4' in day_part:
                day_of_week = 4
            elif 'Thứ 5' in day_part:
                day_of_week = 5
            elif 'Thứ 6' in day_part:
                day_of_week = 6
            elif 'Thứ 7' in day_part or 'CN' in day_part:
                day_of_week = 7
            
            time_match = re.search(r'T(\d+)-(\d+)', day_part)
            if time_match:
                start_period = int(time_match.group(1))
                end_period = int(time_match.group(2))
                return {'day': day_of_week, 'start': start_period, 'end': end_period}
            
            return None
        except:
            return None
    
    def show_replacement_dialog(self, conflicted_class, replacements):
        """
        Hiển thị dialog cho user chọn lớp thay thế
        Tự động chọn sau 60s nếu user không làm gì
        
        Args:
            conflicted_class: Lớp bị trùng cần thay thế
            replacements: Danh sách lớp thay thế
        
        Returns:
            str: Tên lớp được chọn (hoặc None nếu hủy)
        """
        dialog = tk.Toplevel()
        dialog.title("⚠️ Trùng lịch - Chọn lớp thay thế")
        dialog.geometry("900x600")
        dialog.attributes('-topmost', True)
        
        self.selected_class = None
        self.timeout = False
        countdown = {'value': 60}
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_text = f"⚠️ LỚP BỊ TRÙNG LỊCH: {conflicted_class}\n\n"
        title_text += f"💡 Vui lòng chọn lớp thay thế hoặc đợi 60s để tự động chọn lớp tối ưu nhất"
        
        title_label = ttk.Label(main_frame, text=title_text, font=('Arial', 11, 'bold'), justify=tk.LEFT)
        title_label.pack(pady=(0, 10))
        
        # Countdown
        countdown_label = ttk.Label(main_frame, 
                                   text=f"⏱️ Tự động chọn sau: {countdown['value']}s", 
                                   font=('Arial', 12, 'bold'), foreground='red')
        countdown_label.pack(pady=5)
        
        # Scrollable list
        list_frame = ttk.LabelFrame(main_frame, text=" 📋 CÁC LỚP THAY THẾ ", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        canvas = tk.Canvas(list_frame, height=350)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Radio buttons
        var = tk.StringVar(value="")
        
        for replacement in replacements:
            option_frame = ttk.Frame(scrollable_frame)
            option_frame.pack(fill=tk.X, pady=5, padx=5)
            
            conflict_icon = "🔴 TRÙNG LỊCH " if replacement['conflict'] else "✅ PHÙ HỢP "
            text = f"{conflict_icon}{replacement['class_name']}\n"
            text += f"    📅 Lịch: {replacement['schedule']}\n"
            text += f"    💺 Còn trống: {replacement['slots']}"
            
            radio = ttk.Radiobutton(option_frame, text=text, variable=var, value=replacement['class_name'])
            radio.pack(anchor=tk.W)
            
            # Tự động chọn lớp phù hợp đầu tiên
            if not replacement['conflict'] and var.get() == "":
                var.set(replacement['class_name'])
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.BOTTOM, pady=10)
        
        def on_ok():
            selected = var.get()
            if selected:
                self.selected_class = selected
                dialog.destroy()
            else:
                tk.messagebox.showwarning("Chưa chọn", "Vui lòng chọn một lớp!")
        
        def on_cancel():
            self.selected_class = None
            dialog.destroy()
        
        def update_countdown():
            if countdown['value'] > 0 and tk.Toplevel.winfo_exists(dialog):
                countdown['value'] -= 1
                countdown_label.config(text=f"⏱️ Tự động chọn sau: {countdown['value']}s")
                dialog.after(1000, update_countdown)
            elif countdown['value'] == 0:
                self.timeout = True
                selected = var.get()
                if selected:
                    self.selected_class = selected
                    print(f"⏰ HẾT 60s → Tự động chọn: {selected}")
                dialog.destroy()
        
        ok_btn = ttk.Button(btn_frame, text="✅ OK", command=on_ok, width=15)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="❌ Hủy", command=on_cancel, width=15)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        update_countdown()
        dialog.wait_window()
        
        return self.selected_class
    
    def uncheck_class(self, class_name):
        """Bỏ chọn checkbox của lớp"""
        try:
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            
            for cb in checkboxes:
                row = cb.find_element(By.XPATH, "./ancestor::tr")
                if class_name in row.text:
                    if cb.is_selected():
                        cb.click()
                        print(f"✅ Đã bỏ chọn: {class_name}")
                        return True
            
            print(f"⚠️ Không tìm thấy: {class_name}")
            return False
            
        except Exception as e:
            print(f"❌ Lỗi bỏ chọn: {e}")
            return False
    
    def check_class(self, class_name):
        """Chọn checkbox của lớp"""
        try:
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            
            for cb in checkboxes:
                row = cb.find_element(By.XPATH, "./ancestor::tr")
                if class_name in row.text:
                    if not cb.is_selected():
                        cb.click()
                        print(f"✅ Đã chọn: {class_name}")
                        return True
            
            print(f"⚠️ Không tìm thấy: {class_name}")
            return False
            
        except Exception as e:
            print(f"❌ Lỗi chọn lớp: {e}")
            return False
    
    def handle_conflict(self, max_retries=None):
        """
        Xử lý lỗi trùng lịch - Main function
        
        Args:
            max_retries: Số lần thử lại (None = vô hạn)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        retry_count = 0
        
        while max_retries is None or retry_count < max_retries:
            # 1. Check có lỗi không
            has_error, error_msg, conflicted_classes = self.check_conflict_error()
            
            if not has_error:
                print("✅ Không có lỗi trùng lịch")
                return (True, "Không có lỗi")
            
            if len(conflicted_classes) != 2:
                print(f"❌ Không thể parse lỗi: {error_msg}")
                return (False, f"Lỗi không xác định: {error_msg}")
            
            class1, class2 = conflicted_classes
            print(f"🔍 Lớp trùng: {class1} và {class2}")
            
            # 2. Lấy danh sách lớp đang chọn
            current_selected = self.get_currently_selected_classes()
            print(f"📋 Đang chọn: {current_selected}")
            
            # 3. Quyết định bỏ lớp nào (ưu tiên bỏ lớp được thêm sau)
            if class1 in current_selected and class2 in current_selected:
                idx1 = current_selected.index(class1)
                idx2 = current_selected.index(class2)
                class_to_remove = class2 if idx2 > idx1 else class1
            elif class1 in current_selected:
                class_to_remove = class1
            elif class2 in current_selected:
                class_to_remove = class2
            else:
                print("⚠️ Không tìm thấy lớp nào trong danh sách đã chọn")
                return (False, "Không tìm thấy lớp bị trùng")
            
            print(f"🗑️ Sẽ thay thế lớp: {class_to_remove}")
            
            # 4. Tìm lớp thay thế
            subject_code = class_to_remove.split('_')[0]
            replacements = self.find_replacement_classes(subject_code, current_selected, class_to_remove)
            
            if not replacements:
                print(f"❌ Không có lớp thay thế cho {class_to_remove}")
                return (False, f"Không có lớp thay thế cho {class_to_remove}")
            
            print(f"💡 Tìm thấy {len(replacements)} lớp thay thế")
            
            # 5. Hiển thị dialog cho user chọn
            selected_replacement = self.show_replacement_dialog(class_to_remove, replacements)
            
            if not selected_replacement:
                print("⏭️ User hủy")
                return (False, "User hủy")
            
            print(f"✅ Đã chọn: {selected_replacement}")
            
            # 6. Bỏ chọn lớp cũ, chọn lớp mới
            self.uncheck_class(class_to_remove)
            self.check_class(selected_replacement)
            
            # 7. Submit lại
            print("🔄 Submit lại...")
            try:
                submit_button = self.driver.find_element(By.ID, "btnLuu_ket_qua_DK")
                submit_button.click()
                
                # Đợi load
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "lblThong_bao"))
                )
                
            except Exception as e:
                print(f"❌ Lỗi submit: {e}")
            
            retry_count += 1
            if max_retries:
                print(f"🔄 Retry {retry_count}/{max_retries}")
            else:
                print(f"🔄 Retry lần thứ {retry_count} (vô hạn)")
        
        # Chỉ đến đây nếu có max_retries (không phải None)
        return (False, f"Đã thử {max_retries} lần nhưng vẫn bị lỗi")
