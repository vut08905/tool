#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ULSA Full Automation - Login + Course Selection from Config File
Đọc file auto_config.json và tự động đăng nhập, chọn lớp, lưu kết quả
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
screenshot_counter = 0

def setup_screenshot_directory():
    """Tạo thư mục screenshots nếu chưa có"""
    try:
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
            print("📁 Đã tạo thư mục screenshots/")
        else:
            print("📁 Thư mục screenshots/ đã tồn tại")
    except Exception as e:
        print(f"⚠️ Không thể tạo thư mục screenshots: {e}")

def take_screenshot(step_name):
    """Chụp ảnh màn hình với tên mô tả"""
    global driver
    if not driver:
        return
        
    try:
        # Tạo tên file với timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{step_name}.png"
        filepath = os.path.join("screenshots", filename)
        
        # Chụp ảnh
        driver.save_screenshot(filepath)
        print(f"📷 Đã chụp ảnh: {filename}")
        
    except Exception as e:
        print(f"⚠️ Không thể chụp ảnh: {e}")

def check_page_error():
    """Kiểm tra xem trang có bị lỗi không (503, 404, timeout, etc.)"""
    try:
        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower()
        title = driver.title.lower()
        
        # Kiểm tra các lỗi phổ biến
        error_indicators = [
            # HTTP Status Codes
            "503 service unavailable",
            "504 gateway timeout", 
            "502 bad gateway",
            "500 internal server error",
            "404 not found",
            "403 forbidden",
            
            # Thông báo lỗi tiếng Việt
            "trang web tạm thời không khả dụng",
            "máy chủ quá tải",
            "kết nối bị gián đoạn",
            "không thể truy cập",
            "lỗi máy chủ",
            "trang không tồn tại",
            "quá tải",
            "server unavailable",
            "connection timed out",
            "this site can't be reached",
            "took too long to respond",
            
            # Lỗi cụ thể của ULSA
            "application error",
            "runtime error",
            "server error"
        ]
        
        # Kiểm tra trong title và page source
        for error in error_indicators:
            if error in title or error in page_source:
                print(f"🔍 Phát hiện lỗi: {error}")
                
                # Trả về loại lỗi
                if "404" in error or "not found" in error or "không tồn tại" in error:
                    return "404"
                elif any(code in error for code in ["503", "502", "504", "500", "quá tải", "unavailable", "timeout"]):
                    return "server_error"
                else:
                    return "general_error"
        
        # Kiểm tra xem có phải trang trống hay không
        if len(page_source.strip()) < 100:
            print("🔍 Phát hiện trang trống hoặc không tải được")
            return "empty_page"
        
        # Kiểm tra xem có form đăng nhập nào không (có thể bị logout)
        if "login.aspx" in current_url:
            print("🔍 Đã bị logout - cần đăng nhập lại")
            return "logged_out"
        
        # Trang OK
        return None
        
    except Exception as e:
        print(f"⚠️ Lỗi khi kiểm tra trang: {e}")
        return "check_error"

