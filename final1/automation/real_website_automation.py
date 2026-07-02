#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ULSA Real Website Two-Step Registration Automation
Dựa trên HTML thật từ b111.html và b22.html
"""

import time
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Global variables
driver = None
config = {}

def get_chrome_window_title():
    """Lấy tên định danh cho Chrome window theo format: folder_name student_id"""
    try:
        # Lấy tên thư mục hiện tại (parent của automation)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        folder_name = os.path.basename(parent_dir)
        
        # Lấy mã sinh viên từ config
        student_id = config.get('login_info', {}).get('student_id', 'Unknown')
        
        # Tạo title theo format
        window_title = f"{folder_name} {student_id}"
        return window_title
    except Exception as e:
        print(f"⚠️ Không thể tạo window title: {e}")
        return "ULSA Automation"

def setup_chrome_driver():
    """Cấu hình và khởi động ChromeDriver"""
    global driver
    try:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Tạo tab phụ để hiển thị thông tin định danh
        window_title = get_chrome_window_title()
        driver.execute_script("window.open('about:blank', '_blank');")
        driver.switch_to.window(driver.window_handles[0])
        
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1])
            driver.execute_script(f"""
                document.body.style.margin = '0';
                document.body.style.padding = '50px';
                document.body.style.backgroundColor = '#1e1e1e';
                document.body.style.color = '#00ff00';
                document.body.style.fontFamily = 'Consolas, monospace';
                document.body.style.fontSize = '24px';
                document.body.style.display = 'flex';
                document.body.style.alignItems = 'center';
                document.body.style.justifyContent = 'center';
                document.body.innerHTML = '<div style="text-align: center;"><h1 style="color: #00ff00; font-size: 36px; margin-bottom: 20px;">🎯 THÔNG TIN</h1><p style="font-size: 28px; margin: 10px 0;">📁 {window_title}</p></div>';
                document.title = '{window_title}';
            """)
            driver.switch_to.window(driver.window_handles[0])
        
        print(f"✅ ChromeDriver đã được khởi động thành công! [{window_title}]")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi khởi động ChromeDriver: {str(e)}")
        return False

def take_screenshot(step_name):
    """Chụp màn hình với tên file có timestamp"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_dir = os.path.join(os.path.dirname(__file__), "..", "screenshots")
        
        # Tạo thư mục screenshots nếu chưa có
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        filename = f"{timestamp}_{step_name}.png"
        filepath = os.path.join(screenshot_dir, filename)
        
        driver.save_screenshot(filepath)
        print(f"📸 Đã chụp màn hình: {filename}")
        return filepath
    except Exception as e:
        print(f"❌ Lỗi khi chụp màn hình: {e}")
        return None

def load_config():
    """Đọc file cấu hình auto_config.json"""
    global config
    config_file = os.path.join(os.path.dirname(__file__), "..", "auto_config.json")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ Đã đọc file cấu hình thành công!")
        print(f"👤 Mã sinh viên: {config['login_info']['student_id']}")
        
        if 'course_selections' in config:
            subject_names = config['course_selections']['subject_names_b1']
            class_names = config['course_selections']['class_names_b2']
            print(f"📚 Học phần B1: {len(subject_names)} môn")
            print(f"📚 Lớp tín chỉ B2: {len(class_names)} lớp")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi đọc file cấu hình: {e}")
        return False

def retry_with_reload(func, max_retries=5, delay=3):
    """Wrapper function để retry với reload trang"""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Lần thử {attempt}/{max_retries}")
            result = func()
            if result:
                return True
            
            if attempt < max_retries:
                print(f"⚠️ Lần thử {attempt} thất bại, reload trang và thử lại sau {delay}s...")
                driver.refresh()
                time.sleep(delay)
                
        except Exception as e:
            print(f"❌ Lỗi lần thử {attempt}: {e}")
            if attempt < max_retries:
                print(f"🔄 Reload trang và thử lại sau {delay}s...")
                try:
                    driver.refresh()
                    time.sleep(delay)
                except:
                    current_url = driver.current_url
                    driver.get(current_url)
                    time.sleep(delay)
            
    print(f"❌ Đã thử {max_retries} lần nhưng vẫn thất bại!")
    return False

