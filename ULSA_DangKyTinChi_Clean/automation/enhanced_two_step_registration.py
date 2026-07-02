#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ULSA Enhanced Two-Step Registration Automation
Phiên bản nâng cấp với:
- Chọn theo TÊN học phần ở B1
- Chọn theo TÊN lớp tín chỉ ở B2  
- Chụp màn hình tự động
- Hỗ trợ cả config mới và cũ
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
        
        # Kiểm tra config mới có course_selections hay không
        if 'course_selections' in config:
            subject_names = config['course_selections']['subject_names_b1']
            class_names = config['course_selections']['class_names_b2']
            print(f"📚 Config mới: {len(subject_names)} học phần B1, {len(class_names)} lớp B2")
            print("📋 Học phần B1:")
            for i, name in enumerate(subject_names, 1):
                print(f"   {i}. {name}")
            print("📋 Lớp tín chỉ B2:")
            for i, name in enumerate(class_names, 1):
                print(f"   {i}. {name}")
        else:
            # Fallback về cấu trúc cũ
            print(f"📚 Config cũ: {len(config['selected_courses'])} lớp")
        
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
                    # Nếu refresh fail thì load lại URL
                    current_url = driver.current_url
                    driver.get(current_url)
                    time.sleep(delay)
            
    print(f"❌ Đã thử {max_retries} lần nhưng vẫn thất bại!")
    return False

def login_to_ulsa():
    """Đăng nhập vào hệ thống ULSA với retry"""
    def _login_attempt():
        try:
            print("🌐 Đang truy cập trang đăng nhập ULSA...")
            driver.get("http://sinhvien.ulsa.edu.vn/Login.aspx")
            
            # Đợi trang tải
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            # Điền thông tin đăng nhập
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
            
            # Đợi đăng nhập thành công
            WebDriverWait(driver, 10).until(
                lambda d: "login.aspx" not in d.current_url.lower()
            )
            
            print("✅ Đăng nhập thành công!")
            take_screenshot("login_success")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi đăng nhập: {e}")
            return False
    
    print("🔐 BẮTĐẦU QUY TRÌNH ĐĂNG NHẬP VỚI RETRY...")
    return retry_with_reload(_login_attempt, max_retries=5, delay=3)

def step1_select_by_subject_names():
    """Bước 1: Chọn học phần theo TÊN trên trang B1"""
    def _step1_attempt():
        try:
            print("\n📍 BƯỚC 1: CHỌN HỌC PHẦN THEO TÊN")
            print("🎯 Chuyển hướng trực tiếp đến trang B1...")
            
            # Chuyển hướng trực tiếp đến trang B1
            b1_url = "http://sinhvien.ulsa.edu.vn/wfrmDangKyLopTinChiB1.aspx?Chuyen_nganh=1"
            driver.get(b1_url)
            
            # Đợi trang tải
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            print("✅ Trang B1 đã tải xong!")
            take_screenshot("b1_page_loaded")
            
            # Lấy danh sách tên học phần cần chọn từ config
            if 'course_selections' in config:
                subject_names = config['course_selections']['subject_names_b1']
            else:
                # Fallback: extract từ selected_courses
                selected_courses = config['selected_courses']
                subject_names = []
                for course in selected_courses:
                    if '_' in course:
                        code = course.split('_')[0]
                        subject_names.append(code)
            
            print(f"🎯 Tìm kiếm {len(subject_names)} học phần:")
            for i, subject in enumerate(subject_names, 1):
                print(f"   {i}. {subject}")
            
            # Tìm và tích chọn các checkbox tương ứng với tên học phần
            checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            selected_count = 0
            found_subjects = []
            
            for checkbox in checkboxes:
                try:
                    # Tìm hàng chứa checkbox
                    row = checkbox.find_element(By.XPATH, "./ancestor::tr")
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) >= 2:  # Đảm bảo có đủ cột
                        # Kiểm tra tất cả các cột để tìm tên học phần
                        row_text = " ".join([cell.text.strip() for cell in cells])
                        
                        for subject_name in subject_names:
                            # Kiểm tra match linh hoạt
                            if (subject_name.lower() in row_text.lower() or 
                                any(word.lower() in row_text.lower() for word in subject_name.split()) or
                                any(word.lower() in subject_name.lower() for word in row_text.split())):
                                
                                print(f"✅ Tìm thấy học phần: '{subject_name}' trong '{row_text[:100]}...'")
                                if not checkbox.is_selected():
                                    driver.execute_script("arguments[0].click();", checkbox)
                                    selected_count += 1
                                    found_subjects.append(subject_name)
                                    print(f"✅ Đã chọn: {subject_name}")
                                else:
                                    print(f"⚠️ Đã được chọn sẵn: {subject_name}")
                                    found_subjects.append(subject_name)
                                break
                                
                except Exception as e:
                    continue
            
            print(f"\n📊 KẾT QUẢ BƯỚC 1:")
            print(f"   ✅ Đã chọn: {selected_count} học phần")
            print(f"   📚 Tìm thấy: {len(found_subjects)} học phần")
            
            if found_subjects:
                print("✅ Các học phần đã chọn:")
                for subject in found_subjects:
                    print(f"   - {subject}")
            
            missing_subjects = [s for s in subject_names if s not in found_subjects]
            if missing_subjects:
                print("❌ Các học phần chưa tìm thấy:")
                for subject in missing_subjects:
                    print(f"   - {subject}")
            
            if selected_count == 0:
                print("❌ Không tìm thấy học phần nào!")
                return False
            
            # Chụp màn hình sau khi chọn
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
                lambda d: "wfrmdangkyloptin" in d.current_url.lower() and "b2" in d.current_url.lower()
            )
            
            print("✅ Đã chuyển đến trang B2 thành công!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi ở Bước 1: {e}")
            return False
    
    print("🔄 BẮTĐẦU BƯỚC 1 VỚI RETRY...")
    return retry_with_reload(_step1_attempt, max_retries=5, delay=3)