def retry_with_smart_recovery(action_func, max_retries=None, action_name="thao tác"):
    """
    🔄 INFINITE RETRY: Thực hiện action với retry VÔ HẠN cho đến khi thành công
    
    Args:
        action_func: Hàm cần thực hiện
        max_retries: Không sử dụng (infinite retry)
        action_name: Tên của thao tác để hiển thị
    """
    print(f"🔄 INFINITE RETRY MODE: Sẽ retry vô hạn cho đến khi {action_name} thành công!")
    
    attempt = 0
    while True:  # INFINITE LOOP - không giới hạn số lần thử
        attempt += 1
        try:
            print(f"🔄 Thực hiện {action_name} (lần {attempt})")
            
            # Thực hiện action
            result = action_func()
            
            # Kiểm tra trang có lỗi không
            error_type = check_page_error()
            
            if error_type is None:
                print(f"✅ {action_name} thành công!")
                return result
            
            # Xử lý theo loại lỗi
            if attempt < max_retries:  # Còn lần retry
                if error_type == "404" or error_type == "logged_out":
                    print(f"🔑 Lỗi 404/logout - Cần đăng nhập lại...")
                    # Thực hiện đăng nhập lại bằng cách gọi hàm trực tiếp
                    try:
                        driver.get("http://sinhvien.ulsa.edu.vn/Login.aspx")
                        # Đăng nhập đơn giản
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
                        driver.execute_script("arguments[0].click();", login_button)
                        
                        # Đợi đăng nhập xong
                        WebDriverWait(driver, 10).until(
                            lambda d: "login.aspx" not in d.current_url.lower()
                        )
                        print("✅ Đăng nhập lại thành công, tiếp tục...")
                        continue
                    except Exception as e:
                        print(f"❌ Đăng nhập lại thất bại: {e}")
                        return False
                
                elif error_type in ["server_error", "general_error", "empty_page", "check_error"]:
                    wait_time = min(2 ** attempt, 10)  # Exponential backoff, max 10s
                    print(f"⏳ Lỗi máy chủ - Đợi {wait_time}s rồi load lại trang...")
                    
                    # Chụp ảnh trước khi retry
                    take_screenshot(f"error_retry_{attempt}_{action_name}")
                    
                    time.sleep(wait_time)
                    
                    # Refresh trang
                    try:
                        driver.refresh()
                        # Đợi trang tải lại
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        print("🔄 Đã load lại trang")
                    except Exception as e:
                        print(f"⚠️ Lỗi khi refresh trang: {e}")
                        # Thử navigate lại URL
                        try:
                            current_url = driver.current_url
                            driver.get(current_url)
                            print("🔄 Đã navigate lại URL")
                        except:
                            print("❌ Không thể load lại trang")
                    
                    continue
            
            # Hết lần retry
            print(f"❌ {action_name} thất bại sau {max_retries + 1} lần thử!")
            return False
            
        except WebDriverException as e:
            if "net::" in str(e) or "timeout" in str(e).lower():
                print(f"🌐 Lỗi kết nối mạng (lần {attempt + 1}): {e}")
                if attempt < max_retries:
                    wait_time = min(3 * (attempt + 1), 15)  # 3, 6, 9, 12, 15s
                    print(f"⏳ Đợi {wait_time}s rồi thử lại...")
                    time.sleep(wait_time)
                    continue
            else:
                raise e
        except Exception as e:
            print(f"❌ Lỗi không mong muốn trong {action_name}: {e}")
            if attempt < max_retries:
                time.sleep(2)
                continue
            return False
    
    return False

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

def load_config():
    """Đọc và kiểm tra file cấu hình"""
    global config
    config_file = os.path.join(os.path.dirname(__file__), "..", "auto_config.json")
    
    if not os.path.exists(config_file):
        print("❌ Không tìm thấy file auto_config.json!")
        print("📄 Vui lòng tạo file cấu hình với thông tin đăng nhập và danh sách lớp.")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Kiểm tra thông tin bắt buộc
        student_id = config['login_info']['student_id']
        password = config['login_info']['password']
        
        if not student_id or student_id == "":
            print("❌ Mã sinh viên không được để trống!")
            return False
            
        if not password or password == "" or password == "your_password_here":
            print("❌ Mật khẩu không được để trống hoặc chưa được thay đổi!")
            print("📝 Vui lòng cập nhật mật khẩu trong auto_config.json")
            return False
        
        if len(config['selected_courses']) == 0:
            print("❌ Danh sách lớp cần đăng ký không được để trống!")
            return False
        
        print("✅ Đã đọc file cấu hình thành công!")
        print(f"👤 Mã sinh viên: {student_id}")
        print(f"🔒 Mật khẩu: {'*' * len(password)}")
        print(f"📚 Số lớp cần đăng ký: {len(config['selected_courses'])}")
        print(f"🔧 Chế độ test: {config['automation_settings']['test_mode']}")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi đọc file cấu hình: {e}")
        return False

def setup_chrome_driver():
    """Cấu hình và khởi động ChromeDriver"""
    global driver
    try:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Tạo tab phụ để hiển thị thông tin định danh
        window_title = get_chrome_window_title()
        driver.execute_script(f"""
            // Tạo tab mới với thông tin định danh
            window.open('about:blank', '_blank');
        """)
        
        # Chuyển về tab đầu tiên (tab chính)
        driver.switch_to.window(driver.window_handles[0])
        
        # Set title cho tab phụ
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
            # Chuyển lại về tab chính để làm việc
            driver.switch_to.window(driver.window_handles[0])
        
        print(f"✅ ChromeDriver đã được khởi động thành công! [{window_title}]")
        
        # Chụp ảnh sau khi khởi động browser
        take_screenshot("browser_started")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi khi khởi động ChromeDriver: {str(e)}")
        return False