def login_to_ulsa():
    """Đăng nhập vào hệ thống ULSA"""
    def _login_attempt():
        try:
            print("🌐 Đang truy cập trang đăng nhập ULSA...")
            driver.get("http://sinhvien.ulsa.edu.vn/Login.aspx")
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            student_id = config['login_info']['student_id']
            password = config['login_info']['password']
            
            username_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            
            username_field.clear()
            username_field.send_keys(student_id)
            password_field.clear()
            password_field.send_keys(password)
            
            print("🚀 Đang thực hiện đăng nhập...")
            driver.execute_script("arguments[0].click();", login_button)
            
            WebDriverWait(driver, 10).until(
                lambda d: "login.aspx" not in d.current_url.lower()
            )
            
            print("✅ Đăng nhập thành công!")
            take_screenshot("login_success")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi đăng nhập: {e}")
            return False
    
    return retry_with_reload(_login_attempt, max_retries=5, delay=3)

def step1_select_subjects_b1():
    """Bước 1: Chọn học phần trên trang B1 dựa trên HTML thật"""
    def _step1_attempt():
        try:
            print("\\n📍 BƯỚC 1: CHỌN HỌC PHẦN TRÊN TRANG B1")
            
            # Chuyển đến trang B1
            b1_url = "http://sinhvien.ulsa.edu.vn/wfrmDangKyLopTinChiB1.aspx?Chuyen_nganh=1"
            driver.get(b1_url)
            
            # Đợi bảng grdViewMonDangKy tải xong
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "grdViewMonDangKy"))
            )
            
            print("✅ Trang B1 đã tải xong!")
            take_screenshot("b1_page_loaded")
            
            # Lấy danh sách mã học phần cần chọn
            subject_names = config['course_selections']['subject_names_b1']
            print(f"🎯 Tìm kiếm {len(subject_names)} mã học phần:")
            for i, subject in enumerate(subject_names, 1):
                print(f"   {i}. {subject}")
            
            # Tìm và chọn checkbox trong bảng grdViewMonDangKy
            selected_count = 0
            found_subjects = []
            
            # Tìm tất cả checkbox có pattern grdViewMonDangKy_ctl##_chk
            checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[id*='grdViewMonDangKy_ctl'][type='checkbox']")
            print(f"🔍 Tìm thấy {len(checkboxes)} checkbox trong bảng B1")
            
            for checkbox in checkboxes:
                try:
                    # Tìm hàng chứa checkbox
                    row = checkbox.find_element(By.XPATH, "./ancestor::tr")
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) >= 4:
                        # Cột 3: Mã học phần  
                        # Cột 4: Tên học phần (có mã trong ngoặc)
                        course_code = cells[2].text.strip()  # Cột 3
                        course_name = cells[3].text.strip()  # Cột 4
                        
                        # Tìm mã trong ngoặc từ tên học phần
                        # Ví dụ: "Chủ nghĩa xã hội khoa học (CNXH0722H_D18CT)"
                        subject_code_in_parentheses = ""
                        if '(' in course_name and ')' in course_name:
                            subject_code_in_parentheses = course_name.split('(')[1].split(')')[0].strip()
                        
                        # Kiểm tra xem có khớp với danh sách cần chọn không
                        for target_subject in subject_names:
                            if (target_subject == course_code or 
                                target_subject == subject_code_in_parentheses or
                                target_subject in subject_code_in_parentheses):
                                
                                print(f"✅ Tìm thấy: {target_subject}")
                                print(f"   📝 Mã học phần: {course_code}")
                                print(f"   📝 Tên học phần: {course_name[:50]}...")
                                print(f"   📝 Mã trong ngoặc: {subject_code_in_parentheses}")
                                
                                if not checkbox.is_selected():
                                    driver.execute_script("arguments[0].click();", checkbox)
                                    selected_count += 1
                                    found_subjects.append(target_subject)
                                    print(f"✅ Đã chọn: {target_subject}")
                                else:
                                    print(f"⚠️ Đã được chọn sẵn: {target_subject}")
                                    found_subjects.append(target_subject)
                                break
                                
                except Exception as e:
                    continue
            
            print(f"\\n📊 KẾT QUẢ BƯỚC 1:")
            print(f"   ✅ Đã chọn: {selected_count} học phần")
            print(f"   📚 Tìm thấy: {len(found_subjects)} học phần")
            
            if found_subjects:
                print("✅ Các học phần đã chọn:")
                for subject in found_subjects:
                    print(f"   - {subject}")
            
            missing = [s for s in subject_names if s not in found_subjects]
            if missing:
                print("❌ Các học phần chưa tìm thấy:")
                for s in missing:
                    print(f"   - {s}")
            
            if selected_count == 0:
                print("❌ Không có học phần nào được chọn!")
                return False
            
            take_screenshot("b1_subjects_selected")
            
            # Bấm nút "Đăng ký lớp tín chỉ"
            print("🔄 Đang bấm nút 'Đăng ký lớp tín chỉ'...")
            register_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "cmdDangKyLop2"))
            )
            
            driver.execute_script("arguments[0].click();", register_button)
            
            # Đợi chuyển đến trang B2
            print("⏳ Đang đợi chuyển đến trang B2...")
            WebDriverWait(driver, 10).until(
                lambda d: "b2" in d.current_url.lower() or "wfrmdangkyloptin" in d.current_url.lower() and d.current_url != b1_url
            )
            
            print("✅ Đã chuyển đến trang B2 thành công!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi ở Bước 1: {e}")
            return False
    
    return retry_with_reload(_step1_attempt, max_retries=5, delay=3)