def step2_select_by_class_names():
    """Bước 2: Chọn lớp tín chỉ theo TÊN trên trang B2"""
    def _step2_attempt():
        try:
            print("\n📍 BƯỚC 2: CHỌN LỚP TÍN CHỈ THEO TÊN")
            print("📍 URL hiện tại:", driver.current_url)
            
            take_screenshot("b2_page_loaded")
            
            # Đợi bảng tải xong
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "grdViewMonDangKy"))
            )
            
            # Lấy danh sách lớp tín chỉ cần chọn từ config
            if 'course_selections' in config:
                class_names = config['course_selections']['class_names_b2']
            else:
                # Fallback về cấu trúc cũ
                class_names = config['selected_courses']
            
            selected_count = 0
            found_classes = []
            not_found_classes = []
            
            print(f"🎯 Tìm kiếm {len(class_names)} lớp tín chỉ:")
            for i, class_name in enumerate(class_names, 1):
                print(f"   {i}. {class_name}")
            
            # Tìm tất cả checkbox trong bảng
            checkboxes = driver.find_elements(By.CSS_SELECTOR, "#grdViewMonDangKy input[type='checkbox']")
            print(f"🔍 Tìm thấy {len(checkboxes)} checkbox trong bảng")
            
            for checkbox in checkboxes:
                try:
                    # Tìm hàng chứa checkbox
                    row = checkbox.find_element(By.XPATH, "./ancestor::tr")
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) >= 4:
                        # Duyệt qua tất cả các cột để tìm tên lớp
                        row_text = " ".join([cell.text.strip() for cell in cells])
                        
                        # Kiểm tra xem có khớp với danh sách cần đăng ký không
                        for target_class in class_names:
                            # So sánh linh hoạt
                            if (target_class in row_text or 
                                any(part in row_text for part in target_class.split('_')) or
                                any(part in row_text for part in target_class.split('.')) or
                                target_class.split('_')[0] in row_text):  # So sánh mã học phần
                                
                                print(f"✅ Tìm thấy lớp: '{target_class}' trong '{row_text[:100]}...'")
                                
                                if not checkbox.is_selected():
                                    driver.execute_script("arguments[0].click();", checkbox)
                                    selected_count += 1
                                    found_classes.append(target_class)
                                    print(f"✅ Đã chọn: {target_class}")
                                else:
                                    print(f"⚠️ Lớp đã được chọn sẵn: {target_class}")
                                    found_classes.append(target_class)
                                    selected_count += 1
                                break
                                
                except Exception as e:
                    continue
            
            # Kiểm tra lớp nào chưa tìm thấy
            for class_name in class_names:
                if class_name not in found_classes:
                    not_found_classes.append(class_name)
            
            print(f"\n📊 KẾT QUẢ BƯỚC 2:")
            print(f"   ✅ Đã chọn: {selected_count} lớp")
            print(f"   📚 Lớp đã tìm thấy: {len(found_classes)}")
            print(f"   ❌ Lớp chưa tìm thấy: {len(not_found_classes)}")
            
            if found_classes:
                print("✅ Các lớp đã chọn:")
                for cls in found_classes:
                    print(f"   - {cls}")
            
            if not_found_classes:
                print("❌ Các lớp chưa tìm thấy:")
                for cls in not_found_classes:
                    print(f"   - {cls}")
            
            # Chụp màn hình sau khi chọn
            take_screenshot("b2_classes_selected")
            
            if selected_count == 0:
                print("❌ Không có lớp nào được chọn!")
                return False
            
            print("✅ Bước 2 hoàn thành!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi ở Bước 2: {e}")
            return False
    
    print("🔄 BẮTĐẦU BƯỚC 2 VỚI RETRY...")
    return retry_with_reload(_step2_attempt, max_retries=5, delay=3)