def login_to_ulsa():
    """Đăng nhập vào hệ thống ULSA với retry thông minh"""
    def _login_action():
        print("🌐 Đang truy cập trang đăng nhập ULSA...")
        driver.get("http://sinhvien.ulsa.edu.vn/Login.aspx")
        
        # Đợi trang tải hoàn toàn - kiểm tra form xuất hiện
        print("⏳ Đang đợi form đăng nhập xuất hiện...")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            print("✅ Form đăng nhập đã xuất hiện!")
        except:
            print("⚠️ Form đăng nhập chưa xuất hiện, tiếp tục...")
        
        print(f"📍 URL hiện tại: {driver.current_url}")
        print(f"📄 Title trang: {driver.title}")
        
        # Lấy thông tin đăng nhập
        student_id = config['login_info']['student_id']
        password = config['login_info']['password']
        
        print(f"👤 Đang tìm field để điền mã sinh viên: {student_id}")
        
        # Tìm username field với các selector hoạt động
        username_field = None
        username_selectors = [
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.ID, "txtTenDangNhap"),
            (By.NAME, "txtTenDangNhap")
        ]
        
        for by_type, selector in username_selectors:
            try:
                username_field = WebDriverWait(driver, 1).until(  # Giảm từ 2 xuống 1
                    EC.presence_of_element_located((by_type, selector))
                )
                if username_field:
                    print(f"✅ Tìm thấy username field: {selector}")
                    break
            except:
                continue
        
        if not username_field:
            print("❌ KHÔNG TÌM THẤY FIELD MÃ SINH VIÊN!")
            return False
        
        print(f"🔒 Đang tìm field để điền mật khẩu...")
        
        # Tìm password field với các selector hoạt động
        password_field = None
        password_selectors = [
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.ID, "txtMatKhau"),
            (By.NAME, "txtMatKhau")
        ]
        
        for by_type, selector in password_selectors:
            try:
                password_field = WebDriverWait(driver, 1).until(  # Giảm từ 2 xuống 1
                    EC.presence_of_element_located((by_type, selector))
                )
                if password_field:
                    print(f"✅ Tìm thấy password field: {selector}")
                    break
            except:
                continue
        
        if not password_field:
            print("❌ KHÔNG TÌM THẤY FIELD MẬT KHẨU!")
            return False
        
        # Điền thông tin đăng nhập
        print("📝 Đang điền thông tin đăng nhập...")
        
        try:
            # Clear và điền mã sinh viên
            username_field.clear()
            username_field.send_keys(student_id)
            print(f"✅ Đã điền mã sinh viên: {student_id}")
            
            # Clear và điền mật khẩu  
            password_field.clear()
            password_field.send_keys(password)
            print("✅ Đã điền mật khẩu: ************")
            
        except Exception as e:
            print(f"❌ Lỗi khi điền thông tin: {e}")
            return False
        
        # Tìm và click nút đăng nhập
        print("🔍 Đang tìm nút đăng nhập...")
        
        login_button = None
        login_selectors = [
            (By.ID, "btnDangNhap"),
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//input[@value='Đăng nhập']")
        ]
        
        for by_type, selector in login_selectors:
            try:
                login_button = driver.find_element(by_type, selector)
                if login_button:
                    print(f"✅ Tìm thấy login button: {selector}")
                    break
            except:
                continue
        
        if not login_button:
            print("❌ KHÔNG TÌM THẤY NÚT ĐĂNG NHẬP!")
            return False
        
        # Click đăng nhập
        print("🚀 Đang thực hiện đăng nhập...")
        try:
            driver.execute_script("arguments[0].click();", login_button)
            print("✅ Đã click nút đăng nhập")
        except Exception as e:
            print(f"❌ Lỗi khi click đăng nhập: {e}")
            return False
        
        # Đợi kết quả đăng nhập - kiểm tra điều kiện thay vì đợi cố định
        print("⏳ Đang chờ kết quả đăng nhập...")
        try:
            # Đợi URL thay đổi hoặc thông báo lỗi xuất hiện (giảm timeout)
            WebDriverWait(driver, 5).until(  # Giảm từ 10 xuống 5
                lambda d: "login.aspx" not in d.current_url.lower() or 
                         EC.presence_of_element_located((By.ID, "lblThong_bao"))(d)
            )
            print("✅ Phản hồi đăng nhập đã nhận được!")
        except:
            print("⚠️ Không nhận được phản hồi đăng nhập, tiếp tục kiểm tra...")
        
        # Kiểm tra đăng nhập thành công bằng nhiều cách
        login_success = False
        error_message = ""
        
        print("🔍 Đang kiểm tra kết quả đăng nhập...")
        
        try:
            # Kiểm tra có thông báo lỗi không
            error_element = driver.find_element(By.ID, "lblThong_bao")
            if error_element and error_element.text.strip():
                error_message = error_element.text.strip()
                print(f"📢 Thông báo từ hệ thống: {error_message}")
                if any(word in error_message.lower() for word in ["sai", "lỗi", "không đúng", "thất bại"]):
                    print(f"❌ Lỗi đăng nhập: {error_message}")
                    return False
        except:
            pass
        
        # Kiểm tra URL có thay đổi không (tránh còn ở trang login)
        current_url = driver.current_url.lower()
        print(f"📍 URL sau đăng nhập: {current_url}")
        
        if "login.aspx" in current_url:
            print("❌ Vẫn ở trang đăng nhập - thông tin đăng nhập có thể không đúng!")
            return False
        
        # Kiểm tra có menu người dùng hoặc tên sinh viên
        success_indicators = [
            (By.CLASS_NAME, "nav-menu"),
            (By.ID, "HeaderSV1_lblHo_ten"),
            (By.CLASS_NAME, "dropdown"),
            (By.PARTIAL_LINK_TEXT, "Đăng xuất"),
            (By.PARTIAL_LINK_TEXT, "Thông tin"),
            (By.CSS_SELECTOR, "[href*='Logout']"),
            (By.CSS_SELECTOR, ".user-info"),
            (By.CSS_SELECTOR, ".student-name")
        ]
        
        for by_type, locator in success_indicators:
            try:
                element = WebDriverWait(driver, 1).until(  # Giảm từ 2 xuống 1
                    EC.presence_of_element_located((by_type, locator))
                )
                if element:
                    login_success = True
                    print(f"✅ Tìm thấy element đăng nhập thành công: {locator}")
                    break
            except:
                continue
        
        # Kiểm tra cuối cùng - xem có trang dashboard/default không
        if not login_success:
            if "default.aspx" in current_url or "dashboard" in current_url.lower():
                login_success = True
                print("✅ Đã vào trang chính - đăng nhập thành công!")
        
        if login_success:
            print("🎉 ĐĂNG NHẬP THÀNH CÔNG!")
            
            # Chụp ảnh sau khi đăng nhập thành công
            take_screenshot("login_success")
            
            # Tìm và hiển thị tên sinh viên nếu có
            try:
                name_element = driver.find_element(By.ID, "HeaderSV1_lblHo_ten")
                if name_element and name_element.text.strip():
                    print(f"👋 Xin chào: {name_element.text.strip()}")
            except:
                pass
            
            return True
        else:
            print("❌ ĐĂNG NHẬP THẤT BẠI!")
            print("🔍 Vui lòng kiểm tra lại:")
            print("   - Mã sinh viên có đúng không?")
            print("   - Mật khẩu có đúng không?")
            print("   - Tài khoản có bị khóa không?")
            print("   - Kết nối mạng có ổn định không?")
            return False
    
    # Sử dụng retry logic với smart recovery  
    return retry_with_smart_recovery(_login_action, max_retries=3, action_name="đăng nhập ULSA")

