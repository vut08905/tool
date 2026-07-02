# -*- coding: utf-8 -*-
"""
GUI tổng hợp - Tất cả chức năng trong 1 màn hình
Bao gồm: Nhập tài khoản, Chọn lớp, Theo dõi tiến trình, Pause/Resume
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
import sys
import subprocess
import threading
import time
from datetime import datetime
import pandas as pd
from fuzzywuzzy import fuzz, process
import re

class CompleteGUI:
    def __init__(self, root):
        self.root = root
        
        # Dùng đường dẫn tương đối dựa trên vị trí file GUI này
        # Mỗi thư mục copy sẽ có file config riêng
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(script_dir, "automation", "auto_config.json")
        print(f"📁 Config file: {self.config_file}")
        
        # Lấy tên thư mục hiện tại
        self.folder_name = os.path.basename(script_dir)
        
        # Set tiêu đề mặc định (sẽ update sau khi load config)
        self.root.title(f"🎯 {self.folder_name}")
        self.root.geometry("1000x800")
        
        self.process = None
        
        self.setup_ui()
        # Đảm bảo tất cả widget đã khởi tạo xong mới load config
        self.load_existing_config()
        # Cập nhật tiêu đề sau khi load config
        self.update_title()
    
    def setup_ui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Tab 1: Cấu hình tài khoản và lớp
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="⚙️ CẤU HÌNH TÀI KHOẢN & LỚP")
        # Tab 2: Theo dõi tiến trình
        self.monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitor_frame, text="📊 THEO DÕI TIẾN TRÌNH")
        # Khởi tạo widget cho từng tab
        self.setup_config_tab()
        self.setup_monitor_tab()
    
    def setup_config_tab(self):
        """Tab cấu hình tài khoản và chọn lớp"""
        
        # Main frame with scrollbar
        canvas = tk.Canvas(self.config_frame)
        scrollbar = ttk.Scrollbar(self.config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="🎯 CẤU HÌNH ULSA AUTOMATION", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(10, 20))
        
        # ===========================================
        # SECTION 1: THÔNG TIN ĐĂNG NHẬP  
        # ===========================================
        login_frame = ttk.LabelFrame(scrollable_frame, text=" 👤 THÔNG TIN ĐĂNG NHẬP ", padding="15")
        login_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Mã sinh viên
        ttk.Label(login_frame, text="🎓 Mã sinh viên:", font=('Arial', 11)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.student_id_entry = ttk.Entry(login_frame, width=30, font=('Arial', 11))
        self.student_id_entry.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Mật khẩu
        ttk.Label(login_frame, text="🔐 Mật khẩu:", font=('Arial', 11)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(login_frame, width=30, show="*", font=('Arial', 11))
        self.password_entry.grid(row=1, column=1, padx=(10, 0), pady=5)
        
        # ===========================================
        # SECTION 2: QUẢN LÝ LỚP TÍN CHỈ

        # ===========================================
        course_frame = ttk.LabelFrame(scrollable_frame, text=" 📚 QUẢN LÝ LỚP TÍN CHỈ ", padding="15")
        course_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        # ĐÃ BỎ: Listbox chọn môn học và lớp học đã lưu
        
        # Input nhiều dòng - paste hàng loạt
        bulk_frame = ttk.LabelFrame(course_frame, text=" 📋 NHẬP NHANH NHIỀU LỚP (Paste nhiều dòng) ", padding="10")
        bulk_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(bulk_frame, text="💡 Hướng dẫn: Paste nhiều dòng (mã lớp, tên lớp...). Hệ thống tự động lọc!", 
                 font=('Arial', 9, 'italic'), foreground='blue').pack(anchor=tk.W, pady=(0, 5))
        
        self.bulk_input = scrolledtext.ScrolledText(bulk_frame, width=80, height=8, font=('Consolas', 10))
        self.bulk_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Placeholder text
        placeholder = """Ví dụ:
THML0723H_D21QL.03_LT
1121010771
CNSO1322H_D21QL.09_LT
1121010771
..."""
        self.bulk_input.insert('1.0', placeholder)
        self.bulk_input.config(foreground='gray')
        
        def on_focus_in(event):
            if self.bulk_input.get('1.0', 'end-1c') == placeholder:
                self.bulk_input.delete('1.0', tk.END)
                self.bulk_input.config(foreground='black')
        
        def on_focus_out(event):
            if not self.bulk_input.get('1.0', 'end-1c').strip():
                self.bulk_input.insert('1.0', placeholder)
                self.bulk_input.config(foreground='gray')
        
        self.bulk_input.bind('<FocusIn>', on_focus_in)
        self.bulk_input.bind('<FocusOut>', on_focus_out)
        
        # Nút phân tích và thêm tự động
        btn_frame = ttk.Frame(bulk_frame)
        btn_frame.pack(pady=5)
        
        parse_btn = ttk.Button(btn_frame, text="🔍 Phân tích & Thêm tự động", command=self.parse_and_add_courses)
        parse_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(btn_frame, text="🗑️ Xóa ô nhập", command=self.clear_bulk_input)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Danh sách lớp đã chọn
        list_frame = ttk.Frame(course_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(list_frame, text="📋 Danh sách lớp đã chọn:", font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        
        # Treeview để hiển thị danh sách
        columns = ('STT', 'Môn học', 'Lớp')
        self.course_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        self.course_tree.heading('STT', text='STT')
        self.course_tree.heading('Môn học', text='Tên môn học') 
        self.course_tree.heading('Lớp', text='Tên lớp')
        
        self.course_tree.column('STT', width=50)
        self.course_tree.column('Môn học', width=200)
        self.course_tree.column('Lớp', width=200)
        
        self.course_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Nút xóa lớp đã chọn
        delete_btn = ttk.Button(list_frame, text="🗑️ Xóa lớp đã chọn", command=self.delete_course)
        delete_btn.pack(pady=5)
        
        # ===========================================
        # SECTION 3: ĐIỀU KHIỂN
        # ===========================================
        control_frame = ttk.LabelFrame(scrollable_frame, text=" 🎮 ĐIỀU KHIỂN ", padding="15")
        control_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack()
        
        # Nút lưu cấu hình
        save_btn = ttk.Button(btn_frame, text="💾 Lưu cấu hình", command=self.save_config)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # Nút load cấu hình
        load_btn = ttk.Button(btn_frame, text="📂 Tải cấu hình", command=self.load_config)
        load_btn.pack(side=tk.LEFT, padx=10)
        
        # Nút check mã học phần & lớp
        check_class_btn = ttk.Button(btn_frame, text="🔍 Check mã học phần & lớp", command=self.check_course_and_class)
        check_class_btn.pack(side=tk.LEFT, padx=10)
        
        # Nút check trùng lịch
        check_schedule_btn = ttk.Button(btn_frame, text="📅 Check trùng lịch", command=self.check_schedule_only)
        check_schedule_btn.pack(side=tk.LEFT, padx=10)
        
        # Nút gợi ý lớp thay thế
        suggest_btn = ttk.Button(btn_frame, text="💡 Gợi ý lớp thay thế", command=self.suggest_alternative_classes)
        suggest_btn.pack(side=tk.LEFT, padx=10)
        
        # Nút xem thời khóa biểu
        timetable_btn = ttk.Button(btn_frame, text="📅 Xem thời khóa biểu", command=self.show_timetable)
        timetable_btn.pack(side=tk.LEFT, padx=10)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_monitor_tab(self):
        """Tab theo dõi tiến trình với pause/resume"""
        
        main_frame = ttk.Frame(self.monitor_frame, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📊 THEO DÕI TIẾN TRÌNH AUTOMATION", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text=" 📈 TRẠNG THÁI HỆ THỐNG ", padding="15")
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = ttk.Label(status_frame, text="📢 Trạng thái: SẴN SÀNG", 
                                     font=('Arial', 12, 'bold'), foreground='green')
        self.status_label.pack(anchor=tk.W, pady=2)
        
        self.step_label = ttk.Label(status_frame, text="🔄 Bước hiện tại: Chưa bắt đầu", 
                                   font=('Arial', 11))
        self.step_label.pack(anchor=tk.W, pady=2)
        
        self.time_label = ttk.Label(status_frame, text="⏰ Thời gian: --:--:--")
        self.time_label.pack(anchor=tk.W, pady=2)
        
        # Progress bar
        progress_frame = ttk.Frame(status_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(progress_frame, text="📊 Tiến độ:").pack(anchor=tk.W)
        self.progress = ttk.Progressbar(progress_frame, length=500, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.pack(anchor=tk.W)
        
        # Control buttons cho automation
        control_frame = ttk.LabelFrame(main_frame, text=" 🎮 ĐIỀU KHIỂN AUTOMATION ", padding="15")
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        btn_frame1 = ttk.Frame(control_frame)
        btn_frame1.pack(pady=5)
        
        btn_frame2 = ttk.Frame(control_frame)
        btn_frame2.pack(pady=5)
        
        # Hàng 1: START và STOP
        self.start_btn = ttk.Button(btn_frame1, text="🚀 BẮT ĐẦU AUTOMATION", 
                                   command=self.start_automation, width=25)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = ttk.Button(btn_frame1, text="🛑 DỪNG AUTOMATION", 
                                  command=self.stop_automation, width=25)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Hàng 2: PAUSE và RESUME
        self.pause_btn = ttk.Button(btn_frame2, text="⏸️ TẠM DỪNG", 
                                   command=self.pause_automation, width=25)
        self.pause_btn.pack(side=tk.LEFT, padx=10)
        
        self.resume_btn = ttk.Button(btn_frame2, text="▶️ TIẾP TỤC", 
                                    command=self.resume_automation, width=25)
        self.resume_btn.pack(side=tk.LEFT, padx=10)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text=" 📋 LOG AUTOMATION ", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=90, height=15, 
                                                 font=('Consolas', 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial button states
        self.pause_btn.config(state='disabled')
        self.resume_btn.config(state='disabled')
        self.stop_btn.config(state='disabled')
        
        # Initial log
        self.log_message("🎯 Monitor đã sẵn sàng!")
        self.log_message("💡 Chuyển sang tab 'CẤU HÌNH' để nhập thông tin trước")
        
        # Start time updater
        self.update_time()
    
    def add_course(self):
        """Thêm lớp tín chỉ vào danh sách"""
        subject = self.subject_entry.get().strip()
        class_name = self.class_entry.get().strip()
        
        if not subject or not class_name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ tên môn học và tên lớp!")
            return
        
        # Kiểm tra trùng lặp trước khi thêm
        if not self.check_and_handle_duplicates(subject, class_name):
            return
        
        # Thêm vào treeview
        item_count = len(self.course_tree.get_children())
        self.course_tree.insert('', 'end', values=(item_count + 1, subject, class_name))
        
        # Clear inputs
        self.subject_entry.delete(0, tk.END)
        self.class_entry.delete(0, tk.END)
        
        messagebox.showinfo("Thành công", f"Đã thêm: {subject} - {class_name}")
        
        # Kiểm tra trùng lặp sau khi thêm xong tất cả
        self.check_duplicates_after_adding()
    
    def delete_course(self):
        """Xóa lớp đã chọn"""
        selected = self.course_tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn lớp cần xóa!")
            return
        
        for item in selected:
            self.course_tree.delete(item)
        
        # Cập nhật lại STT
        for i, child in enumerate(self.course_tree.get_children()):
            self.course_tree.item(child, values=(i + 1, 
                                                self.course_tree.item(child)['values'][1],
                                                self.course_tree.item(child)['values'][2]))
        
        messagebox.showinfo("Thành công", "Đã xóa lớp đã chọn!")
    
    def parse_and_add_courses(self):
        """Phân tích dữ liệu paste nhiều dòng, tự động tìm kiếm trong Excel và thêm vào danh sách"""
        raw_text = self.bulk_input.get('1.0', 'end-1c').strip()
        
        if not raw_text or raw_text == """Ví dụ:
THML0723H_D21QL.03_LT
1121010771
CNSO1322H_D21QL.09_LT
1121010771
...""":
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng paste dữ liệu vào ô nhập!")
            return
        
        # Kiểm tra file Excel
        excel_file = "lophoc.xlsx"
        if not os.path.exists(excel_file):
            messagebox.showerror("Lỗi", f"Không tìm thấy file {excel_file}!\nCần file này để tìm kiếm tên lớp chính xác.")
            return
        
        try:
            # Đọc Excel
            self.log_message("📂 Đang đọc file Excel để tìm kiếm...")
            df = pd.read_excel(excel_file)
            
            lines = raw_text.split('\n')
            
            added_count = 0
            skipped_count = 0
            not_found = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Bỏ qua nếu dòng toàn số (mã sinh viên)
                if line.isdigit():
                    skipped_count += 1
                    continue
                
                # Bỏ qua dòng quá ngắn (< 5 ký tự)
                if len(line) < 5:
                    skipped_count += 1
                    continue
                
                # Tìm tên lớp trong dòng văn bản (pattern: XXXX####X_XXX_LT/TH/BT)
                # Format chuẩn: Mã_môn (chữ+số+chữ) _ Tên_lớp _ Loại (LT/TH/BT)
                # Ví dụ: KTPT0522H_D20QL03_LT, TLLĐ0322H_D20QL.01_LT
                class_name_match = re.search(r'\b([A-ZĐĂÂÊÔƠƯA-Za-z0-9РТ]{4,12}_[A-ZĐĂÂÊÔƠƯA-Za-z0-9\.РТ]{3,20}_(?:LT|TH|BT|L|T|B))\b', line, re.IGNORECASE)
                
                if class_name_match:
                    # Tìm thấy tên lớp trong dòng
                    extracted_class = class_name_match.group(1).strip()
                    self.log_message(f"🔍 Tìm thấy tên lớp trong dòng: {extracted_class}")
                    line = extracted_class  # Dùng tên lớp đã trích xuất
                else:
                    # Không tìm thấy tên lớp rõ ràng, dùng toàn bộ dòng
                    self.log_message(f"🔍 Xử lý: {line}")
                
                # Tách mã môn (phần trước dấu _ đầu tiên)
                if '_' in line:
                    subject_code = line.split('_')[0].strip()
                else:
                    subject_code = line.strip()
                
                self.log_message(f"  📚 Bước 1: Tìm mã môn '{subject_code}'")
                
                # Kiểm tra mã môn có tồn tại không (exact match trước)
                subject_rows = df[df['Mã_học_phần'] == subject_code]
                
                if subject_rows.empty:
                    # Không tìm thấy exact → Thử fuzzy search mã môn
                    self.log_message(f"  ⚠️ Không tìm thấy exact, thử fuzzy search mã môn...")
                    # Lọc bỏ NaN/None trước khi fuzzy search
                    all_subject_codes = df['Mã_học_phần'].dropna().unique().tolist()
                    
                    best_match_score = 0
                    best_match_code = None
                    
                    for code in all_subject_codes:
                        # Đảm bảo code là string
                        if not isinstance(code, str):
                            continue
                        score = max(
                            fuzz.ratio(subject_code.upper(), code.upper()),
                            fuzz.partial_ratio(subject_code.upper(), code.upper()),
                            fuzz.token_sort_ratio(subject_code.upper(), code.upper())
                        )
                        if score > best_match_score:
                            best_match_score = score
                            best_match_code = code
                    
                    if best_match_score >= 70:
                        # Tìm thấy mã môn gần đúng
                        self.log_message(f"  ✅ Tìm thấy mã môn gần đúng: {best_match_code} (độ khớp: {best_match_score}%)")
                        subject_code = best_match_code  # Dùng mã môn đúng
                        subject_rows = df[df['Mã_học_phần'] == subject_code]
                    else:
                        # Không tìm thấy mã môn
                        self.log_message(f"  ❌ Không tìm thấy mã môn '{subject_code}' trong Excel!")
                        not_found.append(line)
                        skipped_count += 1
                        messagebox.showerror("Lỗi", f"❌ Không tìm thấy mã môn: {subject_code}\n\nVui lòng kiểm tra lại!")
                        continue
                else:
                    self.log_message(f"  ✅ Tìm thấy mã môn '{subject_code}'")
                
                # BƯỚC 2: Tìm tên lớp cụ thể
                self.log_message(f"  🏫 Bước 2: Tìm lớp '{line}'")
                
                # Thử tìm chính xác
                exact_match = df[df['Tên_lớp_tín_chỉ'] == line]
                
                if not exact_match.empty:
                    # Tìm thấy chính xác → Thêm luôn
                    subject_name = exact_match.iloc[0]['Tên_học_phần']
                    class_name = exact_match.iloc[0]['Tên_lớp_tín_chỉ']
                    
                    item_count = len(self.course_tree.get_children())
                    self.course_tree.insert('', 'end', values=(item_count + 1, subject_code, class_name))
                    added_count += 1
                    self.log_message(f"  ✅ Thêm thành công: {subject_name} - {class_name}")
                else:
                    # Không tìm thấy chính xác → Tìm gần đúng nhất (fuzzy search)
                    self.log_message(f"  ⚠️ Không tìm thấy lớp '{line}'")
                    self.log_message(f"  🔍 Tìm lớp gần đúng nhất cùng môn...")
                    
                    # Lấy tất cả lớp cùng mã môn
                    same_subject_classes = subject_rows[['Tên_học_phần', 'Tên_lớp_tín_chỉ', 'Lịch_học', 'Còn_trống']].copy()
                    
                    if not same_subject_classes.empty:
                        # Tìm lớp gần đúng nhất (fuzzy search với nhiều phương pháp)
                        all_class_names = same_subject_classes['Tên_lớp_tín_chỉ'].tolist()
                        
                        # Thử nhiều scorer để tìm match tốt nhất
                        best_ratio = process.extractOne(line, all_class_names, scorer=fuzz.ratio)
                        best_partial = process.extractOne(line, all_class_names, scorer=fuzz.partial_ratio)
                        best_token = process.extractOne(line, all_class_names, scorer=fuzz.token_sort_ratio)
                        
                        # Chọn match tốt nhất
                        candidates = [best_ratio, best_partial, best_token]
                        best_match = max(candidates, key=lambda x: x[1] if x else 0)
                        
                        if best_match and best_match[1] >= 70:  # Độ tương đồng >= 70%
                            matched_class = best_match[0]
                            matched_row = same_subject_classes[same_subject_classes['Tên_lớp_tín_chỉ'] == matched_class].iloc[0]
                            subject_name = matched_row['Tên_học_phần']
                            
                            item_count = len(self.course_tree.get_children())
                            self.course_tree.insert('', 'end', values=(item_count + 1, subject_code, matched_class))
                            added_count += 1
                            self.log_message(f"  💡 Tìm gần đúng ({best_match[1]}%): {matched_class}")
                            
                            # Hiển thị cảnh báo nếu input khác với kết quả
                            if line != matched_class:
                                self.log_message(f"      ⚠️ Input: {line} → Tìm thấy: {matched_class}")
                        else:
                            # Không tìm thấy lớp gần đúng
                            not_found.append(line)
                            skipped_count += 1
                            self.log_message(f"  ❌ Không tìm thấy lớp tương tự")
                    else:
                        # Không có lớp nào cùng môn
                        not_found.append(line)
                        skipped_count += 1
                        self.log_message(f"  ❌ ĐÃ HẾT LỚP! Không có lớp nào của môn {subject_code}")
                        messagebox.showwarning("Đã hết lớp", 
                                             f"❌ ĐÃ HẾT LỚP!\n\n"
                                             f"Môn: {subject_code}\n"
                                             f"Lớp tìm: {line}\n\n"
                                             f"Không còn lớp nào khác của môn này trong hệ thống.")
            
            # Kiểm tra và xử lý trùng lặp sau khi thêm tất cả
            self.log_message("🔍 Kiểm tra trùng lặp...")
            self.check_duplicates_after_adding()
            
            # Hiển thị kết quả
            result_msg = f"✅ Đã thêm {added_count} lớp\n"
            result_msg += f"⏭️ Đã bỏ qua {skipped_count} dòng\n"
            
            if not_found:
                result_msg += f"\n❌ Không tìm thấy:\n"
                result_msg += "\n".join([f"  - {item}" for item in not_found[:5]])
                if len(not_found) > 5:
                    result_msg += f"\n  ... và {len(not_found) - 5} lớp khác"
            
            if added_count > 0:
                messagebox.showinfo("Hoàn thành", result_msg)
                self.clear_bulk_input()
            else:
                messagebox.showwarning("Kết quả", result_msg)
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi đọc Excel: {e}")
            self.log_message(f"❌ Lỗi: {e}")
            import traceback
            self.log_message(traceback.format_exc())
    
    def clear_bulk_input(self):
        """Xóa nội dung ô nhập bulk"""
        self.bulk_input.delete('1.0', tk.END)
        placeholder = """Ví dụ:
THML0723H_D21QL.03_LT
1121010771
CNSO1322H_D21QL.09_LT
1121010771
..."""
        self.bulk_input.insert('1.0', placeholder)
        self.bulk_input.config(foreground='gray')
    
    def check_and_handle_duplicates(self, subject, class_name):
        """Kiểm tra trùng lặp trước khi thêm (cho add_course thủ công)"""
        for child in self.course_tree.get_children():
            values = self.course_tree.item(child)['values']
            if len(values) >= 3:
                existing_subject = values[1].strip()
                existing_class = values[2].strip()
                
                # Trùng hoàn toàn
                if existing_subject == subject and existing_class == class_name:
                    messagebox.showwarning("Trùng lặp", f"Lớp này đã tồn tại:\n{subject} - {class_name}")
                    return False
        return True
    
    def check_duplicates_after_adding(self):
        """Kiểm tra và xử lý trùng lặp sau khi thêm hàng loạt"""
        courses = []
        
        # Thu thập tất cả lớp
        for child in self.course_tree.get_children():
            values = self.course_tree.item(child)['values']
            if len(values) >= 3:
                courses.append({
                    'id': child,
                    'subject': values[1].strip(),
                    'class': values[2].strip()
                })
        
        # Tìm trùng lặp
        exact_duplicates = []  # Trùng hoàn toàn (môn + lớp)
        subject_duplicates = {}  # Cùng môn, khác lớp
        
        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                c1 = courses[i]
                c2 = courses[j]
                
                # Trùng hoàn toàn
                if c1['subject'] == c2['subject'] and c1['class'] == c2['class']:
                    if (c1['id'], c2['id']) not in exact_duplicates:
                        exact_duplicates.append((c1['id'], c2['id']))
                
                # Cùng môn, khác lớp
                elif c1['subject'] == c2['subject']:
                    key = c1['subject']
                    if key not in subject_duplicates:
                        subject_duplicates[key] = []
                    # Tránh trùng lặp trong danh sách
                    if c1 not in subject_duplicates[key]:
                        subject_duplicates[key].append(c1)
                    if c2 not in subject_duplicates[key]:
                        subject_duplicates[key].append(c2)
        
        # Xử lý trùng hoàn toàn - Tự động xóa
        removed_exact = []
        if exact_duplicates:
            for dup_id1, dup_id2 in exact_duplicates:
                try:
                    # Lấy thông tin trước khi xóa
                    values = self.course_tree.item(dup_id2)['values']
                    removed_exact.append(f"{values[1]} - {values[2]}")
                    # Xóa item thứ 2, giữ item đầu tiên
                    self.course_tree.delete(dup_id2)
                except:
                    pass
            
            # Cập nhật lại STT
            self.update_course_numbers()
            
            if removed_exact:
                msg = f"🗑️ ĐÃ TỰ ĐỘNG XÓA {len(removed_exact)} LỚP TRÙNG LẶP:\n\n"
                msg += "\n".join([f"  • {item}" for item in removed_exact])
                self.log_message(f"🗑️ Đã tự động xóa {len(removed_exact)} lớp trùng lặp hoàn toàn")
                messagebox.showinfo("Đã xóa trùng lặp", msg)
        
        # Xử lý cùng môn, khác lớp - Tự động xóa lớp sau, giữ lớp đầu
        removed_subject = []
        if subject_duplicates:
            for subject, courses_list in subject_duplicates.items():
                # Giữ lớp đầu tiên, xóa các lớp sau
                for i in range(1, len(courses_list)):
                    try:
                        course = courses_list[i]
                        removed_subject.append(f"{course['subject']} - {course['class']}")
                        self.course_tree.delete(course['id'])
                    except:
                        pass
            
            # Cập nhật lại STT
            self.update_course_numbers()
            
            if removed_subject:
                msg = f"🗑️ ĐÃ TỰ ĐỘNG XÓA {len(removed_subject)} LỚP TRÙNG MÔN:\n\n"
                msg += "\n".join([f"  • {item}" for item in removed_subject])
                msg += f"\n\n💡 Đã giữ lại lớp đầu tiên của mỗi môn"
                self.log_message(f"🗑️ Đã tự động xóa {len(removed_subject)} lớp trùng môn")
                messagebox.showinfo("Đã xóa trùng môn", msg)
    
    def update_course_numbers(self):
        """Cập nhật lại số thứ tự trong Treeview"""
        for i, child in enumerate(self.course_tree.get_children(), start=1):
            values = list(self.course_tree.item(child)['values'])
            values[0] = i
            self.course_tree.item(child, values=values)
    
    def show_duplicate_subject_dialog(self, subject_duplicates):
        """Hiển thị dialog cho user chọn lớp cần xóa khi cùng môn nhưng khác lớp"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚠️ Phát hiện trùng môn học")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_text = "⚠️ PHÁT HIỆN CÁC MÔN HỌC BỊ TRÙNG\n\n"
        title_text += "Các môn học sau có nhiều lớp khác nhau.\n"
        title_text += "Vui lòng chọn lớp cần XÓA (giữ lớp không tích chọn):"
        
        title_label = ttk.Label(main_frame, text=title_text, font=('Arial', 11, 'bold'), justify=tk.LEFT)
        title_label.pack(pady=(0, 10))
        
        # Scrollable frame
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Checkboxes cho từng môn
        to_delete = []
        
        for subject, courses_list in subject_duplicates.items():
            subject_frame = ttk.LabelFrame(scrollable_frame, text=f" 📚 Môn: {subject} ", padding="10")
            subject_frame.pack(fill=tk.X, pady=10, padx=5)
            
            ttk.Label(subject_frame, text=f"Có {len(courses_list)} lớp khác nhau. Chọn lớp cần XÓA:", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
            
            for course in courses_list:
                var = tk.BooleanVar(value=False)
                checkbox = ttk.Checkbutton(subject_frame, 
                                          text=f"❌ Xóa: {course['class']}", 
                                          variable=var)
                checkbox.pack(anchor=tk.W, pady=2)
                to_delete.append({'var': var, 'id': course['id'], 'class': course['class']})
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def on_ok():
            deleted_count = 0
            for item in to_delete:
                if item['var'].get():
                    try:
                        self.course_tree.delete(item['id'])
                        deleted_count += 1
                        self.log_message(f"🗑️ Đã xóa: {item['class']}")
                    except:
                        pass
            
            if deleted_count > 0:
                self.update_course_numbers()
                messagebox.showinfo("Hoàn thành", f"Đã xóa {deleted_count} lớp được chọn!")
            
            dialog.destroy()
        
        def on_skip():
            self.log_message("⏭️ Bỏ qua xử lý trùng môn")
            dialog.destroy()
        
        ok_btn = ttk.Button(btn_frame, text="✅ Xóa các lớp đã chọn", command=on_ok, width=20)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        skip_btn = ttk.Button(btn_frame, text="⏭️ Bỏ qua", command=on_skip, width=20)
        skip_btn.pack(side=tk.LEFT, padx=5)
    
    def show_class_selection_dialog(self, subject_code, subject_name, original_class, available_classes, df):
        """Hiển thị dialog cho user chọn lớp thay thế, tự động chọn sau 60s"""
        dialog = tk.Toplevel(self.root)
        dialog.title("💡 Chọn lớp thay thế")
        dialog.geometry("900x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Biến lưu kết quả
        result = {'selected_class': None, 'cancelled': False}
        countdown = {'value': 60}
        
        # Frame chính
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_text = f"⚠️ Không tìm thấy lớp: {original_class}\n\n"
        title_text += f"📚 Môn: {subject_name} (Mã: {subject_code})\n\n"
        title_text += f"💡 Các lớp còn lại của môn này:\n"
        title_text += f"   ✅ = Phù hợp với thời khóa biểu\n"
        title_text += f"   🔴 = Trùng lịch\n\n"
        title_text += f"🎯 Hành động:\n"
        title_text += f"   • Chọn lớp + bấm OK → Lưu lớp đó\n"
        title_text += f"   • Đợi 60s → Tự động chọn lớp phù hợp nhất\n"
        title_text += f"   • Bấm Hủy → Bỏ qua lớp này"
        
        title_label = ttk.Label(main_frame, text=title_text, font=('Arial', 10), justify=tk.LEFT)
        title_label.pack(pady=(0, 10))
        
        # Countdown label
        countdown_label = ttk.Label(main_frame, 
                                   text=f"⏱️ Tự động chọn lớp phù hợp sau: {countdown['value']}s", 
                                   font=('Arial', 12, 'bold'), foreground='red')
        countdown_label.pack(pady=5)
        
        # Frame với scrollbar (KHÔNG expand để còn chỗ cho nút)
        list_frame = ttk.LabelFrame(main_frame, text=" 📋 CÁC LỚP CÒN LẠI ", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=False, pady=10)
        
        canvas = tk.Canvas(list_frame, height=350)  # Giới hạn chiều cao
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Radio buttons
        var = tk.StringVar(value="")
        
        # Lấy lịch học hiện tại để check trùng
        current_schedules = []
        for child in self.course_tree.get_children():
            values = self.course_tree.item(child)['values']
            if len(values) >= 3:
                class_name = values[2].strip()
                matching_rows = df[df['Tên_lớp_tín_chỉ'] == class_name]
                if not matching_rows.empty:
                    schedule = matching_rows.iloc[0]['Lịch_học']
                    if pd.notna(schedule):
                        current_schedules.append(str(schedule))
        
        # Hiển thị từng lớp và tìm lớp phù hợp nhất
        best_class = None  # Lớp phù hợp nhất (không trùng lịch, có slot trống)
        
        for idx, row in available_classes.iterrows():
            class_name = row['Tên_lớp_tín_chỉ']  # TÊN LỚP ĐẦY ĐỦ (vd: CNSO1322H_D21QL.01_LT)
            schedule = str(row['Lịch_học']) if pd.notna(row['Lịch_học']) else "Chưa có lịch"
            slots = row['Còn_trống'] if pd.notna(row['Còn_trống']) else "?"
            
            # Check trùng lịch với thời khóa biểu hiện tại
            has_conflict = False
            if pd.notna(row['Lịch_học']):
                for existing_schedule in current_schedules:
                    if str(row['Lịch_học']) == existing_schedule or self.check_time_overlap(str(row['Lịch_học']), existing_schedule):
                        has_conflict = True
                        break
            
            # Tạo frame cho từng option
            option_frame = ttk.Frame(scrollable_frame)
            option_frame.pack(fill=tk.X, pady=5, padx=5)
            
            conflict_icon = "🔴 TRÙNG LỊCH " if has_conflict else "✅ PHÙ HỢP "
            text = f"{conflict_icon}{class_name}\n    📅 Lịch: {schedule}\n    💺 Còn trống: {slots}"
            
            radio = ttk.Radiobutton(option_frame, text=text, variable=var, value=class_name)
            radio.pack(anchor=tk.W)
            
            # Tìm lớp phù hợp nhất: Không trùng lịch + Có slot trống
            if not has_conflict and best_class is None:
                best_class = class_name
                var.set(class_name)  # Tự động chọn sẵn lớp phù hợp nhất
        
        # Nếu không có lớp nào phù hợp, chọn lớp đầu tiên
        if var.get() == "" and not available_classes.empty:
            first_class = available_classes.iloc[0]['Tên_lớp_tín_chỉ']
            var.set(first_class)
            self.log_message(f"  ⚠️ Tất cả lớp đều trùng lịch, tự động chọn: {first_class}")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def on_ok():
            selected = var.get()
            if selected:
                result['selected_class'] = selected
                dialog.destroy()
            else:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn một lớp!")
        
        def on_cancel():
            result['cancelled'] = True
            dialog.destroy()
        
        def update_countdown():
            if countdown['value'] > 0 and dialog.winfo_exists():
                countdown['value'] -= 1
                countdown_label.config(text=f"⏱️ Tự động chọn lớp phù hợp sau: {countdown['value']}s")
                dialog.after(1000, update_countdown)
            elif countdown['value'] == 0 and dialog.winfo_exists():
                # Hết thời gian → Tự động chọn lớp phù hợp nhất (đã được chọn sẵn)
                selected = var.get()
                if selected:
                    result['selected_class'] = selected
                    self.log_message(f"  ⏰ HẾT 60s → Tự động chọn lớp phù hợp với TKB: {selected}")
                    dialog.destroy()
                else:
                    result['cancelled'] = True
                    self.log_message(f"  ⚠️ Không có lớp nào được chọn")
                    dialog.destroy()
        
        ok_btn = ttk.Button(btn_frame, text="✅ OK", command=on_ok, width=15)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="❌ Hủy", command=on_cancel, width=15)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bắt đầu đếm ngược
        update_countdown()
        
        # Đợi dialog đóng
        dialog.wait_window()
        
        # Trả về kết quả
        if result['cancelled']:
            return None
        return result['selected_class']
    
    def save_config(self):
        """Lưu cấu hình vào file JSON đúng chuẩn auto_config.json (login_info, course_selections)"""
        student_id = self.student_id_entry.get().strip()
        password = self.password_entry.get().strip()
        if not student_id or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ mã sinh viên và mật khẩu!")
            return
        # Thu thập danh sách lớp
        subject_names = []
        class_names = []
        for child in self.course_tree.get_children():
            values = self.course_tree.item(child)['values']
            # Chỉ lưu nếu cả subject và class đều có dữ liệu
            if len(values) >= 3 and values[1] and values[2]:
                subject_names.append(values[1])
                class_names.append(values[2])
        if not subject_names or not class_names:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng thêm ít nhất 1 lớp tín chỉ!")
            return
        if len(subject_names) != len(class_names):
            messagebox.showerror("Lỗi dữ liệu", "Số lượng tên môn học và tên lớp không khớp!")
            return
        config_data = {
            "login_info": {
                "student_id": student_id,
                "password": password
            },
            "course_selections": {
                "subject_names_b1": subject_names,
                "class_names_b2": class_names
            },
            "created_time": datetime.now().isoformat()
        }
        # Giữ lại automation_settings nếu có
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                if 'automation_settings' in old_data:
                    config_data['automation_settings'] = old_data['automation_settings']
        except Exception:
            pass
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Thành công", f"Đã lưu cấu hình vào {self.config_file}!")
            self.log_message(f"💾 Đã lưu cấu hình: {len(subject_names)} lớp vào file: {os.path.abspath(self.config_file)}")
            # Cập nhật tiêu đề sau khi lưu
            self.update_title()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cấu hình: {e}\nFile: {os.path.abspath(self.config_file)}")
            self.log_message(f"❌ Lỗi lưu file: {os.path.abspath(self.config_file)}: {e}")
    
    def load_config(self):
        """Load cấu hình từ file"""
        self.load_existing_config()
    
    def load_existing_config(self):
        """Load cấu hình hiện có (login_info, course_selections) và tự động load vào Treeview"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                # Load login info
                login_info = config_data.get('login_info', {})
                self.student_id_entry.delete(0, tk.END)
                self.student_id_entry.insert(0, login_info.get('student_id', ''))
                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, login_info.get('password', ''))
                # Load courses từ course_selections vào Treeview
                self.course_tree.delete(*self.course_tree.get_children())
                course_selections = config_data.get('course_selections', {})
                subject_names = course_selections.get('subject_names_b1', [])
                class_names = course_selections.get('class_names_b2', [])
                for i, (subject, class_name) in enumerate(zip(subject_names, class_names)):
                    self.course_tree.insert('', 'end', values=(
                        i + 1,
                        subject,
                        class_name
                    ))
                self.log_message(f"📂 Đã load cấu hình: {len(subject_names)} lớp")
        except Exception as e:
            self.log_message(f"⚠️ Không thể load cấu hình: {e}")
    
    def update_title(self):
        """Cập nhật tiêu đề cửa sổ với tên thư mục và mã sinh viên"""
        try:
            student_id = self.student_id_entry.get().strip()
            if student_id:
                self.root.title(f"🎯 {self.folder_name} : {student_id}")
            else:
                self.root.title(f"🎯 {self.folder_name}")
        except Exception as e:
            print(f"⚠️ Lỗi cập nhật tiêu đề: {e}")
    
    def update_time(self):
        """Cập nhật thời gian real-time"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=f"⏰ Thời gian: {current_time}")
        self.root.after(1000, self.update_time)
    
    def log_message(self, message):
        """Thêm message vào log nếu widget đã khởi tạo"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            self.root.update()
        else:
            print(log_entry)
    
    def start_automation(self):
        """Bắt đầu automation và log real-time ra giao diện"""
        import threading
        if not os.path.exists(self.config_file):
            messagebox.showwarning("Chưa có cấu hình", "Vui lòng lưu cấu hình trước khi chạy!")
            return
        self.log_message("🚀 ĐANG KHỞI ĐỘNG AUTOMATION...")
        self.status_label.config(text="📢 Trạng thái: ▶️ ĐANG CHẠY", foreground="green")
        self.step_label.config(text="🔄 Bước hiện tại: Khởi động")
        self.progress['value'] = 10
        self.progress_label.config(text="10%")
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.resume_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        # KHÔNG tự động ghi đè file config khi chạy automation

        # Kiểm tra xem đang chạy từ .exe hay source code
        if getattr(sys, 'frozen', False):
            # Chạy từ .exe - PyInstaller
            self.log_message("🎯 Chạy từ file .exe")
            self.run_automation_direct()
        else:
            # Chạy từ source code - dùng subprocess như cũ
            self.log_message("🐍 Chạy từ Python source")
            self.run_automation_subprocess()
    
    def run_automation_direct(self):
        """Chạy automation trực tiếp (khi build .exe)"""
        try:
            # Redirect stdout để capture log
            import queue
            self.log_queue = queue.Queue()
            
            # Import automation module
            if getattr(sys, 'frozen', False):
                # Thêm automation path vào sys.path
                base_path = sys._MEIPASS
                automation_path = os.path.join(base_path, 'automation')
                if automation_path not in sys.path:
                    sys.path.insert(0, automation_path)
            
            from automation import auto_login_with_title_check
            
            self.log_message("✅ Đã load automation module")
            
            # Tạo class để redirect stdout
            class LogCapture:
                def __init__(self, log_queue):
                    self.log_queue = log_queue
                    self.original_stdout = sys.stdout
                    self.original_stderr = sys.stderr
                
                def write(self, text):
                    if text.strip():
                        self.log_queue.put(text.rstrip())
                    # Chỉ write ra console nếu original_stdout không phải None
                    # (khi chạy .exe với console=False thì stdout là None)
                    if self.original_stdout is not None:
                        try:
                            self.original_stdout.write(text)
                        except:
                            pass
                
                def flush(self):
                    if self.original_stdout is not None:
                        try:
                            self.original_stdout.flush()
                        except:
                            pass
            
            # Redirect stdout/stderr
            log_capture = LogCapture(self.log_queue)
            sys.stdout = log_capture
            sys.stderr = log_capture
            
            # Chạy automation trong thread
            def run_with_redirect():
                try:
                    auto_login_with_title_check.main(gui_mode=True)  # Pass gui_mode=True để không gọi input()
                except Exception as e:
                    self.log_queue.put(f"❌ Lỗi: {e}")
                finally:
                    # Restore stdout/stderr
                    sys.stdout = log_capture.original_stdout
                    sys.stderr = log_capture.original_stderr
            
            threading.Thread(target=run_with_redirect, daemon=True).start()
            
            # Tạo thread đọc log từ queue
            threading.Thread(target=self.read_queue_output, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"❌ Lỗi khi khởi động automation: {e}")
            import traceback
            self.log_message(traceback.format_exc())
    
    def run_automation_subprocess(self):
        """Chạy automation qua subprocess (khi dev từ source)"""
        # Đảm bảo PYTHONIOENCODING để log không lỗi Unicode
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        # Đường dẫn tuyệt đối tới python.exe và script automation dựa trên vị trí file GUI
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "automation", "auto_login_with_title_check.py")
        
        # Tìm Python - thử nhiều vị trí
        python_exe = None
        python_candidates = [
            os.path.join(script_dir, ".venv", "Scripts", "python.exe"),  # Trong .venv local
            "python",  # Python trong PATH
            "py"       # Python launcher
        ]
        
        for candidate in python_candidates:
            if candidate in ["python", "py"]:
                # Thử chạy để kiểm tra
                try:
                    result = subprocess.run([candidate, "--version"], capture_output=True, timeout=2)
                    if result.returncode == 0:
                        python_exe = candidate
                        break
                except:
                    continue
            else:
                # Kiểm tra file tồn tại
                if os.path.exists(candidate):
                    python_exe = candidate
                    break
        
        if not python_exe:
            self.log_message("❌ KHÔNG TÌM THẤY PYTHON!")
            self.log_message("💡 Vui lòng chạy SETUP_FIRST_TIME.bat trước!")
            messagebox.showerror("Lỗi", "Không tìm thấy Python!\n\nVui lòng:\n1. Chạy SETUP_FIRST_TIME.bat\n2. Hoặc cài Python vào hệ thống")
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            return
        
        print(f"🐍 Python: {python_exe}")
        print(f"📜 Script: {script_path}")

        try:
            self.process = subprocess.Popen([
                python_exe, script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, text=True, bufsize=1, encoding='utf-8', cwd=script_dir)
            self.log_message(f"▶️ Đã khởi động: {python_exe} {script_path}")
            # Tạo thread đọc log stdout/stderr
            threading.Thread(target=self.read_process_output, daemon=True).start()
        except Exception as e:
            self.log_message(f"❌ Lỗi khi khởi động automation: {e}")
    
    def read_queue_output(self):
        """Đọc log từ queue (khi chạy direct từ .exe)"""
        while True:
            try:
                if hasattr(self, 'log_queue'):
                    line = self.log_queue.get(timeout=0.1)
                    if line:
                        self.log_message(line)
                else:
                    break
            except:
                time.sleep(0.1)
                continue

    def read_process_output(self):
        """Đọc log stdout/stderr từ process và hiển thị lên GUI"""
        if not self.process:
            return
        try:
            for line in self.process.stdout:
                if line:
                    self.log_message(line.rstrip())
        except Exception as e:
            self.log_message(f"[LOG ERROR] {e}")
    
    def pause_automation(self):
        """Tạm dừng automation"""
        self.log_message("⏸️ ĐANG TẠM DỪNG AUTOMATION...")
        self.status_label.config(text="📢 Trạng thái: ⏸️ TẠM DỪNG", foreground="orange")
        self.step_label.config(text="🔄 Bước hiện tại: Đã tạm dừng")
        
        try:
            import json
            pause_data = {
                "state": "PAUSED",
                "current_step": "User paused from GUI",
                "progress": 50,
                "timestamp": datetime.now().isoformat()
            }
            
            with open("pause_signal.json", "w", encoding="utf-8") as f:
                json.dump(pause_data, f, ensure_ascii=False, indent=2)
            
            self.log_message("✅ ĐÃ GỬI TÍN HIỆU TẠM DỪNG!")
            
        except Exception as e:
            self.log_message(f"❌ LỖI TẠM DỪNG: {e}")
        
        self.pause_btn.config(state='disabled')
        self.resume_btn.config(state='normal')
    
    def resume_automation(self):
        """Tiếp tục automation"""
        self.log_message("▶️ ĐANG TIẾP TỤC AUTOMATION...")
        self.status_label.config(text="📢 Trạng thái: ▶️ ĐANG CHẠY", foreground="green")
        self.step_label.config(text="🔄 Bước hiện tại: Đã tiếp tục")
        
        try:
            if os.path.exists("pause_signal.json"):
                os.remove("pause_signal.json")
            self.log_message("✅ ĐÃ GỬI TÍN HIỆU TIẾP TỤC!")
            
        except Exception as e:
            self.log_message(f"❌ LỖI TIẾP TỤC: {e}")
        
        self.pause_btn.config(state='normal')
        self.resume_btn.config(state='disabled')
    
    def stop_automation(self):
        """Dừng automation"""
        self.log_message("🛑 ĐANG DỪNG AUTOMATION...")
        
        if self.process:
            try:
                self.process.terminate()
                self.log_message("✅ ĐÃ DỪNG AUTOMATION")
            except:
                self.log_message("⚠️ Process đã kết thúc")
        
        # Clear pause signal
        try:
            if os.path.exists("pause_signal.json"):
                os.remove("pause_signal.json")
        except:
            pass
        
        self.status_label.config(text="📢 Trạng thái: ⏹️ ĐÃ DỪNG", foreground="red")
        self.step_label.config(text="🔄 Bước hiện tại: Đã kết thúc")
        self.progress['value'] = 0
        self.progress_label.config(text="0%")
        
        self.reset_buttons()
    
    def reset_buttons(self):
        """Reset trạng thái nút"""
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self.resume_btn.config(state='disabled')
        self.stop_btn.config(state='disabled')
    
    def check_course_and_class(self):
        """Kiểm tra CẢ mã học phần (tên môn) VÀ tên lớp tín chỉ với file Excel"""
        try:
            # Kiểm tra file Excel có tồn tại không
            excel_file = "lophoc.xlsx"
            if not os.path.exists(excel_file):
                messagebox.showerror("Lỗi", f"Không tìm thấy file {excel_file}!")
                return
            
            # Đọc danh sách từ Treeview
            saved_data = []
            for child in self.course_tree.get_children():
                values = self.course_tree.item(child)['values']
                if len(values) >= 3:
                    saved_data.append({
                        'index': values[0],
                        'subject': values[1],  # Tên môn (sẽ so sánh với Mã_học_phần)
                        'class': values[2]      # Tên lớp (sẽ so sánh với Tên_lớp_tín_chỉ)
                    })
            
            if not saved_data:
                messagebox.showwarning("Cảnh báo", "Chưa có lớp nào được lưu để kiểm tra!")
                return
            
            # Đọc file Excel
            self.log_message("📖 Đang đọc file lophoc.xlsx...")
            df = pd.read_excel(excel_file)
            
            # Lấy danh sách mã học phần và tên lớp từ Excel
            excel_courses = df['Mã_học_phần'].dropna().unique().tolist()
            excel_classes = df['Tên_lớp_tín_chỉ'].dropna().unique().tolist()
            
            # Helper function: Trích xuất mã học phần từ tên lớp
            def extract_course_code(class_name):
                """Trích xuất mã học phần từ tên lớp (phần trước dấu _)"""
                if '_' in class_name:
                    return class_name.split('_')[0]
                return class_name
            
            # Kiểm tra từng môn - CHỈ BÁO ĐÚNG KHI EXACT MATCH 100%
            errors = []
            auto_fixed = False
            
            for idx, item in enumerate(saved_data):
                subject_input = item['subject'].strip()  # Mã môn user nhập
                class_input = item['class'].strip()      # Tên lớp user nhập
                
                # BƯỚC 1: Kiểm tra EXACT MATCH tên lớp trước
                class_exact_match = class_input in excel_classes
                
                # BƯỚC 2: Tìm mã môn đúng từ Excel (dựa vào tên lớp hoặc trích xuất)
                correct_course = None
                correct_class = None
                
                if class_exact_match:
                    # Lớp đúng -> lấy mã môn từ Excel
                    matching_rows = df[df['Tên_lớp_tín_chỉ'] == class_input]
                    if not matching_rows.empty:
                        correct_course = matching_rows.iloc[0]['Mã_học_phần']
                        correct_class = class_input
                else:
                    # Lớp sai -> tìm lớp gần giống
                    best_class_match = process.extractOne(class_input, excel_classes, scorer=fuzz.ratio)
                    if best_class_match and best_class_match[1] >= 85:  # Tăng độ chính xác lên 85%
                        suggested_class_name = best_class_match[0]
                        # Lấy mã môn từ lớp gợi ý
                        matching_rows = df[df['Tên_lớp_tín_chỉ'] == suggested_class_name]
                        if not matching_rows.empty:
                            correct_course = matching_rows.iloc[0]['Mã_học_phần']
                            correct_class = suggested_class_name
                    
                    # Nếu không tìm được, thử trích xuất mã từ tên lớp input
                    if not correct_course:
                        extracted = extract_course_code(class_input)
                        if extracted in excel_courses:
                            correct_course = extracted
                
                # BƯỚC 3: Kiểm tra mã môn user nhập
                course_exact_match = subject_input in excel_courses
                
                # BƯỚC 4: Xác định xem có đúng 100% không
                is_perfect = False
                if course_exact_match and class_exact_match:
                    # Kiểm tra combo có khớp trong Excel không
                    combo_rows = df[
                        (df['Mã_học_phần'] == subject_input) &
                        (df['Tên_lớp_tín_chỉ'] == class_input)
                    ]
                    is_perfect = not combo_rows.empty
                
                # BƯỚC 5: Ghi nhận kết quả
                if is_perfect:
                    # ĐÚNG 100%
                    self.log_message(f"✅ ĐÚNG 100%: [{subject_input}] - [{class_input}]")
                else:
                    # SAI - Cần sửa
                    self.log_message(f"❌ SAI: [{subject_input}] - [{class_input}]")
                    
                    error_info = {
                        'index': idx,
                        'subject_input': subject_input,
                        'class_input': class_input,
                        'correct_course': correct_course,
                        'correct_class': correct_class,
                        'course_exact': course_exact_match,
                        'class_exact': class_exact_match
                    }
                    errors.append(error_info)
                    
                    # Tự động sửa nếu tìm được combo đúng
                    if correct_course and correct_class:
                        # Kiểm tra lại combo có hợp lệ không
                        verify_rows = df[
                            (df['Mã_học_phần'] == correct_course) &
                            (df['Tên_lớp_tín_chỉ'] == correct_class)
                        ]
                        if not verify_rows.empty:
                            children = self.course_tree.get_children()
                            if idx < len(children):
                                child = children[idx]
                                values = list(self.course_tree.item(child)['values'])
                                values[1] = correct_course
                                values[2] = correct_class
                                self.course_tree.item(child, values=tuple(values))
                                auto_fixed = True
                                self.log_message(f"   🔧 Đã sửa thành: [{correct_course}] - [{correct_class}]")
            
            # Hiển thị kết quả
            if errors:
                message = "❌ PHÁT HIỆN LỖI - CHƯA ĐÚNG 100%:\n\n"
                
                for error in errors:
                    message += "="*50 + "\n"
                    message += f"📌 BẠN NHẬP:\n"
                    message += f"   Mã môn: {error['subject_input']}\n"
                    message += f"   Tên lớp: {error['class_input']}\n\n"
                    
                    # Phân tích lỗi
                    if not error['course_exact']:
                        message += f"❌ MÃ MÔN SAI (không tồn tại trong Excel)\n"
                    if not error['class_exact']:
                        message += f"❌ TÊN LỚP SAI (không tồn tại trong Excel)\n"
                    
                    # Gợi ý sửa
                    if error['correct_course'] and error['correct_class']:
                        message += f"\n✅ GỢI Ý SỬA THÀNH:\n"
                        message += f"   Mã môn: {error['correct_course']}\n"
                        message += f"   Tên lớp: {error['correct_class']}\n"
                    else:
                        message += f"\n⚠️ Không tìm thấy lớp tương tự trong Excel!\n"
                    
                    message += "\n"
                
                if auto_fixed:
                    message += "\n✅ Đã TỰ ĐỘNG SỬA các lỗi!\n"
                    message += "⚠️ Vui lòng kiểm tra và nhấn LƯU CẤU HÌNH!"
                else:
                    message += "\n⚠️ Không thể tự động sửa!\n"
                    message += "Vui lòng nhập lại cho chính xác theo Excel."
                    
                messagebox.showwarning("Kết quả kiểm tra", message)
            else:
                message = "✅ TẤT CẢ ĐỀU ĐÚNG!\n\n"
                message += f"🎯 Đã kiểm tra {len(saved_data)} lớp\n"
                message += "✅ Mã học phần: Đúng\n"
                message += "✅ Tên lớp tín chỉ: Đúng\n"
                message += "✅ Combo mã + lớp: Khớp"
                messagebox.showinfo("Kết quả kiểm tra", message)
                self.log_message("✅ Tất cả mã học phần và lớp đều hợp lệ!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi kiểm tra: {e}")
            self.log_message(f"❌ Lỗi kiểm tra: {e}")
    
    def check_schedule_only(self):
        """Chỉ kiểm tra trùng lịch học (không check mã học phần hay lớp)"""
        try:
            # Kiểm tra file Excel
            excel_file = "lophoc.xlsx"
            if not os.path.exists(excel_file):
                messagebox.showerror("Lỗi", f"Không tìm thấy file {excel_file}!")
                return
            
            # Đọc danh sách lớp từ Treeview
            saved_classes = []
            for child in self.course_tree.get_children():
                values = self.course_tree.item(child)['values']
                if len(values) >= 3:
                    saved_classes.append(values[2].strip())  # Tên lớp
            
            if not saved_classes:
                messagebox.showwarning("Cảnh báo", "Chưa có lớp nào để kiểm tra!")
                return
            
            # Đọc Excel
            self.log_message("📅 Đang kiểm tra trùng lịch học...")
            df = pd.read_excel(excel_file)
            
            # Gọi hàm kiểm tra trùng lịch
            self.check_schedule_conflicts(df, saved_classes)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi kiểm tra lịch: {e}")
            self.log_message(f"❌ Lỗi: {e}")
    
    def check_schedule_conflicts(self, df, saved_classes):
        """Kiểm tra trùng lịch học giữa các lớp đã chọn"""
        try:
            self.log_message("\n🔍 Đang kiểm tra trùng lịch học...")
            self.log_message(f"📋 Số lớp cần kiểm tra: {len(saved_classes)}")
            
            # Lọc các lớp đã lưu từ DataFrame
            class_schedules = []
            for class_name in saved_classes:
                class_name_clean = class_name.strip()
                self.log_message(f"  🔎 Đang tìm: {class_name_clean}")
                matching_rows = df[df['Tên_lớp_tín_chỉ'] == class_name_clean]
                
                if not matching_rows.empty:
                    schedule = matching_rows.iloc[0]['Lịch_học']
                    subject = matching_rows.iloc[0]['Tên_học_phần']
                    self.log_message(f"  ✅ Tìm thấy: {subject} - {class_name_clean}")
                    if pd.notna(schedule):
                        class_schedules.append({
                            'subject': subject,
                            'class': class_name_clean,
                            'schedule': str(schedule)
                        })
                        self.log_message(f"     📅 Lịch: {schedule}")
                    else:
                        self.log_message(f"  ⚠️ Lớp {class_name_clean} không có lịch học")
                else:
                    self.log_message(f"  ❌ Không tìm thấy: {class_name_clean}")
            
            # So sánh lịch học giữa các lớp
            self.log_message(f"\n🔄 So sánh {len(class_schedules)} lớp với nhau...")
            conflicts = []
            for i in range(len(class_schedules)):
                for j in range(i + 1, len(class_schedules)):
                    schedule1 = class_schedules[i]['schedule']
                    schedule2 = class_schedules[j]['schedule']
                    
                    self.log_message(f"  So sánh: {class_schedules[i]['class']} vs {class_schedules[j]['class']}")
                    
                    # So sánh lịch học (nếu giống nhau hoặc tương tự)
                    if schedule1 == schedule2:
                        self.log_message(f"    ⚠️ TRÙNG HOÀN TOÀN!")
                        conflicts.append({
                            'class1': class_schedules[i],
                            'class2': class_schedules[j],
                            'type': 'exact'
                        })
                    # Kiểm tra xem có overlap về thời gian không
                    elif self.check_time_overlap(schedule1, schedule2):
                        self.log_message(f"    ⚠️ TRÙNG THỜI GIAN!")
                        conflicts.append({
                            'class1': class_schedules[i],
                            'class2': class_schedules[j],
                            'type': 'overlap'
                        })
                    else:
                        self.log_message(f"    ✅ Không trùng")
            
            # Hiển thị kết quả
            self.log_message(f"\n📊 Kết quả: Tìm thấy {len(conflicts)} trường hợp trùng lịch")
            
            if conflicts:
                # Lưu conflicts để dùng cho suggest alternative
                self.last_conflicts = conflicts
                self.last_df = df
                
                message = "⚠️ PHÁT HIỆN TRÙNG LỊCH HỌC:\n\n"
                for idx, conflict in enumerate(conflicts, 1):
                    c1 = conflict['class1']
                    c2 = conflict['class2']
                    conflict_type = "TRÙNG HOÀN TOÀN" if conflict['type'] == 'exact' else "TRÙNG THỜI GIAN"
                    
                    message += f"#{idx} 🔴 {conflict_type}:\n"
                    message += f"   📚 Môn 1: {c1['subject']} - {c1['class']}\n"
                    message += f"   📅 Lịch: {c1['schedule']}\n\n"
                    message += f"   📚 Môn 2: {c2['subject']} - {c2['class']}\n"
                    message += f"   📅 Lịch: {c2['schedule']}\n"
                    message += "\n" + "="*50 + "\n\n"
                
                message += "💡 Nhấn nút 'Gợi ý lớp thay thế' để tìm lớp không trùng lịch!"
                
                self.log_message(f"⚠️ Hiển thị thông báo trùng lịch...")
                messagebox.showwarning("Trùng lịch học", message)
                self.log_message(f"⚠️ Phát hiện {len(conflicts)} trường hợp trùng lịch!")
            else:
                self.last_conflicts = None
                self.log_message("✅ Không có trùng lịch, hiển thị thông báo...")
                messagebox.showinfo("Kết quả", "✅ Không có lớp nào trùng lịch học!")
                self.log_message("✅ Không có trùng lịch học")
                
        except Exception as e:
            error_msg = f"❌ Lỗi kiểm tra lịch: {e}"
            self.log_message(error_msg)
            messagebox.showerror("Lỗi", error_msg)
            import traceback
            self.log_message(traceback.format_exc())
    
    def suggest_alternative_classes(self):
        """Gợi ý lớp thay thế cho các lớp bị trùng lịch"""
        try:
            # Kiểm tra có conflict nào không
            if not hasattr(self, 'last_conflicts') or not self.last_conflicts:
                messagebox.showinfo("Thông báo", "Vui lòng chạy 'Check trùng lịch' trước!")
                return
            
            df = self.last_df
            conflicts = self.last_conflicts
            
            self.log_message("\n💡 Đang tìm lớp thay thế...")
            
            # Lấy tất cả lớp hiện tại và lịch của chúng
            current_classes = []
            for child in self.course_tree.get_children():
                values = self.course_tree.item(child)['values']
                if len(values) >= 3:
                    class_name = values[2].strip()
                    current_classes.append(class_name)
            
            # Lấy tất cả lịch học hiện tại
            current_schedules = []
            for class_name in current_classes:
                matching_rows = df[df['Tên_lớp_tín_chỉ'] == class_name]
                if not matching_rows.empty:
                    schedule = matching_rows.iloc[0]['Lịch_học']
                    if pd.notna(schedule):
                        current_schedules.append(str(schedule))
            
            # Tìm lớp thay thế cho từng conflict
            suggestions = []
            
            for conflict in conflicts:
                c1 = conflict['class1']
                c2 = conflict['class2']
                
                # Ưu tiên sửa lớp thứ 2
                class_to_replace = c2['class']
                
                # Trích xuất mã môn học từ tên lớp
                course_code = class_to_replace.split('_')[0] if '_' in class_to_replace else class_to_replace
                
                self.log_message(f"\n🔍 Tìm lớp thay thế cho: {class_to_replace}")
                self.log_message(f"   Mã môn: {course_code}")
                
                # Tìm tất cả lớp cùng môn học
                same_course_classes = df[df['Mã_học_phần'] == course_code]
                
                if same_course_classes.empty:
                    self.log_message(f"   ❌ Không tìm thấy lớp nào cùng môn {course_code}")
                    continue
                
                # Tìm lớp không trùng lịch với tất cả lớp hiện tại
                alternatives = []
                for idx, row in same_course_classes.iterrows():
                    alt_class = row['Tên_lớp_tín_chỉ']
                    alt_schedule = str(row['Lịch_học']) if pd.notna(row['Lịch_học']) else None
                    
                    if alt_class == class_to_replace:
                        continue  # Bỏ qua lớp hiện tại
                    
                    if not alt_schedule:
                        continue
                    
                    # Kiểm tra xem lớp này có trùng với lớp nào đang có không
                    has_conflict = False
                    for existing_schedule in current_schedules:
                        if existing_schedule != c2['schedule']:  # Không so sánh với chính nó
                            if alt_schedule == existing_schedule or self.check_time_overlap(alt_schedule, existing_schedule):
                                has_conflict = True
                                break
                    
                    if not has_conflict:
                        alternatives.append({
                            'class': alt_class,
                            'schedule': alt_schedule,
                            'slots': row.get('Còn_trống', '?')
                        })
                        self.log_message(f"   ✅ Tìm thấy: {alt_class} - Lịch: {alt_schedule}")
                
                if alternatives:
                    suggestions.append({
                        'original': class_to_replace,
                        'original_schedule': c2['schedule'],
                        'alternatives': alternatives,
                        'conflict_with': c1['class']
                    })
                else:
                    self.log_message(f"   ⚠️ Không tìm thấy lớp thay thế phù hợp")
            
            # Hiển thị gợi ý
            if not suggestions:
                messagebox.showinfo("Kết quả", "❌ Không tìm thấy lớp thay thế phù hợp nào!")
                return
            
            # Tạo dialog để user chọn
            self.show_suggestion_dialog(suggestions)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tìm lớp thay thế: {e}")
            self.log_message(f"❌ Lỗi: {e}")
            import traceback
            self.log_message(traceback.format_exc())
    
    def show_suggestion_dialog(self, suggestions):
        """Hiển thị dialog cho user chọn lớp thay thế"""
        # Tạo window mới
        dialog = tk.Toplevel(self.root)
        dialog.title("💡 Gợi ý lớp thay thế")
        dialog.geometry("800x600")
        
        # Frame chính
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label title
        title_label = ttk.Label(main_frame, text="💡 GỢI Ý LỚP THAY THẾ", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Scrolled frame
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Dictionary để lưu user selections
        selections = {}
        
        # Hiển thị từng suggestion
        for idx, suggestion in enumerate(suggestions):
            # Frame cho mỗi suggestion
            sug_frame = ttk.LabelFrame(scrollable_frame, text=f"Trùng #{idx+1}", padding="10")
            sug_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Thông tin lớp hiện tại
            info_text = f"❌ Lớp bị trùng: {suggestion['original']}\n"
            info_text += f"📅 Lịch: {suggestion['original_schedule']}\n"
            info_text += f"🔴 Trùng với: {suggestion['conflict_with']}\n\n"
            info_text += f"✅ Có {len(suggestion['alternatives'])} lớp thay thế:\n"
            
            info_label = ttk.Label(sug_frame, text=info_text, font=('Arial', 9))
            info_label.pack(anchor=tk.W)
            
            # Radio buttons cho alternatives
            var = tk.StringVar(value="KEEP")  # Mặc định giữ nguyên
            selections[suggestion['original']] = var
            
            # Option: Giữ nguyên
            keep_radio = ttk.Radiobutton(sug_frame, text="🔒 Giữ nguyên (không thay đổi)", 
                                        variable=var, value="KEEP")
            keep_radio.pack(anchor=tk.W, padx=20)
            
            # Options: Các lớp thay thế
            for alt_idx, alt in enumerate(suggestion['alternatives'][:5]):  # Giới hạn 5 lớp
                text = f"✅ {alt['class']}\n"
                text += f"    📅 Lịch: {alt['schedule']}\n"
                text += f"    💺 Còn trống: {alt['slots']}"
                
                alt_radio = ttk.Radiobutton(sug_frame, text=text, 
                                           variable=var, value=alt['class'])
                alt_radio.pack(anchor=tk.W, padx=20, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def apply_changes():
            """Áp dụng thay đổi"""
            changes_made = False
            
            for original_class, var in selections.items():
                new_class = var.get()
                
                if new_class != "KEEP" and new_class != original_class:
                    # Tìm và thay thế trong Treeview
                    for child in self.course_tree.get_children():
                        values = list(self.course_tree.item(child)['values'])
                        if len(values) >= 3 and values[2].strip() == original_class:
                            # Cập nhật tên lớp
                            values[2] = new_class
                            
                            # Cập nhật mã môn nếu cần
                            new_course_code = new_class.split('_')[0] if '_' in new_class else new_class
                            values[1] = new_course_code
                            
                            self.course_tree.item(child, values=tuple(values))
                            self.log_message(f"✅ Đã thay: {original_class} → {new_class}")
                            changes_made = True
                            break
            
            if changes_made:
                messagebox.showinfo("Thành công", "✅ Đã cập nhật lớp thay thế!\n\n⚠️ Vui lòng LƯU CẤU HÌNH!")
                dialog.destroy()
            else:
                messagebox.showinfo("Thông báo", "Không có thay đổi nào được áp dụng.")
                dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        ok_btn = ttk.Button(btn_frame, text="✅ Áp dụng", command=apply_changes)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="❌ Hủy", command=cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def parse_schedule(self, schedule):
        """Trích xuất thông tin ngày và tiết học"""
        try:
            parts = schedule.split('\n')
            if len(parts) < 2:
                return None
            
            day_part = parts[1]  # "Thứ 6(T1-3)"
            
            # Trích xuất thứ trong tuần
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
            
            # Trích xuất tiết học (T1-3 nghĩa là tiết 1 đến 3)
            time_match = re.search(r'T(\d+)-(\d+)', day_part)
            if time_match:
                start_period = int(time_match.group(1))
                end_period = int(time_match.group(2))
                return {'day': day_of_week, 'start': start_period, 'end': end_period}
            
            return None
        except:
            return None
    
    def check_time_overlap(self, schedule1, schedule2):
        """Kiểm tra xem 2 lịch học có trùng thời gian không"""
        try:
            s1 = self.parse_schedule(schedule1)
            s2 = self.parse_schedule(schedule2)
            
            if not s1 or not s2:
                return False
            
            # Kiểm tra cùng ngày
            if s1['day'] != s2['day']:
                return False
            
            # Kiểm tra trùng tiết học
            # Overlap nếu: (start1 <= end2) và (end1 >= start2)
            overlap = (s1['start'] <= s2['end']) and (s1['end'] >= s2['start'])
            return overlap
            
        except Exception:
            return False
    
    def show_timetable(self):
        """Hiển thị thời khóa biểu dạng bảng"""
        try:
            # Kiểm tra file Excel
            excel_file = "lophoc.xlsx"
            if not os.path.exists(excel_file):
                messagebox.showerror("Lỗi", f"Không tìm thấy file {excel_file}!")
                return
            
            # Đọc danh sách lớp từ Treeview
            saved_classes = []
            for child in self.course_tree.get_children():
                values = self.course_tree.item(child)['values']
                if len(values) >= 3:
                    saved_classes.append({
                        'subject': values[1].strip(),
                        'class': values[2].strip()
                    })
            
            if not saved_classes:
                messagebox.showwarning("Cảnh báo", "Chưa có lớp nào để xem thời khóa biểu!")
                return
            
            # Đọc Excel
            df = pd.read_excel(excel_file)
            
            # Tạo cấu trúc thời khóa biểu
            timetable = {}  # {day: {period: [subject_info]}}
            
            for class_info in saved_classes:
                class_name = class_info['class']
                subject_name = class_info['subject']
                
                matching_rows = df[df['Tên_lớp_tín_chỉ'] == class_name]
                
                if not matching_rows.empty:
                    schedule = matching_rows.iloc[0]['Lịch_học']
                    
                    if pd.notna(schedule):
                        parsed = self.parse_schedule(str(schedule))
                        
                        if parsed:
                            day = parsed['day']
                            start = parsed['start']
                            end = parsed['end']
                            
                            # Thêm vào thời khóa biểu
                            if day not in timetable:
                                timetable[day] = {}
                            
                            for period in range(start, end + 1):
                                if period not in timetable[day]:
                                    timetable[day][period] = []
                                timetable[day][period].append({
                                    'subject': subject_name,
                                    'class': class_name
                                })
            
            # Hiển thị trong cửa sổ mới
            self.display_timetable_window(timetable)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tạo thời khóa biểu: {e}")
            self.log_message(f"❌ Lỗi: {e}")
    
    def display_timetable_window(self, timetable):
        """Hiển thị cửa sổ thời khóa biểu"""
        dialog = tk.Toplevel(self.root)
        dialog.title("📅 THỜI KHÓA BIỂU")
        dialog.geometry("1200x700")
        
        # Frame chính
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📅 THỜI KHÓA BIỂU", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Tạo frame với scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Tạo bảng thời khóa biểu
        # Header row (Thứ 2 - Thứ 7)
        days = [2, 3, 4, 5, 6, 7]
        day_names = {2: 'Thứ 2', 3: 'Thứ 3', 4: 'Thứ 4', 5: 'Thứ 5', 6: 'Thứ 6', 7: 'Thứ 7'}
        
        # Tiêu đề cột đầu tiên (Tiết)
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.grid(row=0, column=0, sticky='nsew')
        ttk.Label(header_frame, text="Tiết", font=('Arial', 11, 'bold'), 
                 relief='solid', borderwidth=1, anchor='center', width=8).pack(fill=tk.BOTH, expand=True)
        
        # Header các thứ
        for col_idx, day in enumerate(days, start=1):
            header_frame = ttk.Frame(scrollable_frame)
            header_frame.grid(row=0, column=col_idx, sticky='nsew')
            ttk.Label(header_frame, text=day_names[day], font=('Arial', 11, 'bold'),
                     relief='solid', borderwidth=1, anchor='center', width=18,
                     background='lightblue').pack(fill=tk.BOTH, expand=True)
        
        # Tạo 15 hàng (Tiết 1 - 15)
        for period in range(1, 16):
            # Cột đầu: Số tiết
            period_frame = ttk.Frame(scrollable_frame)
            period_frame.grid(row=period, column=0, sticky='nsew')
            ttk.Label(period_frame, text=f"Tiết {period}", font=('Arial', 10),
                     relief='solid', borderwidth=1, anchor='center', width=8).pack(fill=tk.BOTH, expand=True)
            
            # Các cột môn học
            for col_idx, day in enumerate(days, start=1):
                cell_frame = ttk.Frame(scrollable_frame)
                cell_frame.grid(row=period, column=col_idx, sticky='nsew')
                
                # Kiểm tra xem có môn học nào không
                cell_text = ""
                bg_color = "white"
                
                if day in timetable and period in timetable[day]:
                    subjects = timetable[day][period]
                    cell_text = "\n".join([f"{s['subject']}" for s in subjects])
                    bg_color = "lightgreen"
                
                cell_label = tk.Label(cell_frame, text=cell_text, font=('Arial', 9),
                                     relief='solid', borderwidth=1, anchor='center',
                                     width=18, height=3, background=bg_color, wraplength=150)
                cell_label.pack(fill=tk.BOTH, expand=True)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Nút đóng
        close_btn = ttk.Button(main_frame, text="❌ Đóng", command=dialog.destroy)
        close_btn.pack(pady=10)

def main():
    """Chạy Complete GUI"""
    try:
        # Đảm bảo thư mục làm việc là thư mục hiện tại của script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        root = tk.Tk()
        app = CompleteGUI(root)

        def on_closing():
            if app.process and app.process.poll() is None:
                if messagebox.askokcancel("Thoát", "Automation đang chạy. Dừng và thoát?"):
                    app.stop_automation()
                    root.destroy()
            else:
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