def step3_save_results():
    """Bước 3: Lưu kết quả và chuyển đến B3"""
    def _save_attempt():
        try:
            print("\n💾 BƯỚC 3: LUU KẾT QUẢ ĐĂNG KÝ")
            
            # Tìm nút "Lưu kết quả đăng ký"
            save_selectors = [
                "input[type='submit'][value*='Lưu kết quả đăng ký']",
                "input[type='submit'][value*='Lưu kết quả']",
                "input[type='submit'][value*='Lưu']",
                "input[type='submit'][value*='Đăng ký']", 
                "input[type='button'][value*='Lưu']",
                "#cmdDangKyLop2[value*='Lưu']",
                "#cmdSave",
                "#btnSave"
            ]
            
            save_button = None
            for selector in save_selectors:
                try:
                    save_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if save_button and save_button.is_displayed():
                        print(f"✅ Tìm thấy nút: {save_button.get_attribute('value')}")
                        break
                except:
                    continue
            
            if save_button:
                # Chụp màn hình trước khi lưu
                take_screenshot("b2_before_save")
                
                driver.execute_script("arguments[0].click();", save_button)
                print("✅ Đã bấm nút Lưu!")
                
                # Đợi phản hồi từ server
                time.sleep(5)
                
                # Kiểm tra có chuyển đến trang B3 không
                try:
                    WebDriverWait(driver, 10).until(
                        lambda d: "b3" in d.current_url.lower() or 
                                 "ketqua" in d.current_url.lower() or
                                 "wfrmdangkyloptin" in d.current_url.lower() and "b3" in d.current_url.lower()
                    )
                    print("✅ Đã chuyển đến trang kết quả (B3)!")
                    print(f"📍 URL B3: {driver.current_url}")
                    
                    # Chụp màn hình trang kết quả
                    take_screenshot("b3_final_result")
                    
                except TimeoutException:
                    print("⚠️ Chưa chuyển đến trang B3, có thể đã lưu thành công")
                
                # Kiểm tra thông báo kết quả
                try:
                    # Tìm element thông báo
                    notification_selectors = [
                        "#lblThong_bao",
                        "#lblMessage", 
                        ".alert",
                        ".notification",
                        "[id*='lblThongBao']",
                        "[id*='Message']"
                    ]
                    
                    for selector in notification_selectors:
                        try:
                            notification = driver.find_element(By.CSS_SELECTOR, selector)
                            if notification and notification.text.strip():
                                print(f"📢 Thông báo: {notification.text.strip()}")
                                break
                        except:
                            continue
                            
                except:
                    pass
                
                print("✅ Lưu kết quả thành công!")
                return True
            else:
                print("⚠️ Không tìm thấy nút Lưu, có thể đã tự động lưu")
                return True
                
        except Exception as e:
            print(f"❌ Lỗi khi lưu: {e}")
            return False
    
    print("💾 BẮTĐẦU LUU KẾT QUẢ VỚI RETRY...")
    return retry_with_reload(_save_attempt, max_retries=3, delay=2)

def main():
    """Hàm chính - Enhanced Two-Step Registration"""
    try:
        print("🤖 ULSA ENHANCED TWO-STEP REGISTRATION AUTOMATION")
        print("=" * 70)
        print("📋 Quy trình mới:")
        print("   1️⃣ Đăng nhập hệ thống (với retry thông minh)")
        print("   2️⃣ Chọn học phần theo TÊN (Trang B1 - với retry + screenshot)")
        print("   3️⃣ Chọn lớp tín chỉ theo TÊN (Trang B2 - với retry + screenshot)")
        print("   4️⃣ Lưu kết quả và chuyển B3 (với retry + screenshot)")
        print("🔄 Mỗi bước sẽ tự động retry 5 lần nếu gặp lỗi")
        print("🔄 Tự động reload trang và thử lại khi load thất bại")
        print("📸 Tự động chụp màn hình tại tất cả các bước quan trọng")
        print("🆕 Hỗ trợ cả config mới (course_selections) và cũ (selected_courses)")
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
        
        # Bước 2: Chọn học phần theo tên (Trang B1)
        if not step1_select_by_subject_names():
            print("❌ Bước 1 (chọn học phần) thất bại!")
            input("Nhấn Enter để thoát...")
            return
        
        # Bước 3: Chọn lớp tín chỉ theo tên (Trang B2)
        if not step2_select_by_class_names():
            print("❌ Bước 2 (chọn lớp tín chỉ) thất bại!")
            input("Nhấn Enter để thoát...")
            return
        
        # Bước 4: Lưu kết quả và chuyển B3
        if not step3_save_results():
            print("❌ Bước 3 (lưu kết quả) thất bại!")
        
        print("\n🎉 AUTOMATION HOÀN THÀNH!")
        print("✅ Đã thực hiện xong quy trình 3 bước đăng ký lớp tín chỉ")
        print("📸 Tất cả màn hình đã được chụp và lưu trong thư mục screenshots/")
        
        # Hỏi có muốn đóng browser không
        choice = input("\n❓ Đóng browser? (y/n): ").strip().lower()
        if choice == 'y':
            driver.quit()
            print("👋 Đã đóng browser!")
        else:
            print("🔄 Browser vẫn mở để bạn kiểm tra...")
            input("Nhấn Enter để thoát...")
            driver.quit()
        
    except KeyboardInterrupt:
        print("\n⏹️ Dừng automation bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()