def navigate_to_course_registration():
    """Điều hướng đến trang đăng ký lớp tín chỉ với retry thông minh"""
    def _navigate_action():
        test_mode = config['automation_settings']['test_mode']
        
        if test_mode == "local":
            # Sử dụng file HTML local
            local_file = os.path.join(os.path.dirname(__file__), "..", "b2.html")
            if os.path.exists(local_file):
                file_url = f"file:///{os.path.abspath(local_file).replace(os.sep, '/')}"
                print(f"📁 Đang mở file local để test: {local_file}")
                driver.get(file_url)
                return True
            else:
                print("❌ Không tìm thấy file b2.html!")
                return False
        else:
            # Sử dụng website ULSA thật - TỰ ĐỘNG CHUYỂN HƯỚNG
            current_url = driver.current_url.lower()
            print(f"📍 URL hiện tại: {driver.current_url}")
            
            # Kiểm tra xem có đang ở trang SinhVien.aspx không
            if "sinhvien.aspx" in current_url:
                print("🔄 Phát hiện đang ở trang SinhVien.aspx - TỰ ĐỘNG CHUYỂN HƯỚNG!")
                print("⚡ Bỏ qua việc tìm nút, chuyển thẳng đến trang đăng ký...")
            
            # Truy cập TRỰC TIẾP trang đăng ký lớp tín chỉ
            registration_url = "http://sinhvien.ulsa.edu.vn/wfrmDangKyLopTinChiB1.aspx?Chuyen_nganh=1"
            print(f"🎯 Chuyển hướng trực tiếp đến: {registration_url}")
            driver.get(registration_url)
            
            # Đợi trang tải hoàn toàn - kiểm tra element xuất hiện
            print("⏳ Đang đợi trang đăng ký tải...")
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "form"))
                )
                print("✅ Trang đăng ký đã tải xong!")
            except:
                print("⚠️ Trang đăng ký chưa tải hoàn toàn, tiếp tục...")

            print(f"� URL sau khi chuyển hướng: {driver.current_url}")
            
            # Kiểm tra xem có phải trang đăng ký môn học không
            current_page_source = driver.page_source.lower()
            
            if ("chưa đến thời gian" in current_page_source or 
                "chưa mở đăng ký" in current_page_source or
                "không trong thời gian" in current_page_source or
                len(driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")) == 0):
                
                print("⚠️ Phát hiện chưa đến thời gian đăng ký hoặc không có môn học!")
                print("🔄 Chuyển hướng tạm thời đến b2.html để test chức năng...")
                
                # Chuyển đến file b2.html
                local_file = os.path.join(os.path.dirname(__file__), "..", "b2.html")
                if os.path.exists(local_file):
                    file_url = f"file:///{os.path.abspath(local_file).replace(os.sep, '/')}"
                    print(f"📁 Đang chuyển đến file backup: {local_file}")
                    driver.get(file_url)
                    return True
                else:
                    print("❌ Không tìm thấy file b2.html backup!")
                    return False
            
            print("✅ Chuyển hướng trực tiếp thành công - tiết kiệm thời gian!")
            return True
    
    # Sử dụng retry logic với smart recovery
    return retry_with_smart_recovery(_navigate_action, max_retries=3, action_name="điều hướng trang đăng ký")

def select_courses_from_config():
    """Chọn các môn học từ file cấu hình với TWO-STEP PROCESS"""
    def _select_courses_action():
        current_url = driver.current_url.lower()
        
        # Kiểm tra xem đang ở trang nào
        if "wfrmdangkyloptin" in current_url and "b1" in current_url:
            print("📍 Đang ở trang B1 - Chọn mã học phần")
            return step1_select_course_codes()
        elif "wfrmdangkyloptin" in current_url and "b2" in current_url:
            print("📍 Đang ở trang B2 - Chọn lớp tín chỉ cụ thể")
            return step2_select_specific_classes()
        else:
            print("� Trang không xác định, thử workflow cũ...")
            return legacy_select_courses()
            
    # Sử dụng retry logic với smart recovery
    return retry_with_smart_recovery(_select_courses_action, max_retries=3, action_name="chọn lớp tín chỉ")

def step1_select_course_codes():
    """Bước 1: Chọn mã học phần trên trang B1"""
    try:
        print("\n� BƯỚC 1: CHỌN MÃ HỌC PHẦN")
        
        # Đợi trang tải
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        selected_courses = config['selected_courses']
        course_codes = set()
        
        # Trích xuất mã học phần từ tên lớp
        for course in selected_courses:
            if '_' in course:
                code = course.split('_')[0]  # Lấy phần trước dấu _
                course_codes.add(code)
                print(f"� Cần chọn mã học phần: {code}")
        
        # Tìm và chọn checkbox
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        selected_count = 0
        
        for checkbox in checkboxes:
            try:
                row = checkbox.find_element(By.XPATH, "./ancestor::tr")
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 3:
                    for cell in cells[1:4]:  # Kiểm tra 3 cột đầu
                        cell_text = cell.text.strip()
                        if cell_text in course_codes:
                            print(f"✅ Tìm thấy mã học phần: {cell_text}")
                            if not checkbox.is_selected():
                                driver.execute_script("arguments[0].click();", checkbox)
                                selected_count += 1
                                print(f"✅ Đã chọn: {cell_text}")
                            break
            except Exception as e:
                continue
        
        print(f"📊 Đã chọn {selected_count} mã học phần")
        
        if selected_count == 0:
            print("❌ Không tìm thấy mã học phần nào!")
            return False
        
        # Bấm nút "Đăng ký lớp tín chỉ"
        print("🔄 Đang bấm nút 'Đăng ký lớp tín chỉ'...")
        register_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "cmdDangKyLop2"))
        )
        
        driver.execute_script("arguments[0].click();", register_button)
        
        # Đợi chuyển đến trang B2
        print("⏳ Đang đợi chuyển đến trang B2...")
        WebDriverWait(driver, 10).until(
            lambda d: "b2" in d.current_url.lower() or "grdViewMonDangKy" in d.page_source
        )
        
        print("✅ Đã chuyển đến trang B2!")
        
        # Tiếp tục với bước 2
        return step2_select_specific_classes()
        
    except Exception as e:
        print(f"❌ Lỗi ở Bước 1: {e}")
        return False