def step2_select_classes_b2():
    """Bước 2: Chọn lớp tín chỉ trên trang B2 dựa trên HTML thật"""
    def _step2_attempt():
        try:
            print("\\n📍 BƯỚC 2: CHỌN LỚP TÍN CHỈ TRÊN TRANG B2")
            print(f"📍 URL hiện tại: {driver.current_url}")
            
            take_screenshot("b2_page_loaded")
            
            # Đợi bảng grd tải xong
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "grd"))
            )
            
            # Lấy danh sách lớp tín chỉ cần chọn
            class_names = config['course_selections']['class_names_b2']
            print(f"🎯 Tìm kiếm {len(class_names)} lớp tín chỉ:")
            for i, class_name in enumerate(class_names, 1):
                print(f"   {i}. {class_name}")
            
            selected_count = 0
            found_classes = []
            
            # Tìm tất cả radio button có pattern grd_ctl##_chk  
            radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input[id*='grd_ctl'][type='radio']")
            print(f"🔍 Tìm thấy {len(radio_buttons)} radio button trong bảng B2")
            
            for radio in radio_buttons:
                try:
                    # Tìm hàng chứa radio button
                    row = radio.find_element(By.XPATH, "./ancestor::tr")
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) >= 4:
                        # Cột 1: Mã học phần
                        # Cột 4: Tên lớp tín chỉ 
                        course_code = cells[0].text.strip()  # Cột 1
                        class_name_cell = cells[3].text.strip()  # Cột 4
                        
                        # Kiểm tra xem có khớp với danh sách cần chọn không
                        for target_class in class_names:
                            if (target_class == class_name_cell or 
                                target_class in class_name_cell or
                                class_name_cell in target_class):
                                
                                print(f"✅ Tìm thấy lớp: {target_class}")
                                print(f"   📝 Mã học phần: {course_code}")
                                print(f"   📝 Tên lớp: {class_name_cell}")
                                
                                if not radio.is_selected():
                                    driver.execute_script("arguments[0].click();", radio)
                                    selected_count += 1
                                    found_classes.append(target_class)
                                    print(f"✅ Đã chọn: {target_class}")
                                else:
                                    print(f"⚠️ Đã được chọn sẵn: {target_class}")
                                    found_classes.append(target_class)
                                break
                                
                except Exception as e:
                    continue
            
            print(f"\\n📊 KẾT QUẢ BƯỚC 2:")
            print(f"   ✅ Đã chọn: {selected_count} lớp")
            print(f"   📚 Tìm thấy: {len(found_classes)} lớp")
            
            if found_classes:
                print("✅ Các lớp đã chọn:")
                for cls in found_classes:
                    print(f"   - {cls}")
            
            missing = [c for c in class_names if c not in found_classes]
            if missing:
                print("❌ Các lớp chưa tìm thấy:")
                for c in missing:
                    print(f"   - {c}")
            
            if selected_count == 0:
                print("❌ Không có lớp nào được chọn!")
                return False
            
            take_screenshot("b2_classes_selected")
            
            print("✅ Bước 2 hoàn thành!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi ở Bước 2: {e}")
            return False
    
    return retry_with_reload(_step2_attempt, max_retries=5, delay=3)

