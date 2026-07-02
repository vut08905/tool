#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULSA Schedule Crawler - Enhanced Python Version
Version mạnh mẽ nhất, không cần Node.js
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# ANSI Color codes for colored output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def colored_print(text, color=Colors.WHITE):
    """Print colored text"""
    print(f"{color}{text}{Colors.END}")

class EnhancedULSACrawler:
    def __init__(self, headless=False, implicit_wait=10):
        self.driver = None
        self.data = []
        self.headless = headless
        self.implicit_wait = implicit_wait
        self.setup_driver()
    
    def setup_driver(self):
        """Thiết lập Chrome driver với nhiều options"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Thêm các options để tăng tính ổn định
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage') 
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-logging')
        options.add_argument('--silent')
        options.add_experimental_option("detach", not self.headless)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent để tránh bị detect
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(self.implicit_wait)
            colored_print("✅ Đã khởi tạo Chrome driver thành công", Colors.GREEN)
        except Exception as e:
            colored_print(f"❌ Lỗi khởi tạo driver: {e}", Colors.RED)
            colored_print("💡 Hãy đảm bảo Chrome và ChromeDriver đã được cài đặt", Colors.YELLOW)
            sys.exit(1)
    
    def login_and_navigate(self):
        """Mở trang và hướng dẫn người dùng"""
        url = "http://sinhvien.ulsa.edu.vn/TraCuuLichHocSinhVien.aspx"
        
        colored_print("🔗 Đang mở trang ULSA...", Colors.BLUE)
        self.driver.get(url)
        self.driver.maximize_window()
        
        colored_print("\n" + "="*60, Colors.CYAN)
        colored_print("📋 HƯỚNG DẪN SỬ DỤNG", Colors.CYAN + Colors.BOLD)
        colored_print("="*60, Colors.CYAN)
        colored_print("1. 🔐 Đăng nhập vào hệ thống ULSA", Colors.WHITE)
        colored_print("2. 📅 Chọn học kỳ cần crawl dữ liệu", Colors.WHITE)  
        colored_print("3. 🔍 Nhấn nút 'Tra cứu' để hiển thị bảng", Colors.WHITE)
        colored_print("4. ⏰ Đợi bảng lịch học hiển thị hoàn toàn", Colors.WHITE)
        colored_print("5. ✅ Quay lại terminal này và nhấn Enter", Colors.WHITE)
        colored_print("="*60, Colors.CYAN)
        colored_print("⚠️  LƯU Ý: ĐỪNG ĐÓNG BROWSER KHI TOOL ĐANG CHẠY!", Colors.RED + Colors.BOLD)
        
        input(f"\n{Colors.YELLOW}👉 Sau khi hoàn thành các bước trên, nhấn Enter để tiếp tục...{Colors.END}")
        return True
    
    def detect_semester_dropdown(self):
        """Tự động phát hiện và xử lý dropdown học kỳ"""
        try:
            colored_print("🔍 Đang tìm dropdown học kỳ...", Colors.BLUE)
            
            # Danh sách các ID có thể có của dropdown
            dropdown_ids = ["ddlKyDangKy", "DropDownList1", "ddlHocKy", "ddlKy"]
            
            dropdown = None
            for dropdown_id in dropdown_ids:
                try:
                    dropdown = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, dropdown_id))
                    )
                    colored_print(f"✅ Tìm thấy dropdown: {dropdown_id}", Colors.GREEN)
                    break
                except TimeoutException:
                    continue
            
            if dropdown:
                select = Select(dropdown)
                options = [opt.text.strip() for opt in select.options if opt.text.strip()]
                
                if len(options) > 1:
                    colored_print("\n📋 Các học kỳ có sẵn:", Colors.YELLOW)
                    for i, option in enumerate(options, 1):
                        colored_print(f"   {i}. {option}", Colors.WHITE)
                    
                    while True:
                        choice = input(f"\n{Colors.CYAN}👉 Nhập số thứ tự học kỳ (Enter để bỏ qua): {Colors.END}")
                        
                        if not choice:  # Enter để bỏ qua
                            break
                        
                        try:
                            choice_num = int(choice)
                            if 1 <= choice_num <= len(options):
                                select.select_by_visible_text(options[choice_num - 1])
                                colored_print(f"✅ Đã chọn: {options[choice_num - 1]}", Colors.GREEN)
                                time.sleep(2)
                                break
                            else:
                                colored_print("❌ Số không hợp lệ, vui lòng thử lại", Colors.RED)
                        except ValueError:
                            colored_print("❌ Vui lòng nhập số hợp lệ", Colors.RED)
                
                return True
            else:
                colored_print("⚠️ Không tìm thấy dropdown học kỳ", Colors.YELLOW)
                return False
                
        except Exception as e:
            colored_print(f"⚠️ Lỗi xử lý dropdown: {e}", Colors.YELLOW)
            return False
    
    def smart_table_detection(self):
        """Phát hiện bảng thông minh với nhiều phương pháp"""
        colored_print("🔍 Đang tìm bảng lịch học...", Colors.BLUE)
        
        # Danh sách các selector theo độ ưu tiên (dựa trên dữ liệu thực ULSA)
        table_selectors = [
            ("#grd", "ID: grd (Bảng chính ULSA)"),  # Ưu tiên cao nhất
            (".GridViewStyle", "Class: GridViewStyle"),
            ("#gvDSLopMo", "ID: gvDSLopMo"),
            ("#GridView1", "ID: GridView1"),
            ("#DataGrid1", "ID: DataGrid1"),
            ("table[id*='gv']", "Table với ID chứa 'gv'"),
            ("table[id*='Grid']", "Table với ID chứa 'Grid'"),
            ("table", "Bất kỳ table nào")
        ]
        
        for selector, description in table_selectors:
            try:
                colored_print(f"   🔍 Thử: {description}", Colors.CYAN)
                
                table = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                # Kiểm tra xem table có đúng cấu trúc ULSA không
                rows = table.find_elements(By.TAG_NAME, "tr")
                if len(rows) > 1:  # Có ít nhất header + 1 row data
                    # Kiểm tra header có đúng cấu trúc ULSA không
                    header_row = rows[0]
                    header_cells = header_row.find_elements(By.TAG_NAME, "th")
                    if not header_cells:
                        header_cells = header_row.find_elements(By.TAG_NAME, "td")
                    
                    if len(header_cells) >= 9:  # ULSA có 9 cột
                        # Kiểm tra một số header key của ULSA
                        header_texts = [cell.text.strip().lower() for cell in header_cells]
                        ulsa_indicators = ["mã học phần", "tên học phần", "số tín chỉ", "lịch học"]
                        
                        if any(indicator in " ".join(header_texts) for indicator in ulsa_indicators):
                            colored_print(f"✅ Tìm thấy bảng ULSA chính thức: {description}", Colors.GREEN)
                            colored_print(f"📊 Số dòng: {len(rows)}, Số cột: {len(header_cells)}", Colors.WHITE)
                            return selector
                    
                    colored_print(f"✅ Tìm thấy bảng: {description}", Colors.GREEN)
                    colored_print(f"📊 Số dòng: {len(rows)}", Colors.WHITE)
                    return selector
                    
            except (TimeoutException, NoSuchElementException):
                continue
        
        # Nếu không tìm thấy, thử tìm bảng có nhiều dòng nhất
        try:
            all_tables = self.driver.find_elements(By.TAG_NAME, "table")
            if all_tables:
                best_table = max(all_tables, key=lambda t: len(t.find_elements(By.TAG_NAME, "tr")))
                rows = best_table.find_elements(By.TAG_NAME, "tr")
                if len(rows) > 1:
                    colored_print(f"✅ Tìm thấy bảng tốt nhất với {len(rows)} dòng", Colors.GREEN)
                    return "table"
        except:
            pass
        
        colored_print("❌ Không tìm thấy bảng lịch học phù hợp", Colors.RED)
        colored_print("💡 Kiểm tra:", Colors.YELLOW)
        colored_print("   - Đã đăng nhập thành công chưa?", Colors.WHITE)
        colored_print("   - Đã chọn học kỳ chưa?", Colors.WHITE)  
        colored_print("   - Đã nhấn 'Tra cứu' chưa?", Colors.WHITE)
        colored_print("   - Bảng đã hiển thị trên trang chưa?", Colors.WHITE)
        
        return None
    
    def extract_data_smart(self, table_selector):
        """Trích xuất dữ liệu thông minh với auto-detect columns"""
        try:
            colored_print("📊 Đang phân tích cấu trúc bảng...", Colors.BLUE)
            
            rows = self.driver.find_elements(By.CSS_SELECTOR, f"{table_selector} tr")
            
            if len(rows) < 2:
                colored_print("❌ Bảng không có dữ liệu", Colors.RED)
                return 0
            
            # Phân tích header
            header_row = rows[0]
            headers = []
            header_cells = header_row.find_elements(By.TAG_NAME, "th")
            if not header_cells:
                header_cells = header_row.find_elements(By.TAG_NAME, "td")
            
            for cell in header_cells:
                headers.append(cell.text.strip())
            
            colored_print(f"📋 Headers phát hiện: {headers}", Colors.CYAN)
            
            # Mapping columns tự động
            column_map = self.auto_map_columns(headers)
            colored_print(f"🗺️ Column mapping: {column_map}", Colors.CYAN)
            
            # Trích xuất dữ liệu
            extracted_count = 0
            for i, row in enumerate(rows[1:], 1):
                cells = row.find_elements(By.TAG_NAME, "td")
                
                # Bỏ qua dòng pagination
                row_text = row.text.strip()
                if "Trang sau" in row_text or "Next" in row_text:
                    continue
                
                if len(cells) >= len(headers) * 0.7:  # Có ít nhất 70% số cột
                    row_data = {
                        "STT": extracted_count + 1,
                        "Ngày crawl": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Map dữ liệu theo column mapping
                    for j, cell in enumerate(cells):
                        if j < len(headers):
                            mapped_name = column_map.get(j, f"Cột_{j+1}")
                            cell_text = cell.text.strip()
                            
                            # Xử lý dữ liệu trống (&nbsp;)
                            if cell_text == "" or cell_text == "\u00a0" or cell_text == "&nbsp;":
                                if mapped_name in ["Giáo viên", "Phòng học"]:
                                    cell_text = "Chưa có thông tin"
                                else:
                                    cell_text = ""
                            
                            # Xử lý multiple lines (Ca học, Lịch học)
                            if mapped_name in ["Ca học", "Lịch học"]:
                                cell_text = cell_text.replace('\n', ' | ')
                            
                            row_data[mapped_name] = cell_text
                    
                    self.data.append(row_data)
                    extracted_count += 1
                    
                    if extracted_count % 10 == 0:
                        colored_print(f"   📝 Đã xử lý {extracted_count} môn học...", Colors.WHITE)
                        # Hiển thị môn mới nhất
                        if "Mã học phần" in row_data and "Tên học phần" in row_data:
                            ma = row_data["Mã học phần"]
                            ten = row_data["Tên học phần"][:30] + ("..." if len(row_data["Tên học phần"]) > 30 else "")
                            colored_print(f"   📌 Mới nhất: {ma} - {ten}", Colors.CYAN)
            
            colored_print(f"✅ Đã trích xuất {extracted_count} môn học", Colors.GREEN)
            return extracted_count
            
        except Exception as e:
            colored_print(f"❌ Lỗi trích xuất dữ liệu: {e}", Colors.RED)
            return 0
    
    def auto_map_columns(self, headers):
        """Tự động map columns dựa vào header text - Tối ưu cho ULSA"""
        column_map = {}
        
        # Mapping chính xác cho ULSA (9 cột chuẩn)
        ulsa_standard_mapping = {
            0: "Mã học phần",
            1: "Tên học phần", 
            2: "Số tín chỉ",
            3: "Tên lớp tín chỉ",
            4: "Ca học",
            5: "Lịch học",
            6: "Giáo viên",
            7: "Phòng học",
            8: "Còn trống"
        }
        
        # Nếu có đúng 9 cột và header khớp với ULSA
        if len(headers) == 9:
            ulsa_headers = ["mã học phần", "tên học phần", "số tín chỉ", "tên lớp tín chỉ", 
                           "ca học", "lịch học", "giáo viên", "phòng học", "còn trống"]
            
            headers_lower = [h.lower().strip() for h in headers]
            
            # Kiểm tra xem có khớp với cấu trúc ULSA không
            matches = sum(1 for i, h in enumerate(headers_lower) 
                         if i < len(ulsa_headers) and ulsa_headers[i] in h)
            
            if matches >= 6:  # Nếu khớp ít nhất 6/9 cột
                colored_print("✅ Phát hiện cấu trúc bảng ULSA chuẩn!", Colors.GREEN)
                return ulsa_standard_mapping
        
        # Fallback: Auto-mapping thông thường
        mappings = {
            "Mã học phần": ["mã", "code", "hp", "hocphan"],
            "Tên học phần": ["tên", "name", "môn", "subject"],
            "Số tín chỉ": ["tín", "credit", "tc", "số"],
            "Tên lớp tín chỉ": ["lớp", "class", "nhóm", "group", "tín chỉ"],
            "Ca học": ["ca", "shift", "buổi"],
            "Lịch học": ["lịch", "schedule", "thời gian", "time"],
            "Giáo viên": ["giảng", "teacher", "gv", "lecturer", "viên"],
            "Phòng học": ["phòng", "room", "địa điểm"],
            "Còn trống": ["trống", "available", "slot", "còn"],
            "Ghi chú": ["ghi chú", "note", "remark"]
        }
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            mapped = False
            
            for standard_name, keywords in mappings.items():
                if any(keyword in header_lower for keyword in keywords):
                    column_map[i] = standard_name
                    mapped = True
                    break
            
            if not mapped:
                column_map[i] = header if header else f"Cột_{i+1}"
        
        return column_map
    
    def handle_pagination_smart(self, table_selector):
        """Xử lý phân trang thông minh"""
        page_count = 1
        max_pages = 100  # Giới hạn an toàn
        
        while page_count <= max_pages:
            colored_print(f"\n📄 Đang xử lý trang {page_count}...", Colors.PURPLE)
            
            # Extract data from current page
            current_count = len(self.data)
            new_records = self.extract_data_smart(table_selector)
            
            if new_records == 0:
                colored_print("⚠️ Không có dữ liệu mới", Colors.YELLOW)
                break
            
            # Tìm nút next với nhiều cách
            next_found = False
            
            # Cách 1: Tìm theo href pattern (ưu tiên cho ULSA)
            next_selectors = [
                "a[href*='Page$Next']",  # ULSA specific
                "a[href*='__doPostBack'][href*='grd'][href*='Page']",  # ULSA table grd
                "a[href*='__doPostBack'][href*='Page']",
                "a[href*='Next']"
            ]
            
            for selector in next_selectors:
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_btn.is_displayed() and next_btn.is_enabled():
                        colored_print(f"👆 Tìm thấy nút Next: {selector}", Colors.BLUE)
                        href = next_btn.get_attribute("href")
                        
                        if "javascript:" in href:
                            # Xử lý ULSA postback
                            script = href.replace("javascript:", "")
                            colored_print(f"🔄 Executing: {script}", Colors.CYAN)
                            self.driver.execute_script(script)
                        else:
                            next_btn.click()
                        
                        # Đợi trang load và kiểm tra
                        time.sleep(3)
                        try:
                            WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, table_selector))
                            )
                        except:
                            pass
                        
                        next_found = True
                        break
                except:
                    continue
            
            # Cách 2: Tìm theo text
            if not next_found:
                next_texts = ["Trang sau", "Next", ">", ">>"]
                for text in next_texts:
                    try:
                        next_btn = self.driver.find_element(By.XPATH, f"//a[contains(text(), '{text}')]")
                        if next_btn.is_displayed() and next_btn.is_enabled():
                            colored_print(f"👆 Tìm thấy nút '{text}' (XPath)", Colors.BLUE)
                            next_btn.click()
                            next_found = True
                            break
                    except:
                        continue
            
            if not next_found:
                colored_print("✅ Không tìm thấy nút chuyển trang - Đã crawl hết", Colors.GREEN)
                break
            
            # Chờ trang load
            time.sleep(3)
            page_count += 1
            
            # Progress update
            colored_print(f"📈 Tổng đã crawl: {len(self.data)} môn học", Colors.WHITE)
        
        total_pages = page_count if next_found else page_count
        colored_print(f"\n📊 TỔNG KẾT: {total_pages} trang, {len(self.data)} môn học", Colors.GREEN + Colors.BOLD)
    
    def save_to_excel_enhanced(self, filename=None):
        """Lưu Excel với formatting đẹp"""
        if not self.data:
            colored_print("❌ Không có dữ liệu để lưu", Colors.RED)
            return False
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lich_hoc_ulsa_enhanced_{timestamp}.xlsx"
        
        try:
            # Tạo DataFrame
            df = pd.DataFrame(self.data)
            
            # Sắp xếp lại columns nếu có (ưu tiên ULSA structure)
            preferred_order = ["STT", "Mã học phần", "Tên học phần", "Số tín chỉ", 
                             "Tên lớp tín chỉ", "Ca học", "Lịch học", "Giáo viên", 
                             "Phòng học", "Còn trống", "Ghi chú", "Ngày crawl"]
            
            existing_cols = [col for col in preferred_order if col in df.columns]
            other_cols = [col for col in df.columns if col not in existing_cols]
            final_cols = existing_cols + other_cols
            
            df = df[final_cols]
            
            # Lưu với formatting
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Lịch học', index=False)
                
                # Formatting
                worksheet = writer.sheets['Lịch học']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            colored_print(f"✅ Đã lưu {len(self.data)} môn học vào: {filename}", Colors.GREEN)
            colored_print(f"📍 Vị trí: {os.path.abspath(filename)}", Colors.CYAN)
            
            # Hiển thị summary
            self.show_summary()
            
            return True
            
        except Exception as e:
            colored_print(f"❌ Lỗi lưu Excel: {e}", Colors.RED)
            return False
    
    def save_to_json_enhanced(self, filename=None):
        """Lưu JSON với metadata"""
        if not self.data:
            return False
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lich_hoc_ulsa_enhanced_{timestamp}.json"
        
        try:
            output_data = {
                "metadata": {
                    "crawl_time": datetime.now().isoformat(),
                    "total_records": len(self.data),
                    "source": "http://sinhvien.ulsa.edu.vn/TraCuuLichHocSinhVien.aspx",
                    "tool": "Enhanced ULSA Crawler v2.0"
                },
                "data": self.data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            colored_print(f"✅ Đã lưu JSON: {filename}", Colors.GREEN)
            return True
            
        except Exception as e:
            colored_print(f"❌ Lỗi lưu JSON: {e}", Colors.RED)
            return False
    
    def show_summary(self):
        """Hiển thị tóm tắt kết quả"""
        if not self.data:
            return
        
        colored_print("\n" + "="*60, Colors.CYAN)
        colored_print("📋 TÓM TẮT KẾT QUẢ CRAWL", Colors.CYAN + Colors.BOLD)
        colored_print("="*60, Colors.CYAN)
        
        # Thống kê cơ bản
        total = len(self.data)
        colored_print(f"📊 Tổng số môn học: {total}", Colors.WHITE)
        
        # Thống kê theo tín chỉ
        if "Số tín chỉ" in self.data[0]:
            try:
                credits = [int(row.get("Số tín chỉ", 0)) for row in self.data if row.get("Số tín chỉ", "").isdigit()]
                if credits:
                    total_credits = sum(credits)
                    colored_print(f"🎯 Tổng tín chỉ: {total_credits}", Colors.WHITE)
            except:
                pass
        
        # Preview 5 môn đầu
        colored_print("\n📋 Preview 5 môn học đầu tiên:", Colors.YELLOW)
        for i in range(min(5, len(self.data))):
            ma = self.data[i].get("Mã học phần", "N/A")
            ten = self.data[i].get("Tên học phần", "N/A")
            colored_print(f"   {i+1}. {ma} - {ten}", Colors.WHITE)
        
        if len(self.data) > 5:
            colored_print(f"   ... và {len(self.data) - 5} môn khác", Colors.GRAY)
        
        colored_print("="*60, Colors.CYAN)
    
    def run_enhanced(self):
        """Chạy crawler với enhanced features"""
        try:
            colored_print("🚀 ENHANCED ULSA SCHEDULE CRAWLER", Colors.BLUE + Colors.BOLD)
            colored_print("Phiên bản nâng cao - Chỉ cần Python!", Colors.CYAN)
            
            # Bước 1: Mở trang và hướng dẫn
            self.login_and_navigate()
            
            # Bước 2: Xử lý dropdown học kỳ  
            self.detect_semester_dropdown()
            
            # Bước 3: Phát hiện bảng thông minh
            table_selector = self.smart_table_detection()
            if not table_selector:
                return False
            
            # Bước 4: Crawl với pagination
            self.handle_pagination_smart(table_selector)
            
            if not self.data:
                colored_print("❌ Không có dữ liệu được crawl", Colors.RED)
                return False
            
            # Bước 5: Lưu kết quả
            colored_print("\n💾 Đang lưu kết quả...", Colors.BLUE)
            
            excel_saved = self.save_to_excel_enhanced()
            json_saved = self.save_to_json_enhanced()
            
            if excel_saved:
                colored_print("\n🎉 CRAWL HOÀN THÀNH THÀNH CÔNG!", Colors.GREEN + Colors.BOLD)
                return True
            else:
                return False
            
        except KeyboardInterrupt:
            colored_print("\n⚠️ Người dùng dừng crawl", Colors.YELLOW)
            return False
        except Exception as e:
            colored_print(f"\n❌ Lỗi không mong muốn: {e}", Colors.RED)
            return False
        finally:
            if self.driver:
                input(f"\n{Colors.YELLOW}👉 Nhấn Enter để đóng browser...{Colors.END}")
                self.driver.quit()

def main():
    """Enhanced main function"""
    print("\n" + "="*70)
    colored_print("🎓 ENHANCED ULSA SCHEDULE CRAWLER", Colors.BLUE + Colors.BOLD)
    colored_print("Phiên bản Python mạnh mẽ - Không cần Node.js!", Colors.CYAN)
    print("="*70)
    
    # Tùy chọn
    colored_print("\n⚙️ Cấu hình:", Colors.YELLOW)
    
    headless_choice = input(f"{Colors.WHITE}Chạy ẩn browser? (y/N): {Colors.END}").lower()
    headless = headless_choice in ['y', 'yes', '1']
    
    if headless:
        colored_print("🔇 Sẽ chạy ở chế độ headless", Colors.CYAN)
    else:
        colored_print("🖥️ Sẽ hiển thị browser", Colors.CYAN)
    
    # Khởi tạo và chạy
    crawler = EnhancedULSACrawler(headless=headless)
    success = crawler.run_enhanced()
    
    # Kết quả
    if success:
        colored_print("\n✅ THÀNH CÔNG! Kiểm tra file Excel đã được tạo.", Colors.GREEN + Colors.BOLD)
    else:
        colored_print("\n❌ THẤT BẠI! Kiểm tra lại các bước.", Colors.RED + Colors.BOLD)
    
    input(f"\n{Colors.CYAN}Nhấn Enter để thoát...{Colors.END}")

if __name__ == "__main__":
    main()