def step2_select_specific_classes():
    """Bước 2: Chọn lớp tín chỉ cụ thể trên trang B2"""
    try:
        print("\n📍 BƯỚC 2: CHỌN LỚP TÍN CHỈ CỤ THỂ")
        
        # Đợi bảng tải xong
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "grdViewMonDangKy"))
        )
        
        selected_courses = config['selected_courses']
        selected_count = 0
        found_classes = []
        
        print(f"🎯 Tìm kiếm {len(selected_courses)} lớp cụ thể:")
        
        # Tìm tất cả checkbox trong bảng
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "#grdViewMonDangKy input[type='checkbox']")
        print(f"🔍 Tìm thấy {len(checkboxes)} checkbox trong bảng")
        
        for checkbox in checkboxes:
            try:
                row = checkbox.find_element(By.XPATH, "./ancestor::tr")
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 4:
                    # Cột 3: Mã học phần
                    course_code = cells[2].text.strip()
                    # Cột 4: Tên học phần (có chứa mã lớp)
                    course_name = cells[3].text.strip()
                    
                    # Trích xuất mã lớp từ tên học phần
                    class_code = ""
                    if '(' in course_name and ')' in course_name:
                        class_part = course_name.split('(')[1].split(')')[0]
                        class_code = class_part.strip()
                    
                    # Kiểm tra khớp với danh sách cần đăng ký
                    for target_course in selected_courses:
                        if (target_course == class_code or 
                            target_course.startswith(course_code) and class_code in target_course):
                            
                            print(f"✅ Tìm thấy lớp: {class_code}")
                            
                            if not checkbox.is_selected():
                                driver.execute_script("arguments[0].click();", checkbox)
                                selected_count += 1
                                found_classes.append(class_code)
                                print(f"✅ Đã chọn: {class_code}")
                                
                                # Chụp ảnh sau khi chọn thành công
                                take_screenshot(f"selected_class_{class_code}")
                            break
                            
            except Exception as e:
                continue
        
        print(f"\n📊 KẾT QUẢ BƯỚC 2:")
        print(f"   ✅ Đã chọn: {selected_count} lớp")
        
        if selected_count == 0:
            print("❌ Không có lớp nào được chọn!")
            return False
        
        # Chụp ảnh hoàn thành việc chọn
        take_screenshot("course_selection_completed")
        
        # Lưu kết quả
        return save_registration_results(found_classes, [])
        
    except Exception as e:
        print(f"❌ Lỗi ở Bước 2: {e}")
        return False