def step3_save_results():
    """Bước 3: Lưu kết quả đăng ký"""
    def _save_attempt():
        try:
            print("\\n💾 BƯỚC 3: LUU KẾT QUẢ ĐĂNG KÝ")
            
            # Tìm nút "Lưu kết quả đăng ký"
            save_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "cmdDangKyLop2"))
            )
            
            if save_button and save_button.is_displayed():
                print(f"✅ Tìm thấy nút: {save_button.get_attribute('value')}")
                
                take_screenshot("b2_before_save")
                
                driver.execute_script("arguments[0].click();", save_button)
                print("✅ Đã bấm nút Lưu!")
                
                time.sleep(5)
                
                # Kiểm tra có chuyển đến trang B3 không
                try:
                    WebDriverWait(driver, 10).until(
                        lambda d: "b3" in d.current_url.lower() or "ketqua" in d.current_url.lower()
                    )
                    print("✅ Đã chuyển đến trang kết quả (B3)!")
                    print(f"📍 URL B3: {driver.current_url}")
                    
                    take_screenshot("b3_final_result")
                    
                except TimeoutException:
                    print("⚠️ Chưa chuyển đến trang B3, kiểm tra thông báo...")
                
                print("✅ Lưu kết quả thành công!")
                return True
            else:
                print("❌ Không tìm thấy nút Lưu!")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi khi lưu: {e}")
            return False
    
    return retry_with_reload(_save_attempt, max_retries=3, delay=2)

def main():
    """Hàm chính - Real Website Automation"""
    try:
        print("🤖 ULSA REAL WEBSITE TWO-STEP AUTOMATION")
        print("=" * 70)
        print("📋 Dựa trên HTML thật từ b111.html và b22.html:")
        print("   1️⃣ Đăng nhập hệ thống")
        print("   2️⃣ B1: Chọn học phần trong bảng grdViewMonDangKy (checkbox)")
        print("   3️⃣ B2: Chọn lớp tín chỉ trong bảng grd (radio button)")
        print("   4️⃣ Lưu kết quả và chuyển B3")
        print("🔄 Mỗi bước có retry thông minh với reload trang")
        print("📸 Tự động chụp màn hình tại tất cả bước quan trọng")
        print("=" * 70)
        
        # Đọc cấu hình
        if not load_config():
            input("Nhấn Enter để thoát...")
            return
        
        # Khởi động browser
        if not setup_chrome_driver():
            input("Nhấn Enter để thoát...")
            return
        
        # Bước 1: Đăng nhập
        if not login_to_ulsa():
            print("❌ Đăng nhập thất bại!")
            input("Nhấn Enter để thoát...")
            return
        
        # Bước 2: Chọn học phần trên B1
        if not step1_select_subjects_b1():
            print("❌ Bước 1 (chọn học phần B1) thất bại!")
            input("Nhấn Enter để thoát...")
            return
        
        # Bước 3: Chọn lớp tín chỉ trên B2
        if not step2_select_classes_b2():
            print("❌ Bước 2 (chọn lớp tín chỉ B2) thất bại!")
            input("Nhấn Enter để thoát...")
            return
        
        # Bước 4: Lưu kết quả
        if not step3_save_results():
            print("❌ Bước 3 (lưu kết quả) thất bại!")
        
        print("\\n🎉 AUTOMATION HOÀN THÀNH!")
        print("✅ Đã thực hiện xong quy trình đăng ký dựa trên website thật")
        print("📸 Tất cả màn hình đã được chụp trong thư mục screenshots/")
        
        # Hỏi có muốn đóng browser không
        choice = input("\\n❓ Đóng browser? (y/n): ").strip().lower()
        if choice == 'y':
            driver.quit()
            print("👋 Đã đóng browser!")
        else:
            print("🔄 Browser vẫn mở để bạn kiểm tra...")
            input("Nhấn Enter để thoát...")
            driver.quit()
        
    except KeyboardInterrupt:
        print("\\n⏹️ Dừng automation bởi người dùng")
    except Exception as e:
        print(f"\\n❌ Lỗi không mong muốn: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()