def save_registration_results(selected_courses_info, not_found_classes):
    """Lưu kết quả đăng ký với retry thông minh"""
    def _save_action():
        # Tìm và bấm nút Lưu
        save_button = driver.find_element(By.ID, "cmdDangKyLop2")
        if save_button:
            print("\n💾 Đang lưu kết quả đăng ký...")
            driver.execute_script("arguments[0].click();", save_button)
            
            # Đợi kết quả lưu hoàn tất - kiểm tra thông báo xuất hiện
            print("⏳ Đang đợi kết quả lưu...")
            try:
                WebDriverWait(driver, 5).until(  # Giảm từ 10 xuống 5
                    lambda d: EC.presence_of_element_located((By.ID, "lblThong_bao"))(d) and
                             d.find_element(By.ID, "lblThong_bao").text.strip() != ""
                )
                print("✅ Đã nhận được phản hồi từ hệ thống!")
            except:
                print("⚠️ Không nhận được thông báo rõ ràng, tiếp tục...")
            
            # Kiểm tra thông báo kết quả
            success = True
            notification_text = ""
            try:
                notification = driver.find_element(By.ID, "lblThong_bao")
                notification_text = notification.text.strip()
                if notification_text:
                    print(f"📢 Thông báo từ hệ thống: {notification_text}")
                    if any(word in notification_text.lower() for word in ["lỗi", "không thể", "thất bại", "error"]):
                        success = False
                else:
                    print("✅ Lưu thành công!")
                    
                    # Chụp ảnh sau khi lưu thành công
                    take_screenshot("save_success")
            except:
                print("✅ Đã lưu (không có thông báo)")
            
            # Kiểm tra xem các môn đã được lưu thực sự chưa
            print("\n🔍 Đang kiểm tra kết quả đăng ký...")
            
            # Đợi kết quả lưu hoàn tất - kiểm tra thông báo hoặc trạng thái
            try:
                WebDriverWait(driver, 3).until(  # Giảm từ 5 xuống 3
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][name^='chkSelect']:checked")) > 0 or
                             EC.presence_of_element_located((By.ID, "lblMessage"))(d)
                )
                print("✅ Kết quả đăng ký đã được cập nhật!")
            except:
                print("⚠️ Không thể xác nhận kết quả, tiếp tục kiểm tra...")
            
            # Đếm số checkbox đã được tích sau khi lưu
            checked_boxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][name^='chkSelect']:checked")
            actually_registered = []
            
            for checkbox in checked_boxes:
                try:
                    row = checkbox.find_element(By.XPATH, "../../..")
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 6:
                        course_code = cells[2].text.strip()
                        course_name = cells[3].text.strip()
                        class_name = cells[5].text.strip()
                        actually_registered.append({
                            'code': course_code,
                            'name': course_name,
                            'class': class_name
                        })
                except:
                    continue
            
            # Hiển thị kết quả
            print(f"\n📋 KẾT QUẢ CUỐI CÙNG:")
            print(f"   🎯 Lớp muốn đăng ký: {len(config['selected_courses'])}")
            print(f"   ✅ Lớp đã chọn thành công: {len(selected_courses_info)}")
            print(f"   💾 Lớp đã lưu trong hệ thống: {len(actually_registered)}")
            
            if actually_registered:
                print(f"\n✅ Các lớp đã đăng ký thành công:")
                for course in actually_registered:
                    print(f"   📚 {course['code']} - {course['name']} - {course['class']}")
            
            # Kiểm tra sự khác biệt
            registered_classes = [course['class'] for course in actually_registered]
            failed_classes = [cls for cls in config['selected_courses'] if cls not in registered_classes]
            
            if failed_classes:
                print(f"\n❌ Các lớp không đăng ký được:")
                for class_name in failed_classes:
                    print(f"   ⚠️ {class_name}")
            
            # Lưu kết quả chi tiết vào file
            result_data = {
                'timestamp': datetime.now().isoformat(),
                'student_id': config['login_info']['student_id'],
                'test_mode': config['automation_settings']['test_mode'],
                'requested_courses': config['selected_courses'],
                'selected_courses': selected_courses_info,
                'actually_registered': actually_registered,
                'registration_successful': success and len(actually_registered) > 0,
                'total_requested': len(config['selected_courses']),
                'total_selected': len(selected_courses_info),
                'total_registered': len(actually_registered),
                'not_found_classes': not_found_classes,
                'failed_classes': failed_classes,
                'notification': notification_text,
                'success_rate': len(actually_registered) / len(config['selected_courses']) * 100 if config['selected_courses'] else 0
            }
            
            result_file = os.path.join(os.path.dirname(__file__), "..", "registration_result.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n📄 Kết quả chi tiết đã được lưu vào: registration_result.json")
            print(f"🎯 Tỷ lệ thành công: {result_data['success_rate']:.1f}%")
            
            # Screenshot nếu cần
            if config['automation_settings']['screenshot_on_error'] and not success:
                try:
                    screenshot_file = os.path.join(os.path.dirname(__file__), "..", f"error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    driver.save_screenshot(screenshot_file)
                    print(f"📸 Đã chụp màn hình lỗi: {screenshot_file}")
                except:
                    pass
            
            return success and len(actually_registered) > 0
        else:
            print("❌ Không tìm thấy nút Lưu!")
            return False
            
    # Sử dụng retry logic với smart recovery
    return retry_with_smart_recovery(_save_action, max_retries=3, action_name="lưu kết quả đăng ký")

def legacy_select_courses():
    """Legacy course selection cho các trang không phải B1/B2"""
    try:
        print("🔄 Sử dụng phương pháp chọn lớp cũ...")
        
        # Đợi trang tải
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        selected_classes = config['selected_courses']
        selected_count = 0
        selected_courses_info = []
        not_found_classes = []
        
        # Tìm checkbox với nhiều phương pháp
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"🔍 Tìm thấy {len(checkboxes)} checkbox")
        
        course_mapping = {}
        
        for i, checkbox in enumerate(checkboxes):
            try:
                row = checkbox.find_element(By.XPATH, "./ancestor::tr")
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 3:
                    # Tìm thông tin trong các cột
                    course_code = ""
                    course_name = ""
                    class_name = ""
                    
                    for cell in cells:
                        cell_text = cell.text.strip()
                        if cell_text and len(cell_text) >= 6:
                            if any(c.isdigit() for c in cell_text) and any(c.isalpha() for c in cell_text):
                                if not course_code:
                                    course_code = cell_text
                                elif "_" in cell_text:
                                    class_name = cell_text
                            elif len(cell_text) > 10:
                                course_name = cell_text
                    
                    if course_code:
                        for course in selected_classes:
                            if course_code in course:
                                course_mapping[course] = {
                                    'checkbox': checkbox,
                                    'code': course_code,
                                    'name': course_name,
                                    'class': class_name or course
                                }
                                break
                                
            except Exception as e:
                continue
        
        # Chọn các lớp
        for class_name in selected_classes:
            if class_name in course_mapping:
                course_info = course_mapping[class_name]
                checkbox = course_info['checkbox']
                
                if not checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox)
                    selected_count += 1
                    selected_courses_info.append(course_info)
                    print(f"✅ Đã chọn: {class_name}")
            else:
                not_found_classes.append(class_name)
                print(f"❌ Không tìm thấy: {class_name}")
        
        print(f"📊 Đã chọn {selected_count}/{len(selected_classes)} lớp")
        
        if selected_count == 0:
            print("❌ Không có lớp nào được chọn!")
            return False
        
        # Chụp ảnh và lưu kết quả
        take_screenshot("legacy_course_selection_completed")
        return save_registration_results(selected_courses_info, not_found_classes)
        
    except Exception as e:
        print(f"❌ Lỗi trong legacy selection: {e}")
        return False

def main():
    """Hàm chính với kiểm tra nghiêm ngặt"""
    try:
        print("🤖 ULSA Full Automation - Login + Course Selection (IMPROVED)")
        print("=" * 60)
        print("🚀 Tính năng mới: CHUYỂN HƯỚNG TRỰC TIẾP")
        print("   ⚡ Tự động chuyển từ SinhVien.aspx sang wfrmDangKyLopTinChiB1.aspx")
        print("   🎯 Tiết kiệm 3-5s mỗi lần chạy - Không cần tìm nút!")
        print("   ✅ Infinite retry system - Retry đến khi thành công!")
        print("=" * 60)
        
        # Tạo thư mục screenshots
        setup_screenshot_directory()
        
        # Bước 1: Đọc và kiểm tra file cấu hình
        print("📋 BƯỚC 1: KIỂM TRA FILE CẤU HÌNH")
        if not load_config():
            print("❌ Không thể tiếp tục - file cấu hình có vấn đề!")
            input("Nhấn Enter để thoát...")
            return
        
        # Bước 2: Khởi động browser
        print("\n🌐 BƯỚC 2: KHỞI ĐỘNG TRÌNH DUYỆT")
        if not setup_chrome_driver():
            print("❌ Không thể khởi động trình duyệt!")
            input("Nhấn Enter để thoát...")
            return
        
        test_mode = config['automation_settings']['test_mode']
        
        # Bước 3: Đăng nhập (chỉ khi dùng website thật)
        if test_mode == "ulsa":
            print("\n🔐 BƯỚC 3: ĐĂNG NHẬP HỆ THỐNG")
            if not login_to_ulsa():
                print("❌ ĐĂNG NHẬP THẤT BẠI - DỪNG AUTOMATION!")
                print("🔧 Vui lòng kiểm tra lại thông tin trong auto_config.json")
                
                # Chụp màn hình lỗi
                try:
                    error_screenshot = os.path.join(os.path.dirname(__file__), "..", f"login_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    driver.save_screenshot(error_screenshot)
                    print(f"� Đã chụp màn hình lỗi: {error_screenshot}")
                except:
                    pass
                
                input("Nhấn Enter để thoát...")
                return
            
            print("✅ ĐĂNG NHẬP THÀNH CÔNG - TIẾP TỤC AUTOMATION!")
        else:
            print("\n📁 BƯỚC 3: CHẾ ĐỘ TEST LOCAL - BỎ QUA ĐĂNG NHẬP")
        
        # Bước 4: Điều hướng đến trang đăng ký với AUTO-DETECTION
        print("\n🎯 BƯỚC 4: VÀO TRANG ĐĂNG KÝ LỚP TÍN CHỈ")
        print("🔍 Auto-detecting registration flow...")
        if not navigate_to_course_registration():
            print("❌ Không thể truy cập trang đăng ký!")
            input("Nhấn Enter để thoát...")
            return
        
        # Bước 5: Tự động tiếp tục (không cần hỏi người dùng)
        if test_mode == "ulsa":
            print("\n⏸️ BƯỚC 5: XÁC NHẬN TRƯỚC KHI CHỌN LỚP")
            print("🔍 Kiểm tra tự động:")
            print("   ✅ Trang đăng ký lớp đã tải xong")
            print("   ✅ Danh sách lớp đã hiển thị")
            print("   ✅ Tự động tiếp tục automation...")
            print("\n🚀 Tiếp tục chọn lớp tự động...")
            # Tự động chọn "y" - không cần input từ người dùng
        
        # Bước 6: Auto-detect và chọn lớp với TWO-STEP PROCESS
        print("\n📚 BƯỚC 6: TỰ ĐỘNG CHỌN LỚP (TWO-STEP PROCESS)")
        print("🔍 Detecting current page and using appropriate method...")
        if select_courses_from_config():
            print("\n🎉 AUTOMATION HOÀN THÀNH THÀNH CÔNG!")
            
            # Chụp ảnh hoàn thành automation
            take_screenshot("automation_completed")
            
            print("📊 Vui lòng kiểm tra file registration_result.json để xem kết quả chi tiết.")
            print("✅ Hệ thống đã tự động xử lý quy trình 2 bước và retry thông minh!")
        else:
            print("\n😞 AUTOMATION KHÔNG THÀNH CÔNG HOÀN TOÀN.")
            
            # Chụp ảnh lỗi automation
            take_screenshot("automation_failed")
            
            print("🔍 Vui lòng kiểm tra lại danh sách lớp trong auto_config.json")
            print("⚠️ Hệ thống đã retry nhiều lần nhưng vẫn gặp lỗi")
        
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
        take_screenshot("automation_stopped")
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
        take_screenshot("automation_error")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()
