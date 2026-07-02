# Đảm bảo stdout/stderr luôn là utf-8 để tránh lỗi charmap codec khi chạy qua GUI trên Windows
import sys
if hasattr(sys.stdout, 'reconfigure'):
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ULSA Auto Login with Title Check
Tự động reload trang cho đến khi title thay đổi, sau đó đăng nhập tự động
"""

import time
import os
import json
import shutil
import subprocess
import webbrowser
import urllib.request
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Global variables
driver = None
config = {}
GUI_MODE = False  # True khi chạy từ GUI, False khi chạy từ command line

# CẤU HÌNH: Sử dụng Chrome đang mở (debugging mode)
USE_EXISTING_CHROME = False  # True = kết nối vào Chrome đang mở, False = mở Chrome mới
DEBUGGING_PORT = 9222  # Cổng debug (mặc định 9222)

def safe_input(prompt=""):
    """Input an toàn - bỏ qua nếu chạy từ GUI"""
    if GUI_MODE:
        return ""  # Không cần input khi chạy từ GUI
    try:
        return safe_input(prompt)
    except:
        return ""  # Trả về empty nếu không có stdin

def check_chrome_installed():
    """Kiểm tra Chrome đã được cài đặt chưa"""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            return True, path
    return False, None

def get_chromedriver_path():
    """Tìm ChromeDriver trong thư mục local trước, nếu không có thì tải về"""
    # Các đường dẫn để tìm chromedriver.exe
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    local_paths = [
        os.path.join(current_dir, "drivers", "chromedriver.exe"),  # automation/drivers/
        os.path.join(parent_dir, "drivers", "chromedriver.exe"),   # root/drivers/
        os.path.join(current_dir, "chromedriver.exe"),             # automation/
        os.path.join(parent_dir, "chromedriver.exe"),              # root/
    ]
    
    # Tìm chromedriver local
    for path in local_paths:
        if os.path.exists(path):
            print(f"✅ Tìm thấy ChromeDriver local: {path}")
            return path
    
    # Không tìm thấy, tải về bằng ChromeDriverManager
    print("📥 Không tìm thấy ChromeDriver local, đang tải về...")
    try:
        driver_path = ChromeDriverManager().install()
        
        # Fix: webdriver-manager có thể trả về path sai, cần tìm chromedriver.exe
        if not driver_path.endswith('chromedriver.exe'):
            # Tìm chromedriver.exe trong thư mục chứa driver_path
            driver_dir = os.path.dirname(driver_path)
            # Tìm trong thư mục hiện tại và các thư mục con
            for root, dirs, files in os.walk(driver_dir):
                for file in files:
                    if file == 'chromedriver.exe':
                        driver_path = os.path.join(root, file)
                        break
                if driver_path.endswith('chromedriver.exe'):
                    break
        
        print(f"✅ Đã tải ChromeDriver: {driver_path}")
        return driver_path
    except Exception as e:
        print(f"❌ Lỗi tải ChromeDriver: {e}")
        # Thử tạo thư mục drivers và hướng dẫn
        drivers_dir = os.path.join(parent_dir, "drivers")
        if not os.path.exists(drivers_dir):
            os.makedirs(drivers_dir, exist_ok=True)
        print(f"\n💡 TIP: Bạn có thể tải chromedriver.exe thủ công về: {drivers_dir}")
        print("   Tải tại: https://googlechromelabs.github.io/chrome-for-testing/")
        raise

def get_chrome_version():
    """Lấy phiên bản Chrome hiện tại"""
    try:
        is_installed, chrome_path = check_chrome_installed()
        if not is_installed:
            return None
        
        # Lấy version từ Chrome
        result = subprocess.run(
            [chrome_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        version = result.stdout.strip().split()[-1]
        return version
    except Exception:
        return None

def auto_update_chrome():
    """Tự động mở Chrome để update hoặc tải Chrome mới"""
    print("\n" + "="*60)
    print("🔧 TỰ ĐỘNG KHẮC PHỤC LỖI CHROME")
    print("="*60)
    
    is_installed, chrome_path = check_chrome_installed()
    
    if is_installed:
        # Chrome đã cài, mở trang update
        print("✅ Đã phát hiện Chrome trên máy")
        version = get_chrome_version()
        if version:
            print(f"📌 Phiên bản hiện tại: {version}")
        
        print("\n🔄 Đang mở trang cập nhật Chrome...")
        print("📝 Chrome sẽ tự động kiểm tra và cập nhật phiên bản mới")
        print("⏳ Vui lòng đợi Chrome cập nhật xong rồi khởi động lại app này\n")
        
        try:
            # Mở Chrome với trang update
            subprocess.Popen([chrome_path, "chrome://settings/help"])
            print("✅ Đã mở Chrome Settings → About")
            print("💡 Hãy đợi Chrome update xong, sau đó đóng app này và chạy lại!")
            return True
        except Exception as e:
            print(f"⚠️ Không thể mở Chrome tự động: {e}")
            print("📖 Hãy mở Chrome thủ công: Menu (⋮) → Help → About Google Chrome")
            return False
    else:
        # Chrome chưa cài, tải về
        print("❌ Không tìm thấy Chrome trên máy")
        print("\n📥 Đang mở trang tải Chrome...")
        
        try:
            chrome_download_url = "https://www.google.com/chrome/"
            webbrowser.open(chrome_download_url)
            print(f"✅ Đã mở trình duyệt tại: {chrome_download_url}")
            print("\n📝 HƯỚNG DẪN:")
            print("   1. Tải và cài đặt Google Chrome")
            print("   2. Khởi động lại máy tính (nếu cần)")
            print("   3. Chạy lại ứng dụng này")
            return True
        except Exception as e:
            print(f"⚠️ Không thể mở trình duyệt: {e}")
            print("📖 Hãy tải Chrome thủ công tại: https://www.google.com/chrome/")
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
    """Đọc file cấu hình auto_config.json"""
    global config
    # Đảm bảo luôn lấy file config trong thư mục automation
    config_file = os.path.join(os.path.dirname(__file__), "auto_config.json")

    if not os.path.exists(config_file):
        print("❌ Không tìm thấy file automation/auto_config.json!")
        return False

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Kiểm tra thông tin bắt buộc
        student_id = config['login_info']['student_id']
        password = config['login_info']['password']
        
        if not student_id or not password:
            print("❌ Thông tin đăng nhập không hợp lệ!")
            return False
            
        print("✅ Đã load config thành công!")
        print(f"👤 Mã sinh viên: {student_id}")
        print(f"🔒 Mật khẩu: {'*' * len(password)}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi đọc file config: {e}")
        return False

def setup_chrome_driver():
    """Thiết lập Chrome driver với auto-update khi gặp lỗi"""
    global driver
    max_retries = 2
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            chrome_options = Options()
            
            if USE_EXISTING_CHROME:
                # KẾT NỐI VÀO CHROME ĐANG MỞ
                print("🔧 Đang kết nối vào Chrome đang mở...")
                print(f"📡 Cổng debug: {DEBUGGING_PORT}")
                
                chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{DEBUGGING_PORT}")
                
                # Lấy đường dẫn ChromeDriver
                driver_path = get_chromedriver_path()
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                print("✅ Đã kết nối vào Chrome đang mở!")
                print(f"🌐 URL hiện tại: {driver.current_url}")
                print(f"📄 Title hiện tại: {driver.title}")
                
            else:
                # MỞ CHROME MỚI (chế độ cũ)
                print("🔧 Đang khởi động Chrome mới...")
                
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Lấy đường dẫn ChromeDriver
                driver_path = get_chromedriver_path()
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
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
                
                print(f"✅ Chrome driver đã sẵn sàng! [{window_title}]")
            
            return True
            
        except (AttributeError, TypeError) as e:
            # Lỗi liên quan đến phiên bản Chrome không tương thích
            if "'NoneType' object has no attribute 'split'" in str(e) or "split" in str(e):
                retry_count += 1
                print(f"❌ Lỗi kết nối Chrome: {e}")
                print(f"🔄 Đang thử lại lần {retry_count}/{max_retries}...")
                
                if retry_count < max_retries:
                    print("🧹 Đang xóa cache ChromeDriver cũ...")
                    try:
                        # Xóa cache webdriver-manager
                        cache_path = os.path.expanduser("~/.wdm")
                        if os.path.exists(cache_path):
                            shutil.rmtree(cache_path)
                            print("✅ Đã xóa cache cũ")
                    except Exception as cache_error:
                        print(f"⚠️ Không thể xóa cache: {cache_error}")
                    
                    print("📥 Đang tải ChromeDriver phiên bản mới nhất...")
                    time.sleep(2)
                    continue
                else:
                    print("\n" + "="*60)
                    print("❌ LỖI: Không thể khởi tạo ChromeDriver sau nhiều lần thử")
                    print("="*60)
                    print("\n💡 NGUYÊN NHÂN CÓ THỂ:")
                    print("   1. Phiên bản Chrome của bạn quá cũ hoặc quá mới")
                    print("   2. ChromeDriver không tương thích với Chrome hiện tại")
                    print("   3. Lỗi kết nối mạng khi tải ChromeDriver")
                    print("="*60)
                    
                    # Tự động mở Chrome update
                    auto_update_chrome()
                    
                    print("\n⏸️  Ứng dụng sẽ tạm dừng để bạn update Chrome...")
                    print("💡 Sau khi update xong, hãy đóng app này và chạy lại!")
                    print("="*60)
                    
                    # Đợi user đọc hướng dẫn
                    safe_input("\n👉 Nhấn Enter để thoát...")
                    return False
                    
        except Exception as e:
            print(f"❌ Lỗi kết nối Chrome: {e}")
            if USE_EXISTING_CHROME:
                print("\n💡 HƯỚNG DẪN:")
                print("- Đảm bảo Chrome đã được mở với debugging port 9222")
                print("- Hoặc chạy lại từ GUI để tự động mở Chrome")
            else:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"🔄 Đang thử lại lần {retry_count}/{max_retries}...")
                    time.sleep(2)
                    continue
            return False
    
    return False

def take_screenshot(step_name, check_title=True):
    """
    Chụp ảnh màn hình
    check_title=True: Chỉ chụp khi title ĐÚNG
    check_title=False: Chụp luôn không kiểm tra title (dùng cho trường hợp đặc biệt)
    """
    global driver
    if not driver:
        return
    
    # Kiểm tra title nếu cần
    if check_title:
        try:
            current_title = driver.title.strip()
            valid_titles = [
                "Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An",
                "Đăng nhập SSO – UniSoft"
            ]
            
            if current_title not in valid_titles:
                print(f"⚠️ Bỏ qua chụp ảnh - Title không hợp lệ: '{current_title}'")
                return
        except Exception as e:
            print(f"⚠️ Không thể kiểm tra title: {e}")
            return
        
    try:
        # Tạo thư mục screenshots nếu chưa có
        screenshots_dir = os.path.join(os.path.dirname(__file__), "..", "screenshots")
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{step_name}.png"
        filepath = os.path.join(screenshots_dir, filename)
        
        driver.save_screenshot(filepath)
        print(f"📷 Đã chụp ảnh: {filename}")
        
    except Exception as e:
        print(f"⚠️ Lỗi chụp ảnh: {e}")

def wait_for_correct_title():
    """
    Reload trang liên tục cho đến khi title ĐÚNG
    CHỈ CÓ 2 TITLE ĐÚNG:
    1. 'Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An'
    2. 'Đăng nhập SSO – UniSoft'
    TẤT CẢ TITLE KHÁC ĐỀU SAI - PHẢI RELOAD VÔ HẠN
    """
    global driver
    
    valid_titles = [
        "Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An",
        "Đăng nhập SSO – UniSoft"
    ]
    reload_count = 0
    
    print("🔄 BẮT ĐẦU KIỂM TRA TITLE - CHỈ CHẤP NHẬN 2 TITLE HỢP LỆ")
    for i, title in enumerate(valid_titles, 1):
        print(f"🎯 Title hợp lệ {i}: '{title}'")
    print("❌ Title 'sinhvien.ulsa.edu.vn' là LỖI - sẽ reload vô hạn")
    print("❌ TẤT CẢ title khác đều SAI và sẽ reload vô hạn")
    print("⚡ Tối ưu hóa: Kiểm tra liên tục cho đến khi thành công")
    print("-" * 60)
    
    while True:  # Vòng lặp vô hạn
        try:
            # Lấy title hiện tại
            current_title = driver.title.strip()
            current_url = driver.current_url
            reload_count += 1
            
            print(f"\n🔍 Lần kiểm tra {reload_count}:")
            print(f"   📄 Title hiện tại: '{current_title}'")
            print(f"   🔗 URL: {current_url}")
            
            # KIỂM TRA NẾU ĐÃ CÓ TITLE ĐÚNG - DỪNG LẠI
            if current_title in valid_titles:
                print("🎉 TITLE CHÍNH XÁC ĐÃ XUẤT HIỆN!")
                print(f"✅ Title đúng: '{current_title}'")
                take_screenshot("correct_title_found")
                return True
            
            # NẾU TITLE KHÁC - RELOAD NGAY
            else:
                print(f"❌ Title SAI: '{current_title}'")
                print(f"🎯 Cần một trong các title hợp lệ (xem trên)")
                print(f"🔄 Đang reload lần {reload_count}...")
                driver.refresh()
                
                # Đợi ngắn để tối ưu thời gian
                time.sleep(1)
                
                # Đợi trang load xong nhanh
                try:
                    WebDriverWait(driver, 5).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                except:
                    pass  # Không chờ quá lâu
            
            # Hiển thị tiến trình mỗi 10 lần
            if reload_count % 10 == 0:
                print(f"📊 Đã reload {reload_count} lần, tiếp tục kiểm tra...")
            
        except Exception as e:
            print(f"❌ Lỗi khi kiểm tra title: {e}")
            print("🔄 Thử reload trang...")
            try:
                driver.refresh()
                time.sleep(2)
            except:
                print("❌ Không thể reload trang!")
                return False

def auto_login():
    """Thực hiện đăng nhập tự động sau khi title đã đúng"""
    global driver, config
    
    try:
        print("\n🔐 BẮT ĐẦU QUÁ TRÌNH ĐĂNG NHẬP TỰ ĐỘNG")
        print("-" * 50)
        
        # Lấy thông tin đăng nhập từ config
        student_id = config['login_info']['student_id']
        password = config['login_info']['password']
        
        print(f"👤 Sử dụng mã sinh viên: {student_id}")
        
        # Chờ form đăng nhập xuất hiện
        print("⏳ Đang chờ form đăng nhập xuất hiện...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        # Tìm các field đăng nhập bằng hàm helper
        print("🔍 Đang tìm các field đăng nhập...")
        
        username_field = find_login_element("username")
        if not username_field:
            print("❌ Không tìm thấy username field!")
            return False
        print("✅ Đã tìm thấy username field")
        
        password_field = find_login_element("password")
        if not password_field:
            print("❌ Không tìm thấy password field!")
            return False
        print("✅ Đã tìm thấy password field")
        
        login_button = find_login_element("login_button")
        if not login_button:
            print("❌ Không tìm thấy login button!")
            return False
        print("✅ Đã tìm thấy login button")
        
        # Điền thông tin đăng nhập
        print("✏️ Đang điền thông tin đăng nhập...")
        
        username_field.clear()
        username_field.send_keys(student_id)
        print("✅ Đã điền mã sinh viên")
        
        password_field.clear()
        password_field.send_keys(password)
        print("✅ Đã điền mật khẩu")
        
        # Chụp ảnh trước khi submit
        take_screenshot("before_login_submit")
        
        # BƯỚC QUAN TRỌNG: BẤM NÚT ĐĂNG NHẬP TRƯỚC
        print("🔘 Tìm và bấm nút đăng nhập...")
        login_button = find_login_element("login_button")
        
        if login_button:
            try:
                # Bấm nút đăng nhập
                print("📤 Đang bấm nút đăng nhập...")
                driver.execute_script("arguments[0].click();", login_button)
                print("✅ Đã bấm nút đăng nhập thành công")
                
                # Chờ trang xử lý
                time.sleep(3)
                wait_for_page_load_complete()
                
                # KHÔNG KIỂM TRA TITLE SAU KHI ĐĂNG NHẬP - ĐỂ WEB TỰ CHUYỂN HƯỚNG
                print("✅ Đã đăng nhập, chờ web tự chuyển hướng...")
                print("⏸️ KHÔNG reload để tránh bị chuyển về ChangePassword.aspx")
                
                # Chụp ảnh sau khi bấm
                take_screenshot("after_login_click")
                
            except Exception as e:
                print(f"❌ Lỗi khi bấm nút đăng nhập: {e}")
                # Thử cách khác
                try:
                    login_button.click()
                    print("✅ Đã bấm nút đăng nhập (cách 2)")
                    time.sleep(3)
                    wait_for_page_load_complete()
                except:
                    print("❌ Không thể bấm nút đăng nhập")
                    return False
        else:
            print("❌ Không tìm thấy nút đăng nhập")
            return False
        
        # Kiểm tra kết quả sau khi bấm đăng nhập - CHỈ KIỂM TRA URL, KHÔNG KIỂM TRA TITLE
        current_url = driver.current_url
        print(f"📍 URL sau khi đăng nhập: {current_url}")
        print("🔍 CHỈ KIỂM TRA URL - KHÔNG KIỂM TRA TITLE ở bước này")
        
        target_success_urls = ["SinhVien.aspx", "ChangePassword.aspx"]
        target_course_url = "http://sinhvien.ulsa.edu.vn/wfrmDangKyLopTinChiB1.aspx?Chuyen_nganh=1"
        
        # RELOAD CHO ĐẾN KHI URL = SinhVien.aspx?Chuyen_nganh=1 HOẶC ChangePassword.aspx
        reload_count = 0
        url_matched = any(url in current_url for url in target_success_urls)
        
        while not url_matched:  # ← KHÔNG giới hạn - reload vô hạn
            reload_count += 1
            print(f"\n🔄 Reload lần {reload_count}:")
            print(f"   ❌ URL hiện tại: {current_url}")
            print(f"   🎯 URL cần đạt (1 trong 2):")
            print(f"      - SinhVien.aspx")
            print(f"      - ChangePassword.aspx")
            
            # Reload trang
            try:
                driver.set_page_load_timeout(25)
                driver.refresh()
            except TimeoutException:
                print("   ⚠️ Reload bị timeout, vẫn tiếp tục kiểm tra URL hiện tại...")
            time.sleep(2)
            wait_for_page_load_complete()
            
            # Kiểm tra lại URL
            current_url = driver.current_url
            print(f"   📍 URL sau reload: {current_url}")
            
            # Kiểm tra có khớp với 1 trong 2 URL không
            url_matched = any(url in current_url for url in target_success_urls)
            
            if reload_count % 10 == 0:
                print(f"📊 Đã reload {reload_count} lần, tiếp tục...")
                take_screenshot(f"login_reload_{reload_count}")

        if not url_matched:
            print("⚠️ LỖI: Không bắt được URL đích sau nhiều lần reload!")
            print(f"⏹️ Vẫn ở trang: {current_url}")
            print("❌ Dừng lại - KHÔNG ĐƯỢC nhảy sang B1 khi vẫn ở Login.aspx")
            print("💡 Cần chờ đến khi nó tự chuyển sang SinhVien.aspx hoặc ChangePassword.aspx")
            return False
        
        # ✅ URL ĐÃ ĐÚNG (1 trong 2) - CÓ THỂ CHUYỂN SANG B1
        matched_url = next((url for url in target_success_urls if url in current_url), "Unknown")
        print(f"✅ URL CHÍNH XÁC: {current_url}")
        print(f"✅ Khớp với: {matched_url}")
        print(f"📚 Bây giờ mới chuyển sang trang chọn lớp B1: {target_course_url}")
        if not force_redirect_to_b1(target_course_url, "auto_login"):
            return False
        
        print("✅ Đã chuyển sang trang B1 - KHÔNG KIỂM TRA TITLE")
        take_screenshot("switched_to_b1_from_login")
        
        # Bắt đầu xử lý trang B1 và B2
        print("\n🔄 CHUYỂN SANG GIAI ĐOẠN CHỌN LỚP TÍN CHỈ")
        course_selection_success = handle_course_selection_pages()
        
        if course_selection_success:
            print("🎉 HOÀN THÀNH TOÀN BỘ QUÁ TRÌNH ĐĂNG KÝ!")
            take_screenshot("final_success")
            return True
        else:
            print("❌ Lỗi trong quá trình chọn lớp tín chỉ")
            take_screenshot("course_selection_error")
            return False
    
    except Exception as e:
        print(f"❌ Lỗi trong quá trình đăng nhập: {e}")
        take_screenshot("login_error")
        return False

def retry_login_with_reload_button(username_field, password_field, student_id, password):
    """
    STRATEGY MỚI: Không submit form mà bấm "Reload this page" liên tục
    cho đến khi URL chuyển thành http://sinhvien.ulsa.edu.vn/SinhVien.aspx?Chuyen_nganh=1
    """
    global driver
    
    target_url = "http://sinhvien.ulsa.edu.vn/SinhVien.aspx?Chuyen_nganh=1"
    target_course_url = "http://sinhvien.ulsa.edu.vn/wfrmDangKyLopTinChiB1.aspx?Chuyen_nganh=1"
    reload_count = 0
    wait_time = 2  # Thời gian chờ giữa mỗi lần reload
    
    print("\n🔄 BẮT ĐẦU STRATEGY MỚI: RELOAD THIS PAGE")
    print(f"🎯 Mục tiêu URL: {target_url}")
    print(f"📚 URL chọn lớp: {target_course_url}")
    print(f"⏰ Thời gian chờ: {wait_time}s giữa mỗi lần reload")
    print(f"🔄 Phương pháp: Bấm 'Reload this page' liên tục")
    print("📝 Lưu ý: KHÔNG submit form, chỉ reload trang")
    print("-" * 70)
    
    # Bước 1: Điền thông tin đăng nhập một lần duy nhất
    try:
        print("✏️ Điền thông tin đăng nhập một lần duy nhất...")
        username_field.clear()
        username_field.send_keys(student_id)
        print("✅ Đã điền mã sinh viên")
        
        password_field.clear()
        password_field.send_keys(password)
        print("✅ Đã điền mật khẩu")
        
        # Chụp ảnh sau khi điền thông tin
        take_screenshot("credentials_filled")
        
    except Exception as e:
        print(f"❌ Lỗi khi điền thông tin: {e}")
        return False
    
    # Bước 2: Bắt đầu vòng lặp reload page
    while True:  # Vòng lặp vô hạn
        reload_count += 1
        
        try:
            print(f"\n🔄 Lần reload thứ {reload_count}:")
            
            # Kiểm tra URL hiện tại trước khi reload
            current_url = driver.current_url
            print(f"📍 URL hiện tại: {current_url}")
            
            # KIỂM TRA NẾU BỊ CHUYỂN SANG TRANG ĐỔI MẬT KHẨU - Bỏ QUA VÀ CHUYỂN THẲNG SANG B1
            if "ChangePassword.aspx" in current_url:
                print("⚠️ Hệ thống yêu cầu đổi mật khẩu - Bỏ QUA và chuyển thẳng sang B1")
                print(f"✅ URL hiện tại: {current_url}")
                
                # Chuyển đến trang chọn lớp NGAY LẬP TỨC - KHÔNG RELOAD
                print(f"📚 Đang chuyển đến trang chọn lớp: {target_course_url}")
                if not force_redirect_to_b1(target_course_url, "retry_from_changepassword"):
                    return False
                
                print("✅ Đã chuyển sang trang B1 - SẼ BỎ QUA KIỂM TRA TITLE LẦN ĐẦU")
                
                take_screenshot("switched_to_b1_from_changepassword")
                
                # Bắt đầu xử lý trang B1 và B2 - BỎ QUA KIỂM TRA TITLE LẦN ĐẦU
                print("\n🔄 CHUYỂN SANG GIAI ĐOẠN CHỌN LỚP TÍN CHỈ")
                
                # Xử lý B1 với skip_initial_title_check=True
                target_title = "Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An"
                wrong_title = "sinhvien.ulsa.edu.vn"
                success_b1 = handle_page_b1(target_title, wrong_title, skip_initial_title_check=True)
                
                if not success_b1:
                    print("❌ Lỗi tại trang B1")
                    take_screenshot("course_selection_error")
                    return False
                
                # Xử lý B2
                success_b2 = handle_page_b2(target_title, wrong_title)
                if not success_b2:
                    print("❌ Lỗi tại trang B2")
                    take_screenshot("course_selection_error")
                    return False
                
                # Chờ B3
                b3_ready = wait_for_b3_title_and_url()
                if not b3_ready:
                    print("❌ Không thể vào đúng trang B3!")
                    return False
                
                if success_b1 and success_b2 and b3_ready:
                    print("🎉 HOÀN THÀNH TOÀN BỘ QUÁ TRÌNH ĐĂNG KÝ!")
                    take_screenshot("final_success")
                    return True
                else:
                    print("❌ Lỗi trong quá trình chọn lớp tín chỉ")
                    take_screenshot("course_selection_error")
                    return False
            
            # KIỂM TRA NẾU ĐÃ VÀO SinhVien.aspx - CHUYỂN SANG B1 NGAY
            if "SinhVien.aspx" in current_url:
                print("🎉 ĐÃ VÀO SinhVien.aspx - CHUYỂN SANG B1 NGAY!")
                print(f"✅ URL hiện tại: {current_url}")
                
                # Chuyển đến trang chọn lớp NGAY LẬP TỨC - KHÔNG RELOAD
                print(f"📚 Đang chuyển đến trang chọn lớp: {target_course_url}")
                if not force_redirect_to_b1(target_course_url, "retry_from_sinhvien"):
                    return False
                
                print("✅ Đã chuyển sang trang B1 - SẼ BỎ QUA KIỂM TRA TITLE LẦN ĐẦU")
                
                take_screenshot("switched_to_b1_from_sinhvien")
                
                # Bắt đầu xử lý trang B1 và B2 - BỎ QUA KIỂM TRA TITLE LẦN ĐẦU
                print("\n🔄 CHUYỂN SANG GIAI ĐOẠN CHỌN LỚP TÍN CHỈ")
                
                # Xử lý B1 với skip_initial_title_check=True
                target_title = "Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An"
                wrong_title = "sinhvien.ulsa.edu.vn"
                success_b1 = handle_page_b1(target_title, wrong_title, skip_initial_title_check=True)
                
                if not success_b1:
                    print("❌ Lỗi tại trang B1")
                    take_screenshot("course_selection_error")
                    return False
                
                # Xử lý B2
                success_b2 = handle_page_b2(target_title, wrong_title)
                if not success_b2:
                    print("❌ Lỗi tại trang B2")
                    take_screenshot("course_selection_error")
                    return False
                
                # Chờ B3
                b3_ready = wait_for_b3_title_and_url()
                if not b3_ready:
                    print("❌ Không thể vào đúng trang B3!")
                    return False
                
                if success_b1 and success_b2 and b3_ready:
                    print("🎉 HOÀN THÀNH TOÀN BỘ QUÁ TRÌNH ĐĂNG KÝ!")
                    take_screenshot("final_success")
                    return True
                else:
                    print("❌ Lỗi trong quá trình chọn lớp tín chỉ")
                    take_screenshot("course_selection_error")
                    return False
            
            # Nếu chưa vào được SinhVien.aspx - tiếp tục reload
            else:
                print("⚠️ Chưa vào được SinhVien.aspx - tiếp tục reload...")
                print(f"🎯 Đang chờ vào URL có chứa: SinhVien.aspx")
                
                # Bấm reload page
                print("🔄 Đang tìm và bấm nút 'Reload this page'...")
                reload_success = click_reload_page_button()
                
                if reload_success:
                    print("✅ Đã bấm reload page thành công")
                else:
                    print("⚠️ Không tìm thấy nút reload, thử F5...")
                    driver.refresh()
                
                # Chờ trang load
                print(f"⏳ Chờ {wait_time}s để trang load...")
                time.sleep(wait_time)
                
                # Chờ trang load hoàn toàn
                wait_for_page_load_complete()
                
                # KIỂM TRA TITLE SAU MỖI LẦN RELOAD
                print("🔍 Kiểm tra title sau reload...")
                check_and_reload_if_error(f"retry reload lần {reload_count}")
                
                # Chụp ảnh trạng thái sau reload
                take_screenshot(f"reload_attempt_{reload_count}")
            
            # Hiển thị thống kê mỗi 10 lần
            if reload_count % 10 == 0:
                print(f"\n📊 THỐNG KÊ: Đã reload {reload_count} lần, tiếp tục...")
            
            # Kiểm tra có thông báo lỗi không
            check_error_messages()
            
        except Exception as e:
            print(f"❌ Lỗi trong lần reload {reload_count}: {e}")
            
            # Thử recovery
            try:
                print("🔧 Thử recovery...")
                driver.refresh()
                wait_for_page_load_complete()
                time.sleep(2)
                
                # Kiểm tra nếu cần điền lại thông tin
                current_url = driver.current_url
                if "Login.aspx" in current_url:
                    print("🔄 Đã quay về trang login, thử điền lại thông tin...")
                    username_field = find_login_element("username")
                    password_field = find_login_element("password")
                    
                    if username_field and password_field:
                        username_field.clear()
                        username_field.send_keys(student_id)
                        password_field.clear()
                        password_field.send_keys(password)
                        print("✅ Đã điền lại thông tin")
                    else:
                        print("⚠️ Không thể tìm thấy form đăng nhập")
                
            except Exception as recovery_error:
                print(f"❌ Recovery thất bại: {recovery_error}")
                time.sleep(5)
            
            continue

def click_reload_page_button():
    """
    Tìm và bấm nút 'Reload this page' 
    Có thể là nút reload của browser hoặc nút trên trang web
    """
    global driver
    
    try:
        # Cách 1: Tìm nút reload bằng text
        reload_selectors = [
            # Text-based selectors
            (By.XPATH, "//button[contains(text(), 'Reload')]"),
            (By.XPATH, "//button[contains(text(), 'reload')]"),
            (By.XPATH, "//a[contains(text(), 'Reload')]"),
            (By.XPATH, "//a[contains(text(), 'reload')]"),
            (By.XPATH, "//span[contains(text(), 'Reload')]"),
            (By.XPATH, "//div[contains(text(), 'Reload')]"),
            
            # Vietnamese text
            (By.XPATH, "//button[contains(text(), 'Tải lại')]"),
            (By.XPATH, "//a[contains(text(), 'Tải lại')]"),
            (By.XPATH, "//button[contains(text(), 'Làm mới')]"),
            (By.XPATH, "//a[contains(text(), 'Làm mới')]"),
            
            # Common reload button classes/IDs
            (By.CLASS_NAME, "reload-button"),
            (By.CLASS_NAME, "refresh-button"),
            (By.ID, "reload"),
            (By.ID, "refresh"),
            (By.ID, "reload-page"),
            
            # Browser reload button (ít có thể click được)
            (By.CSS_SELECTOR, "[data-testid='reload']"),
            (By.CSS_SELECTOR, "[title*='Reload']"),
            (By.CSS_SELECTOR, "[aria-label*='Reload']"),
        ]
        
        print("🔍 Đang tìm nút reload...")
        
        for by_type, selector in reload_selectors:
            try:
                reload_button = driver.find_element(by_type, selector)
                if reload_button and reload_button.is_displayed():
                    print(f"✅ Tìm thấy nút reload: {selector}")
                    
                    # Thử click bằng nhiều cách
                    try:
                        # Cách 1: Click thường
                        reload_button.click()
                        print("✅ Đã click nút reload (click thường)")
                        return True
                    except:
                        try:
                            # Cách 2: JavaScript click
                            driver.execute_script("arguments[0].click();", reload_button)
                            print("✅ Đã click nút reload (JavaScript)")
                            return True
                        except:
                            try:
                                # Cách 3: Action chains
                                from selenium.webdriver.common.action_chains import ActionChains
                                actions = ActionChains(driver)
                                actions.move_to_element(reload_button).click().perform()
                                print("✅ Đã click nút reload (Action chains)")
                                return True
                            except:
                                continue
                        
            except:
                continue
        
        # Cách 2: Thử tìm nút refresh của browser
        print("🔍 Thử tìm nút refresh của browser...")
        try:
            # Sử dụng keyboard shortcut F5
            from selenium.webdriver.common.keys import Keys
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.F5)
            print("✅ Đã bấm F5 để reload")
            return True
        except:
            pass
        
        # Cách 3: Thử right-click và tìm context menu
        print("🔍 Thử right-click để tìm reload option...")
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            
            # Right-click trên trang
            body = driver.find_element(By.TAG_NAME, "body")
            actions.context_click(body).perform()
            
            time.sleep(1)
            
            # Tìm option reload trong context menu
            reload_options = [
                (By.XPATH, "//div[contains(text(), 'Reload')]"),
                (By.XPATH, "//span[contains(text(), 'Reload')]"),
                (By.XPATH, "//div[contains(text(), 'Refresh')]"),
                (By.XPATH, "//span[contains(text(), 'Refresh')]"),
            ]
            
            for by_type, selector in reload_options:
                try:
                    reload_option = driver.find_element(by_type, selector)
                    if reload_option.is_displayed():
                        reload_option.click()
                        print("✅ Đã bấm reload từ context menu")
                        return True
                except:
                    continue
            
            # Đóng context menu nếu không tìm thấy
            body.send_keys(Keys.ESCAPE)
            
        except:
            pass
        
        print("⚠️ Không tìm thấy nút reload")
        return False
        
    except Exception as e:
        print(f"❌ Lỗi khi tìm nút reload: {e}")
        return False

def check_error_messages():
    """Kiểm tra có thông báo lỗi nào không"""
    global driver
    
    try:
        # Kiểm tra thông báo lỗi đăng nhập
        error_selectors = [
            (By.ID, "lblThong_bao"),
            (By.CLASS_NAME, "error-message"),
            (By.CLASS_NAME, "alert-danger"),
            (By.XPATH, "//div[contains(@class, 'error')]"),
            (By.XPATH, "//span[contains(@class, 'error')]"),
        ]
        
        for by_type, selector in error_selectors:
            try:
                error_element = driver.find_element(by_type, selector)
                if error_element and error_element.text.strip():
                    error_msg = error_element.text.strip()
                    print(f"⚠️ Thông báo: {error_msg}")
                    
                    # Kiểm tra lỗi nghiêm trọng
                    if any(keyword in error_msg.lower() for keyword in ["sai", "incorrect", "invalid", "wrong", "locked"]):
                        print("❌ Phát hiện lỗi nghiêm trọng!")
                        take_screenshot("error_detected")
                        return False
                    
            except:
                continue
                
        return True
        
    except Exception as e:
        print(f"⚠️ Lỗi khi kiểm tra error messages: {e}")
        return True


def force_redirect_to_b1(target_course_url, source_step=""):
    """
    Cưỡng bức chuyển hướng sang B1 ngay cả khi trang trung gian đang load dở.
    Trả về True nếu đã vào B1/B2/B3, False nếu thất bại.
    """
    global driver

    success_markers = [
        "wfrmDangKyLopTinChiB1.aspx",
        "wfrmDangKyLopTinChiB2.aspx",
        "wfrmDangKyLopTinChiB3.aspx",
    ]

    for attempt in range(1, 5):
        try:
            current_url = driver.current_url
        except Exception:
            current_url = ""

        if any(marker in current_url for marker in success_markers):
            print(f"✅ Đã ở trang đăng ký (attempt {attempt}): {current_url}")
            return True

        print(f"🚀 [{source_step}] Ép chuyển B1 lần {attempt}: {target_course_url}")

        try:
            driver.set_page_load_timeout(12)
            driver.get(target_course_url)
        except TimeoutException:
            print("⚠️ driver.get(B1) bị timeout, thử JavaScript redirect...")
        except Exception as nav_err:
            print(f"⚠️ Lỗi driver.get(B1): {nav_err}")

        time.sleep(1.2)
        try:
            after_get_url = driver.current_url
        except Exception:
            after_get_url = ""

        if any(marker in after_get_url for marker in success_markers):
            print(f"✅ Chuyển hướng thành công qua driver.get: {after_get_url}")
            return True

        try:
            driver.execute_script("window.location.href = arguments[0];", target_course_url)
            time.sleep(1.2)
            after_js_url = driver.current_url
            if any(marker in after_js_url for marker in success_markers):
                print(f"✅ Chuyển hướng thành công qua JS: {after_js_url}")
                return True
        except Exception as js_err:
            print(f"⚠️ Lỗi JS redirect B1: {js_err}")

    print("❌ Không thể chuyển sang B1 sau nhiều lần thử")
    return False



def handle_f5_refresh_method(current_url, target_url, target_course_url):
    """
    Xử lý phương pháp F5 refresh và thông báo của browser
    """
    global driver
    
    print("\n🔄 BẮT ĐẦU PHƯƠNG PHÁP F5 REFRESH")
    print(f"📍 URL hiện tại: {current_url}")
    print("-" * 50)
    
    max_f5_attempts = 20  # Giới hạn số lần F5 để tránh vô hạn
    f5_count = 0
    
    while f5_count < max_f5_attempts:
        f5_count += 1
        
        try:
            print(f"\n🔄 F5 lần thứ {f5_count}:")
            
            # Bấm F5 (refresh trang)
            print("⌨️ Đang bấm F5...")
            driver.refresh()
            
            # Chờ một chút để thông báo xuất hiện
            time.sleep(2)
            
            # Kiểm tra có thông báo refresh không
            refresh_dialog_handled = handle_refresh_dialog()
            
            if refresh_dialog_handled:
                print("✅ Đã xử lý thông báo refresh, chờ trang load...")
            else:
                print("⚠️ Không có thông báo refresh")
            
            # Chờ trang load hoàn toàn
            wait_for_page_load_complete()
            
            # Kiểm tra URL sau F5
            new_url = driver.current_url
            print(f"📍 URL sau F5: {new_url}")
            
            # Kiểm tra nếu đã thành công
            if new_url == target_url:
                print("🎉 F5 THÀNH CÔNG - ĐĂNG NHẬP THÀNH CÔNG!")
                print(f"✅ Đã đạt được URL mục tiêu: {target_url}")
                
                # Chuyển thẳng đến trang chọn lớp
                print(f"📚 Đang chuyển đến trang chọn lớp: {target_course_url}")
                if not force_redirect_to_b1(target_course_url, "f5_success"):
                    return False
                
                take_screenshot("f5_success")
                return True
            
            elif "SinhVien.aspx" in new_url:
                print("🟡 F5 đã vào SinhVien.aspx, thử navigate đến URL mục tiêu...")
                driver.get(target_url)
                wait_for_page_load_complete()
                
                final_url = driver.current_url
                if final_url == target_url:
                    print("🎉 NAVIGATE THÀNH CÔNG!")
                    
                    # Chuyển thẳng đến trang chọn lớp
                    print(f"📚 Đang chuyển đến trang chọn lớp: {target_course_url}")
                    if not force_redirect_to_b1(target_course_url, "f5_navigate_success"):
                        return False
                    
                    take_screenshot("f5_navigate_success")
                    return True
                else:
                    print(f"⚠️ Navigate thất bại, tiếp tục F5...")
            
            elif "Login.aspx" in new_url:
                print("⚠️ F5 đưa về trang login - có thể cần đăng nhập lại")
                if not refresh_dialog_handled:
                    # Nếu không có thông báo refresh, có thể cần đăng nhập lại
                    print("❌ Không có thông báo refresh - có thể cần đăng nhập lại")
                    return False
                else:
                    print("🔄 Có thông báo refresh - tiếp tục F5...")
            
            else:
                print(f"🤔 URL bất thường sau F5: {new_url}")
                print("🔄 Tiếp tục F5...")
            
            # Chụp ảnh trạng thái sau F5
            take_screenshot(f"f5_attempt_{f5_count}")
            
            # Chờ một chút trước lần F5 tiếp theo
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Lỗi trong lần F5 {f5_count}: {e}")
            time.sleep(2)
            continue
    
    print(f"\n⚠️ Đã F5 {max_f5_attempts} lần nhưng chưa thành công")
    return False

def handle_refresh_dialog():
    """
    Xử lý thông báo refresh của browser:
    'Trang mà bạn đang tìm sử dụng thông tin bạn đã nhập vào. 
    Việc quay lại trang đó có thể lặp lại bất kỳ tác vụ nào bạn đã thực hiện. 
    Bạn có muốn tiếp tục không?'
    """
    global driver
    
    try:
        print("🔍 Đang kiểm tra thông báo refresh...")
        
        # Chờ thông báo xuất hiện (có thể là alert hoặc confirm dialog)
        try:
            # Kiểm tra alert
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"📢 Tìm thấy thông báo: {alert_text}")
            
            # Kiểm tra nếu là thông báo refresh
            refresh_keywords = ["trang mà bạn đang tìm", "thông tin bạn đã nhập", "tiếp tục", "quay lại"]
            if any(keyword in alert_text.lower() for keyword in refresh_keywords):
                print("✅ Đây là thông báo refresh - bấm Accept/Tiếp tục")
                alert.accept()  # Bấm OK/Tiếp tục
                print("✅ Đã bấm Tiếp tục")
                return True
            else:
                print("⚠️ Thông báo khác - bấm Accept")
                alert.accept()
                return True
                
        except:
            # Không có alert, có thể là confirm dialog hoặc không có gì
            print("⚠️ Không tìm thấy alert dialog")
            
            # Thử tìm confirm dialog bằng JavaScript
            try:
                result = driver.execute_script("""
                    // Thử trigger confirm nếu có
                    if (window.confirm) {
                        return 'confirm_available';
                    }
                    return 'no_confirm';
                """)
                print(f"🔍 Kết quả kiểm tra confirm: {result}")
            except:
                pass
            
            return False
            
    except Exception as e:
        print(f"⚠️ Lỗi khi xử lý thông báo refresh: {e}")
        return False

def check_and_reload_if_error(step_name):
    """
    Kiểm tra title, nếu KHÔNG PHẢI title đúng thì reload vô hạn
    CHỈ CÓ 2 TITLE ĐÚNG:
    1. 'Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An'
    2. 'Đăng nhập SSO – UniSoft'
    TITLE 'sinhvien.ulsa.edu.vn' là LỖI/SẬP - PHẢI RELOAD
    
    NẾU GẶP TIMEOUT: Đợi rồi thử lại, KHÔNG crash
    """
    global driver
    
    valid_titles = [
        "Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An",
        "Đăng nhập SSO – UniSoft"
    ]
    
    reload_count = 0
    consecutive_errors = 0
    
    while True:  # Vòng lặp vô hạn
        try:
            # Lấy title hiện tại
            current_title = driver.title.strip()
            
            if reload_count == 0:
                print(f"📄 [{step_name}] Title hiện tại: '{current_title}'")
            
            # Nếu title ĐÚNG - dừng lại
            if current_title in valid_titles:
                print(f"✅ [{step_name}] Title ĐÚNG: '{current_title}'")
                return True
            
            # Title SAI - reload
            reload_count += 1
            if reload_count == 1:
                print(f"❌ [{step_name}] Title SAI: '{current_title}'")
                print(f"🎯 [{step_name}] Cần một trong các title hợp lệ")
            
            print(f"🔄 Đang reload trang lần {reload_count}...")
            
            try:
                # Reload với xử lý timeout
                driver.set_page_load_timeout(60)  # Timeout 60 giây
                driver.refresh()
                consecutive_errors = 0  # Reset error counter khi thành công
            except Exception as refresh_error:
                consecutive_errors += 1
                print(f"⚠️ Lỗi khi reload (lần {consecutive_errors}): {str(refresh_error)[:80]}")
                print(f"💤 Đợi 5 giây rồi thử lại...")
                time.sleep(5)
                
                # Nếu lỗi quá nhiều, thử tạo driver mới
                if consecutive_errors >= 3:
                    print(f"⚠️ Quá nhiều lỗi liên tiếp, đợi thêm 10 giây...")
                    time.sleep(10)
                    consecutive_errors = 0
                
                continue  # Thử lại từ đầu vòng lặp
            
            # Đợi 2 giây cho trang load
            time.sleep(2)
            
            # Thử chờ trang load hoàn toàn (có xử lý timeout)
            try:
                wait_for_page_load_complete()
            except Exception as wait_error:
                print(f"⚠️ Timeout khi chờ trang load: {str(wait_error)[:80]}")
                print(f"💡 Bỏ qua và kiểm tra title tiếp...")
            
            # Log tiến trình mỗi 10 lần
            if reload_count % 10 == 0:
                print(f"📊 [{step_name}] Đã reload {reload_count} lần, tiếp tục...")
                take_screenshot(f"reload_{reload_count}_{step_name.replace(' ', '_')}")
        
        except Exception as e:
            consecutive_errors += 1
            print(f"⚠️ Lỗi ngoài dự kiến (lần {consecutive_errors}): {str(e)[:100]}")
            print(f"💤 Đợi 5 giây rồi thử lại...")
            time.sleep(5)
            
            if consecutive_errors >= 5:
                print(f"⚠️ Quá nhiều lỗi, đợi 15 giây...")
                time.sleep(15)
                consecutive_errors = 0

def wait_for_page_load_complete():
    """Chờ trang load hoàn toàn trước khi tiếp tục"""
    global driver
    
    try:
        print("⏳ Đang chờ trang load hoàn toàn...")
        
        # Chờ document.readyState = 'complete'
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Chờ thêm jQuery nếu có
        try:
            WebDriverWait(driver, 5).until(
                lambda d: d.execute_script("return typeof jQuery === 'undefined' || jQuery.active === 0")
            )
        except:
            pass  # Không có jQuery thì bỏ qua
        
        print("✅ Trang đã load hoàn toàn")
        
    except Exception as e:
        print(f"⚠️ Timeout chờ trang load hoàn toàn: {e}")
        print("⚠️ Tiếp tục với trang hiện tại...")

def find_login_element(element_type):
    """Tìm các element đăng nhập với nhiều selector"""
    global driver
    
    if element_type == "username":
        selectors = [
            (By.ID, "txtTenDangNhap"),
            (By.NAME, "txtTenDangNhap"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input[name*='user']")
        ]
    elif element_type == "password":
        selectors = [
            (By.ID, "txtMatKhau"),
            (By.NAME, "txtMatKhau"), 
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input[name*='pass']")
        ]
    elif element_type == "login_button":
        selectors = [
            (By.ID, "btnDangNhap"),
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//input[@value='Đăng nhập']")
        ]
    else:
        return None
    
    for by_type, selector in selectors:
        try:
            element = driver.find_element(by_type, selector)
            if element:
                return element
        except:
            continue
    
    return None

def handle_course_selection_pages():
    """
    Xử lý trang B1 và B2 với title checking và course selection
    """
    global driver, config
    
    target_title = "Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An"
    wrong_title = "sinhvien.ulsa.edu.vn"
    
    print("\n📚 BẮT ĐẦU QUÁ TRÌNH CHỌN LỚP TÍN CHỈ")
    print("=" * 70)
    
    # Bước 1: Xử lý trang B1 (chọn học phần)
    print("\n🔸 BƯỚC 1: XỬ LÝ TRANG B1 - CHỌN HỌC PHẦN")
    success_b1 = handle_page_b1(target_title, wrong_title, skip_initial_title_check=False)
    
    if not success_b1:
        print("❌ Lỗi tại trang B1")
        return False
    
    # Bước 2: Xử lý trang B2 (chọn lớp tín chỉ) 
    print("\n🔸 BƯỚC 2: XỬ LÝ TRANG B2 - CHỌN LỚP TÍN CHỈ")
    success_b2 = handle_page_b2(target_title, wrong_title)
    
    if not success_b2:
        print("❌ Lỗi tại trang B2")
        return False
    
    # Sau khi hoàn thành B2, chờ đến khi title và URL đúng trang B3 rồi hỏi user
    b3_ready = wait_for_b3_title_and_url()
    if not b3_ready:
        print("❌ Không thể vào đúng trang B3!")
        return False
    print("\n🎉 HOÀN THÀNH TOÀN BỘ QUÁ TRÌNH ĐĂNG KÝ!")
    print("📍 Hiện tại đang ở trang B3 - có thể kiểm tra kết quả")
def wait_for_b3_after_save_button():
    """
    CHỜ user bấm nút, SAU ĐÓ mới reload vô hạn cho đến khi vào B3
    Không reload trước khi user bấm nút!
    """
    global driver
    valid_titles = [
        "Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An",
        "Đăng nhập SSO – UniSoft"
    ]
    target_url_marker = "wfrmDangKyLopTinChiB3.aspx"
    
    # LƯU TRẠNG THÁI BAN ĐẦU (trước khi user bấm nút)
    initial_url = driver.current_url
    initial_title = driver.title.strip()
    
    print("\n⏸️  ĐANG CHỜ USER BẤM NÚT 'LƯU KẾT QUẢ ĐĂNG KÝ'...")
    print(f"📍 URL hiện tại: {initial_url}")
    print(f"📄 Title hiện tại: '{initial_title}'")
    print("👀 Script đang theo dõi, KHÔNG reload...")
    print("-" * 70)
    
    # BƯỚC 1: CHỜ PHÁT HIỆN USER ĐÃ BẤM NÚT
    # Chấp nhận cả trường hợp postback không đổi URL:
    # - URL/title đổi, HOẶC
    # - DOM B3 đã xuất hiện
    check_count = 0
    
    while True:
        try:
            time.sleep(0.5)  # Kiểm tra mỗi 0.5 giây
            check_count += 1
            current_title = driver.title.strip()
            current_url = driver.current_url
            
            # Hiển thị trạng thái mỗi 1200 lần (600 giây = 10 phút)
            if check_count % 1200 == 0:
                elapsed_seconds = check_count * 0.5
                print(f"⏱️ Đã chờ {int(elapsed_seconds)}s - URL: {current_url[:50]}...", end="\r", flush=True)
            
            # PHÁT HIỆN THAY ĐỔI = USER ĐÃ BẤM NÚT!
            b3_dom_ready = False
            try:
                # B3 thường có bảng danh sách đăng ký + checkbox xác nhận
                b3_checks = driver.find_elements(By.XPATH, "//table[@id='grdViewMonDangKy']//input[@type='checkbox']")
                b3_dom_ready = len(b3_checks) > 0
            except Exception:
                b3_dom_ready = False

            if current_url != initial_url or current_title != initial_title or b3_dom_ready:
                print("\n")
                print("="*70)
                print("🎯 PHÁT HIỆN THAY ĐỔI - User đã bấm nút!")
                print(f"   📄 Title ban đầu: '{initial_title}'")
                print(f"   📄 Title mới: '{current_title}'")
                print(f"   🔗 URL ban đầu: {initial_url}")
                print(f"   🔗 URL mới: {current_url}")
                if b3_dom_ready:
                    print("   ✅ DOM B3 đã xuất hiện")
                print("="*70)
                break
                
        except Exception as e:
            print(f"\n⚠️ Lỗi khi theo dõi: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(1)
    
    # BƯỚC 2: BẮT ĐẦU RELOAD CHO ĐẾN KHI VÀO ĐÚNG B3
    print("\n🔄 BẮT ĐẦU KIỂM TRA VÀ RELOAD CHO ĐẾN KHI VÀO B3...")
    for i, title in enumerate(valid_titles, 1):
        print(f"🎯 Title hợp lệ {i}: '{title}'")
    print(f"🎯 Target URL marker: '{target_url_marker}'")
    print("-" * 70)
    
    reload_count = 0
    while True:
        try:
            current_title = driver.title.strip()
            current_url = driver.current_url
            reload_count += 1
            
            print(f"\n🔍 Check #{reload_count}:")
            print(f"   📄 Title: '{current_title}'")
            print(f"   🔗 URL: {current_url}")
            
            # ĐIỀU KIỆN THÀNH CÔNG: Title đúng và (URL marker đúng hoặc DOM B3 đúng)
            b3_dom_ready = False
            try:
                b3_checks = driver.find_elements(By.XPATH, "//table[@id='grdViewMonDangKy']//input[@type='checkbox']")
                b3_dom_ready = len(b3_checks) > 0
            except Exception:
                b3_dom_ready = False

            if (current_title in valid_titles) and (target_url_marker in current_url or b3_dom_ready):
                print("\n" + "="*70)
                print("🎉 THÀNH CÔNG! ĐÃ VÀO ĐƯỢC TRANG B3!")
                print(f"✅ Title ĐÚNG: '{current_title}'")
                print(f"✅ URL: {current_url}")
                if b3_dom_ready:
                    print("✅ DOM B3: Đã phát hiện bảng grdViewMonDangKy")
                print("="*70)
                
                # KIỂM TRA TITLE MỘT LẦN NỮA TRƯỚC KHI CHỤP
                print("🔍 Kiểm tra lại title B3 trước khi chụp ảnh...")
                final_title = driver.title.strip()
                if final_title in valid_titles:
                    print(f"✅ Xác nhận title ĐÚNG: '{final_title}'")
                    take_screenshot("b3_reached_after_save")
                    return True
                else:
                    print(f"⚠️ Title đổi thành SAI: '{final_title}' - Tiếp tục reload...")
                    continue
            
            # Nếu title hoặc URL KHÁC - Reload ngay
            else:
                if current_title not in valid_titles:
                    print(f"❌ Title SAI: '{current_title}'")
                    print(f"🎯 Cần một trong các title hợp lệ (xem trên)")
                if target_url_marker not in current_url and not b3_dom_ready:
                    print(f"❌ URL chưa đúng")
                
                print("🔄 Tiếp tục reload...")
                driver.refresh()
                time.sleep(1)
                wait_for_page_load_complete()
            
            # Hiển thị tiến trình mỗi 10 lần
            if reload_count % 10 == 0:
                print(f"\n📊 Đã reload {reload_count} lần, tiếp tục chờ vào B3...")
                
        except Exception as e:
            print(f"❌ Lỗi khi kiểm tra: {e}")
            print("🔄 Thử reload lại...")
            try:
                driver.refresh()
                time.sleep(1)
            except:
                pass

# --- NEW FUNCTION: Wait for both title and URL at B3 ---
def wait_for_b3_title_and_url():
    """
    Reload until both title and URL are correct for B3
    CHỈ CHẤP NHẬN 2 TITLE ĐÚNG:
    1. 'Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An'
    2. 'Đăng nhập SSO – UniSoft'
    Tất cả khác đều reload vô hạn
    """
    global driver
    valid_titles = [
        "Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An",
        "Đăng nhập SSO – UniSoft"
    ]
    target_url_marker = "wfrmDangKyLopTinChiB3.aspx"
    reload_count = 0
    
    print("\n🔄 ĐANG KIỂM TRA TITLE VÀ URL TRANG B3 - VÔ HẠN NẾU CẦN")
    for i, title in enumerate(valid_titles, 1):
        print(f"🎯 Title hợp lệ {i}: '{title}'")
    print(f"🎯 URL cần chứa: '{target_url_marker}'")
    print("❌ TẤT CẢ title khác đều SAI - sẽ reload vô hạn")
    
    while True:
        try:
            current_title = driver.title.strip()
            current_url = driver.current_url
            reload_count += 1
            
            print(f"\n🔍 B3 Check #{reload_count}:")
            print(f"   📄 Title: '{current_title}'")
            print(f"   🔗 URL: {current_url}")
            
            # ĐIỀU KIỆN THÀNH CÔNG: Title ĐÚNG VÀ URL đúng (chấp nhận query string)
            if (current_title in valid_titles) and (target_url_marker in current_url):
                print("🎉 ĐÃ ĐÚNG TITLE VÀ URL TRANG B3!")
                take_screenshot("b3_title_and_url_ready")
                return True
                
            # NẾU TITLE HOẶC URL KHÁC - RELOAD VÔ HẠN
            else:
                if current_title not in valid_titles:
                    print(f"❌ Title SAI: '{current_title}'")
                    print(f"🎯 Cần một trong các title hợp lệ (xem trên)")
                if target_url_marker not in current_url:
                    print(f"❌ URL chưa đúng: '{current_url}'")
                    print(f"🎯 Cần chứa: '{target_url_marker}'")
                
                print(f"🔄 Đang reload lần {reload_count}...")
                driver.refresh()
                time.sleep(1)  # Tối ưu thời gian
                wait_for_page_load_complete()
                
            # Hiển thị tiến trình mỗi 15 lần
            if reload_count % 15 == 0:
                print(f"📊 B3: Đã reload {reload_count} lần, tiếp tục kiểm tra...")
                
        except Exception as e:
            print(f"❌ Lỗi khi kiểm tra B3 title/url: {e}")
            reload_count += 1
            time.sleep(1)

def handle_page_b1(valid_titles, wrong_title, skip_initial_title_check=False):
    """
    Xử lý trang B1: Kiểm tra title → reload nếu cần → chọn học phần → bấm "Đăng ký lớp tín chỉ"
    
    Args:
        skip_initial_title_check: Nếu True, bỏ qua kiểm tra title lần đầu (dùng khi redirect từ SinhVien.aspx)
    """
    global driver, config
    
    print("📋 Trang B1: Chọn học phần")
    print(f"🎯 Valid titles: {valid_titles}")
    print(f"⚠️ Wrong title: {wrong_title}")
    
    # Bước 1: Đảm bảo title đúng - Kiểm tra ngay khi vào trang
    if skip_initial_title_check:
        print("⏭️  BỎ QUA kiểm tra title lần đầu (đã redirect từ SinhVien.aspx)")
    else:
        print("🔍 Kiểm tra title khi vào trang B1...")
        current_title = driver.title.strip()
        print(f"📄 Title hiện tại: '{current_title}'")
        
        # Nếu title SAI - reload cho đến khi đúng
        if current_title not in valid_titles:
            print(f"❌ Title SAI, bắt đầu reload...")
            check_and_reload_if_error("vào trang B1")
        else:
            print(f"✅ Title ĐÚNG! Tiếp tục xử lý...")
    
    # Bước 2: Tìm và chọn các học phần từ config mới
    subject_names_b1 = config.get("course_selections", {}).get("subject_names_b1", [])
    
    # Fallback về cấu trúc cũ nếu không có config mới
    if not subject_names_b1:
        subject_names_b1 = config.get("selected_courses", [])
    
    print(f"📚 Danh sách học phần cần chọn (B1): {subject_names_b1}")
    print(f"🔍 DEBUG: Có {len(subject_names_b1)} học phần cần tìm")
    
    if "KTCT0722H_D19QL" in subject_names_b1:
        print(f"🎯 KTCT0722H_D19QL có trong danh sách - sẽ tìm kiếm môn này!")
    elif "CNXH0722H_D18CT" in subject_names_b1:
        print(f"🎯 CNXH0722H_D18CT có trong danh sách - sẽ tìm kiếm môn này!")
    else:
        print(f"⚠️ Không tìm thấy KTCT0722H_D19QL hoặc CNXH0722H_D18CT trong danh sách!")
        print(f"📋 Danh sách hiện tại: {subject_names_b1}")
    
    selection_success, not_found_count = select_courses_on_page(subject_names_b1, "học phần")
    if not selection_success:
        print("❌ Lỗi khi chọn học phần")
        return False
    
    # KIỂM TRA TITLE SAU KHI CHỌᱸ HỌC PHẦN
    print("🔍 Kiểm tra title sau khi chọn học phần B1...")
    check_and_reload_if_error("sau khi chọn học phần B1")
    
    # Nếu có môn không tìm thấy → CHỜ USER kiểm tra và tự bấm nút
    if not_found_count > 0:
        print("\n" + "="*70)
        print("⚠️  CÓ MÔN KHÔNG TÌM THẤY - DỪNG LẠI ĐỂ USER KIỂM TRA")
        print("="*70)
        print(f"❌ Số môn không tìm thấy: {not_found_count}")
        print(f"📋 Vui lòng kiểm tra danh sách môn học trên trang")
        print(f"👉 SAU KHI KIỂM TRA XONG:")
        print(f"   1. Tự tay bấm nút 'Đăng ký lớp tín chỉ' trên trang web")
        print(f"   2. Script sẽ tự động phát hiện và tiếp tục sang bước 2")
        print("="*70)
        
        # CHỜ user bấm nút - script sẽ tự động phát hiện khi URL thay đổi
        print("\n⏸️  Đang chờ user bấm nút 'Đăng ký lớp tín chỉ'...")
        print("👀 Script đang theo dõi URL + DOM, KHÔNG reload...")
        
        # Lưu URL hiện tại
        current_url = driver.current_url
        wait_count = 0
        
        # Đợi cho đến khi user bấm nút:
        # - URL đổi, HOẶC
        # - DOM đã sang cấu trúc B2 (table#grd có radio button)
        while True:
            time.sleep(0.5)
            wait_count += 1

            # Kiểm tra URL thay đổi
            new_url = driver.current_url
            if new_url != current_url:
                print(f"\n✅ Phát hiện URL đã thay đổi! User đã bấm nút.")
                print(f"📍 URL mới: {new_url}")
                break

            # Kiểm tra DOM B2
            try:
                b2_radios = driver.find_elements(By.XPATH, "//table[@id='grd']//input[@type='radio']")
                if b2_radios and len(b2_radios) > 0:
                    print(f"\n✅ Phát hiện DOM B2 (table#grd + {len(b2_radios)} radio button), coi như đã bấm nút.")
                    break
            except Exception as e:
                pass
    else:
        # Không có môn nào thiếu → Tự động bấm nút
        print("\n✅ Tất cả môn đều tìm thấy - Tự động bấm nút 'Đăng ký lớp tín chỉ'")
        print("🔘 Tìm và bấm nút 'Đăng ký lớp tín chỉ'...")
        button_success = click_submit_button("cmdDangKyLop2", "Đăng ký lớp tín chỉ")
        if not button_success:
            print("❌ Không thể bấm nút 'Đăng ký lớp tín chỉ'")
            return False
    
    # Sau khi bấm nút (auto hoặc user), bắt buộc chờ sang đúng URL B2 mới xử lý tiếp
    if not wait_for_b2_url_after_b1_button():
        print("❌ Không thể chuyển sang trang B2 sau khi bấm nút 'Đăng ký lớp tín chỉ'")
        return False
    
    print("✅ Hoàn thành trang B1")
    take_screenshot("b1_completed")

    # Sau khi hoàn thành B1, khởi động script tự động chọn môn/lớp
    try:
        import subprocess
        import sys
        print("🚀 Đang khởi động course_auto_selector.py để tự động tích chọn môn/lớp...")
        subprocess.Popen([sys.executable, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "course_auto_selector.py"))])
    except Exception as e:
        print(f"❌ Lỗi khi khởi động course_auto_selector.py: {e}")

    return True

def wait_for_b2_url_after_b1_button():
    """
    Sau khi bấm cmdDangKyLop2 ở B1, chờ cho đến khi vào đúng URL B2.
    """
    global driver

    target_b2 = "wfrmDangKyLopTinChiB2.aspx"
    check_count = 0

    print("\n🔄 ĐANG CHỜ CHUYỂN TỪ B1 SANG B2...")
    print(f"🎯 URL cần chứa: {target_b2}")

    while True:
        check_count += 1
        try:
            current_url = driver.current_url

            # Thành công nếu URL đúng HOẶC DOM đã là trang B2 (một số lần postback không đổi URL)
            b2_dom_ready = False
            try:
                b2_radios = driver.find_elements(By.XPATH, "//table[@id='grd']//input[@type='radio']")
                b2_dom_ready = len(b2_radios) > 0
                
                if b2_dom_ready:
                    print(f"✅ B2 DOM detected: {len(b2_radios)} radio buttons found")
            except Exception:
                b2_dom_ready = False

            # Log mỗi 10 lần kiểm tra (5 giây) để user còn theo dõi
            if check_count % 10 == 0:
                elapsed = check_count * 0.5
                print(f"🔍 B1→B2 check #{check_count} ({elapsed:.1f}s): URL = {current_url[:70]}...")

            if target_b2 in current_url or b2_dom_ready:
                print("✅ Đã chuyển sang đúng trang B2")
                take_screenshot("reached_b2_after_cmdDangKyLop2")
                return True

            # Chờ trang tự chuyển trước khi refresh
            time.sleep(0.5)
            wait_for_page_load_complete()

            # Nếu vẫn chưa vào B2 thì refresh và kiểm tra tiếp
            if target_b2 not in driver.current_url and not b2_dom_ready:
                print("🔄 Chưa vào B2, tiếp tục reload để chờ chuyển trang...")
                driver.refresh()
                time.sleep(1)
        except Exception as e:
            print(f"⚠️  Lỗi khi chờ sang B2: {e}")
            time.sleep(0.5)

def handle_page_b2(valid_titles, wrong_title):
    """
    Xử lý trang B2: Kiểm tra title → reload nếu cần → chọn lớp tín chỉ → bấm "Lưu kết quả đăng ký"
    """
    global driver, config
    
    print("📋 Trang B2: Chọn lớp tín chỉ")
    print(f"🎯 Valid titles: {valid_titles}")
    print(f"⚠️ Wrong title: {wrong_title}")
    
    # Bước 1: Đảm bảo title đúng - Kiểm tra ngay khi vào trang
    print("🔍 Kiểm tra title khi vào trang B2...")
    current_title = driver.title.strip()
    print(f"📄 Title hiện tại: '{current_title}'")
    
    # Nếu title SAI - reload cho đến khi đúng
    if current_title not in valid_titles:
        print(f"❌ Title SAI, bắt đầu reload...")
        check_and_reload_if_error("vào trang B2")
    else:
        print(f"✅ Title ĐÚNG! Tiếp tục xử lý...")
    
    # Bước 2: Tìm và chọn các lớp tín chỉ từ config mới
    class_names_b2 = config.get("course_selections", {}).get("class_names_b2", [])

    # Fallback an toàn: chỉ lấy các mục trông như mã lớp tín chỉ, tránh nhầm sang mã học phần B1
    if not class_names_b2:
        legacy_items = config.get("selected_courses", [])
        class_names_b2 = [
            x for x in legacy_items
            if isinstance(x, str) and ('.' in x or '_LT' in x or '_TH' in x or '_BT' in x)
        ]
    
    print(f"📚 Danh sách lớp tín chỉ cần chọn (B2): {class_names_b2}")
    print(f"🔍 DEBUG: Có {len(class_names_b2)} lớp tín chỉ cần tìm")
    
    if "KTCT0722H_D19QL.03_LT" in class_names_b2:
        print(f"🎯 KTCT0722H_D19QL.03_LT có trong danh sách B2 - sẽ tìm kiếm lớp này!")
    elif "CNXH0722H_D18CT.01_LT" in class_names_b2:
        print(f"🎯 CNXH0722H_D18CT.01_LT có trong danh sách B2 - sẽ tìm kiếm lớp này!")
    else:
        print(f"⚠️ Không tìm thấy KTCT0722H_D19QL.03_LT hoặc CNXH0722H_D18CT.01_LT trong danh sách!")
        print(f"📋 Danh sách B2 hiện tại: {class_names_b2}")
    
    selection_success, not_found_count_b2 = select_courses_on_page(class_names_b2, "lớp tín chỉ")
    if not selection_success:
        print("❌ Lỗi khi chọn lớp tín chỉ")
        return False
    
    # Hiển thị cảnh báo nếu có lớp không tìm thấy ở B2
    if not_found_count_b2 > 0:
        print(f"\n⚠️  CÓ {not_found_count_b2} LỚP KHÔNG TÌM THẤY Ở TRANG B2")
        print(f"📋 Vui lòng kiểm tra danh sách lớp tín chỉ trên trang")
        
        # Nếu có lớp không tìm thấy - CHỜ USER BẤM NÚT
        print("\n" + "="*70)
        print("⚠️  CÓ MÔN KHÔNG TÌM THẤY - DỪNG LẠI ĐỂ USER KIỂM TRA")
        print("="*70)
        print("👉 SAU KHI KIỂM TRA XONG:")
        print("   1. Tự tay bấm nút 'Lưu kết quả đăng ký' trên trang web")
        print("   2. Script sẽ tự động phát hiện và tiếp tục sang bước 3")
        print("="*70)
        
        # CHỜ USER BẤM NÚT - KHÔNG TỰ ĐỘNG RELOAD
        print("\n⏳ Đang chờ bạn bấm nút 'Lưu kết quả đăng ký'...")
        print("💡 Script sẽ tự động phát hiện khi bạn bấm và xử lý tiếp...")
        
        # Bắt đầu kiểm tra và reload vô hạn cho đến khi vào B3
        wait_for_b3_after_save_button()
    else:
        # TÌM ĐỦ VÀ TÍCH ĐỦ CÁC LỚP → TỰ ĐỘNG BẤM NÚT
        print("\n" + "="*70)
        print("✅ ĐÃ TÌM VÀ CHỌN ĐỦ TẤT CẢ CÁC LỚP TÍN CHỈ!")
        print("="*70)
        print(f"📊 Tổng số lớp: {len(class_names_b2)}")
        print(f"✅ Đã chọn: {len(class_names_b2)}")
        print(f"❌ Không tìm thấy: 0")
        print("="*70)
        
        # Chụp ảnh tổng hợp trước khi bấm nút
        print("\n📸 Chụp ảnh tổng hợp tất cả các lớp đã chọn...")
        take_screenshot("b2_all_classes_selected")
        
        # TỰ ĐỘNG BẤM NÚT "LƯU KẾT QUẢ ĐĂNG KÝ"
        print("\n🔘 Tự động bấm nút 'Lưu kết quả đăng ký'...")
        button_success = False
        
        # Thử cách 1: Submit button với text "Lưu kết quả đăng ký"
        try:
            btn = driver.find_element(By.XPATH, "//input[@type='submit' and contains(translate(@value, 'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ', 'aaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooouuuuuuuuuuuyyyyyd'), @value)]" )
            # Fallback: Tìm bằng text gần đúng
            if not btn:
                btn = driver.find_element(By.XPATH, "//input[contains(@value, 'Lưu')]")
        except:
            btn = None
        
        # Thử cách 2: Button element với text chứa "Lưu"
        if not btn:
            try:
                btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Lưu')]")
            except:
                btn = None
        
        # Thử cách 3: Input type submit (không có text filter cụ thể)
        if not btn:
            try:
                btns = driver.find_elements(By.XPATH, "//input[@type='submit']")
                for b in btns:
                    if 'Lưu' in b.get_attribute('value'):
                        btn = b
                        break
            except:
                btn = None
        
        if btn:
            try:
                driver.execute_script("arguments[0].click();", btn)
                print("✅ Đã bấm nút thành công!")
                button_success = True
            except Exception as e:
                print(f"⚠️ Không thể bấm: {e}")
                button_success = False
        
        if not button_success:
            print("❌ Không thể tự động bấm nút 'Lưu kết quả đăng ký'")
            print("👆 Vui lòng TỰ BẤM nút trên trình duyệt!")
            
            # CHỜ USER BẤM NÚT
            print("\n⏳ Đang chờ bạn bấm nút...")
            wait_for_b3_after_save_button()
        else:
            # Chờ trang xử lý một chút
            time.sleep(2)
            
            # KIỂM TRA TITLE NGAY SAU KHI BẤM
            print("\n🔄 Kiểm tra title sau khi bấm nút...")
            current_title = driver.title.strip()
            current_url = driver.current_url
            
            valid_titles = [
                "Giải pháp Phần mềm Quản trị Trường học số UniSoft - Thiên An",
                "Đăng nhập SSO – UniSoft"
            ]
            target_url_marker = "wfrmDangKyLopTinChiB3.aspx"
            
            print(f"📍 URL hiện tại: {current_url}")
            print(f"📄 Title hiện tại: '{current_title}'")
            
            # NẾU TITLE SAI → RELOAD CHO ĐẾN KHI ĐÚNG
            if current_title not in valid_titles:
                print(f"❌ Title SAI sau khi bấm nút!")
                print(f"🎯 Cần title hợp lệ:")
                for i, title in enumerate(valid_titles, 1):
                    print(f"   {i}. '{title}'")
                print("\n🔄 Bắt đầu reload cho đến khi title đúng và vào B3...")
                
                reload_count = 0
                while True:
                    try:
                        reload_count += 1
                        print(f"\n🔄 Reload lần #{reload_count}...")
                        driver.refresh()
                        time.sleep(1)
                        wait_for_page_load_complete()
                        
                        current_title = driver.title.strip()
                        current_url = driver.current_url
                        
                        print(f"📄 Title sau reload: '{current_title}'")
                        print(f"📍 URL sau reload: {current_url}")
                        
                        # KIỂM TRA THÀNH CÔNG
                        if current_title in valid_titles:
                            print("\n✅ ĐÃ VÀO ĐƯỢC TRANG B3 VỚI TITLE ĐÚNG!")
                            if target_url_marker in current_url:
                                print("✅ URL marker B3 đã đúng")
                            else:
                                print("⏸️ Title B3 đã đúng, tạm dừng toàn bộ hành động và KHÔNG reload thêm")
                            break
                        elif current_title not in valid_titles:
                            print(f"❌ Title vẫn sai: '{current_title}'")
                            print("🔄 Tiếp tục reload...")
                        else:
                            print("⚠️ Title đúng nhưng URL chưa đúng, tiếp tục...")
                            
                    except Exception as e:
                        print(f"⚠️ Lỗi khi reload: {e}")
                        time.sleep(1)
            else:
                # Title đã đúng ngay sau khi bấm
                print("✅ Title đã đúng ngay sau khi bấm!")
                if target_url_marker in current_url:
                    print("✅ Đã vào trang B3!")
                else:
                    print("⏸️ Title B3 đã đúng, tạm dừng toàn bộ hành động và KHÔNG reload thêm")

    print("✅ Hoàn thành trang B2")
    take_screenshot("b2_completed")
    return True

def ensure_correct_title(target_title, wrong_title, page_name):
    """
    Đảm bảo title đúng - CHỈ CHẤP NHẬN 1 TITLE DUY NHẤT
    Tất cả title khác đều SAI và reload vô hạn
    """
    global driver
    
    reload_count = 0
    print(f"🔄 [{page_name}] BẮT ĐẦU KIỂM TRA TITLE - CHỈ CHẤP NHẬN 1 TITLE")
    print(f"🎯 Title DUY NHẤT được chấp nhận: '{target_title}'")
    print("❌ TẤT CẢ title khác đều SAI - sẽ reload vô hạn")
    
    while True:
        try:
            current_title = driver.title.strip()
            current_url = driver.current_url
            reload_count += 1
            
            print(f"\n🔍 [{page_name}] Kiểm tra lần {reload_count}:")
            print(f"📍 URL: {current_url}")
            print(f"📄 Title: '{current_title}'")
            
            # KIỂM TRA NẾU TITLE ĐÃ ĐÚNG - DỪNG LẠI
            if current_title == target_title:
                print(f"✅ [{page_name}] Title ĐÚNG! DỪNG KIỂM TRA")
                return True
            
            # NẾU TITLE KHÁC - RELOAD VÔ HẠN
            else:
                print(f"❌ [{page_name}] Title SAI: '{current_title}'")
                print(f"🎯 Cần title: '{target_title}'")
                print(f"🔄 Reload vô hạn lần {reload_count}...")
                reload_success = reload_page_multiple_ways()
                if reload_success:
                    print("✅ Reload thành công")
                else:
                    print("⚠️ Reload thất bại, thử cách khác...")
                time.sleep(1)  # Tối ưu thời gian
                wait_for_page_load_complete()
                
            # Hiển thị tiến trình mỗi 10 lần
            if reload_count % 10 == 0:
                print(f"📊 [{page_name}] Đã reload {reload_count} lần, tiếp tục...")
                
        except Exception as e:
            print(f"❌ [{page_name}] Lỗi khi kiểm tra title: {e}")
            reload_count += 1
            time.sleep(1)

def reload_page_multiple_ways():
    """
    Thử reload trang bằng nhiều cách khác nhau
    """
    global driver
    
    try:
        # Cách 1: F5
        try:
            from selenium.webdriver.common.keys import Keys
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.F5)
            print("🔄 Đã bấm F5")
            return True
        except:
            pass
        
        # Cách 2: driver.refresh()
        try:
            driver.refresh()
            print("🔄 Đã dùng driver.refresh()")
            return True
        except:
            pass
        
        # Cách 3: Reload current URL
        try:
            current_url = driver.current_url
            driver.get(current_url)
            print("🔄 Đã reload URL")
            return True
        except:
            pass
            
        return False
        
    except Exception as e:
        print(f"❌ Lỗi khi reload: {e}")
        return False

def normalize_text_for_search(text):
    """
    Làm sạch text: bỏ dấu, bỏ khoảng trắng, uppercase
    TĐTC0122L → TDTC0122L
    """
    import unicodedata
    
    raw = str(text).replace("Đ", "D").replace("đ", "d")
    # Chuẩn hóa Unicode NFD để tách diacritics
    normalized = unicodedata.normalize('NFD', raw)
    # Loại bỏ tất cả diacritics (Combining Diacritical Marks)
    text_without_accents = ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
    # Trim và uppercase
    return text_without_accents.strip().upper()

def select_courses_on_page(selected_courses, item_type):
    """
    Tìm và chọn các khóa học trên trang
    """
    global driver
    
    if not selected_courses:
        print(f"⚠️ Không có {item_type} nào cần chọn")
        return True
    
    print(f"🔍 Đang tìm {item_type} trên trang...")
    
    # DEBUG: In ra tất cả text có trên trang
    try:
        all_page_text = driver.execute_script("""
            var allText = [];
            document.querySelectorAll('*').forEach(el => {
                var text = el.textContent.trim();
                if (text && text.length < 200 && text.length > 2) {
                    allText.push(text);
                }
            });
            return [...new Set(allText)];  // Remove duplicates
        """)
        print(f"📋 DEBUG: Tất cả text trên trang (max 50):")
        for idx, text in enumerate(all_page_text[:50]):
            norm = normalize_text_for_search(text)
            if "TDTC0122L" in norm or "0122" in text:
                print(f"   🎯 [{idx}] '{text}' → Normalized: '{norm}'")
    except Exception as e:
        print(f"⚠️ Không thể lấy tất cả text: {e}")
    
    selected_count = 0
    already_selected_count = 0
    not_found_list = []  # Danh sách các môn/lớp không tìm thấy
    
    for course_code in selected_courses:
        print(f"\n🔍 Đang tìm {item_type}: {course_code}")
        
        if course_code == "KTCT0722H_D19QL":
            print(f"🎯 ĐÂY LÀ MÔN KTCT0722H_D19QL - SẼ TÌM KIẾM KỸ LƯỠNG!")
        elif course_code == "CNXH0722H_D18CT":
            print(f"🎯 ĐÂY LÀ MÔN CNXH0722H_D18CT - SẼ TÌM KIẾM KỸ LƯỠNG!")
        
        found_and_selected = find_and_select_course(course_code, item_type)
        
        if found_and_selected in ["selected", "success"]:  # Support both "selected" (B1) and "success" (B2)
            selected_count += 1
            print(f"✅ Đã chọn {item_type}: {course_code}")
        elif found_and_selected == "already_selected":
            already_selected_count += 1
            print(f"✅ {item_type} đã tích sẵn (bỏ qua): {course_code}")
        else:
            print(f"❌ Không tìm thấy {item_type}: {course_code}")
            not_found_list.append(course_code)  # Thêm vào danh sách không tìm thấy
    
    not_found_count = len(not_found_list)
    
    print(f"\n📊 Tổng kết chọn {item_type}:")
    print(f"✅ Đã chọn mới: {selected_count}")
    print(f"✅ Đã tích sẵn (bỏ qua): {already_selected_count}")
    print(f"❌ Không tìm thấy: {not_found_count}")
    
    # In ra danh sách các môn/lớp không tìm thấy
    if not_found_list:
        print(f"\n⚠️ Danh sách {item_type} không tìm thấy:")
        for idx, course in enumerate(not_found_list, 1):
            print(f"   {idx}. {course}")
    
    take_screenshot(f"course_selection_{item_type.replace(' ', '_')}")
    return True, not_found_count

def find_and_select_course(course_code, item_type):
    """
    Tìm và chọn một khóa học cụ thể
    """
    global driver
    
    try:
        print(f"🔍 Đang tìm {item_type}: '{course_code}'")
        
        # Chuẩn hóa code để tìm kiếm
        normalized_code = normalize_text_for_search(course_code)
        print(f"📝 Normalized khi tìm: '{course_code}' → '{normalized_code}'")
        
        if "KTCT0722H_D19QL" in course_code:
            print(f"🚨 QUAN TRỌNG: Đang tìm kiếm lớp KTCT0722H_D19QL - {course_code}!")
        elif course_code == "CNXH0722H_D18CT":
            print(f"🚨 QUAN TRỌNG: Đang tìm kiếm môn CNXH0722H_D18CT!")
        elif "CNXH0722H_D18CT" in course_code:
            print(f"🚨 QUAN TRỌNG: Đang tìm kiếm lớp CNXH0722H_D18CT - {course_code}!")
            
        # Tách thành các phần để tìm kiếm linh hoạt hơn
        course_parts = course_code.split('.')
        base_course = course_parts[0] if course_parts else course_code
        normalized_base = normalize_text_for_search(base_course)
        
        print(f"📋 Tìm kiếm với: '{course_code}' và base: '{base_course}'")
        course_element = None
        found_selector = None
        course_selectors = []

        # ✅ PHƯƠNG PHÁP 1: Tìm kiểu Ctrl+F trên nội dung trang bằng JavaScript
        print("🔍 Phương pháp 1: Tìm kiếm kiểu Ctrl+F trên text trang...")
        try:
            match_info = driver.execute_script("""
                function normalizeText(text) {
                    if (text === null || text === undefined) return '';
                    return String(text)
                        .replace(/[Đđ]/g, 'D')
                        .normalize('NFD')
                        .replace(/[\u0300-\u036f]/g, '')
                        .toUpperCase()
                        .trim();
                }

                var rawTarget = arguments[0];
                var baseTarget = arguments[1];
                var targetNorm = normalizeText(rawTarget);
                var baseNorm = normalizeText(baseTarget);
                var candidates = Array.from(document.querySelectorAll('td,span,div,label,a,button,input,option,tr'));

                for (var i = 0; i < candidates.length; i++) {
                    var el = candidates[i];
                    var text = (el.innerText || el.textContent || '').trim();
                    if (!text || text.length > 200) continue;

                    var textNorm = normalizeText(text);
                    if (textNorm === targetNorm || textNorm.includes(targetNorm) || targetNorm.includes(textNorm) ||
                        textNorm === baseNorm || textNorm.includes(baseNorm)) {
                        return {element: el, text: text, tag: el.tagName};
                    }
                }
                return null;
            """, course_code, base_course)

            if match_info and match_info.get('element'):
                course_element = match_info['element']
                found_selector = "CTRL+F text search"
                print(f"✅ Ctrl+F tìm thấy: '{match_info.get('text', '').strip()}'")
                print(f"✅ Element tag: '{course_element.tag_name}'")
                print(f"✅ Element text: '{course_element.text.strip()}'")
                print(f"✅ Tìm thấy bằng kiểu tìm text trên trang, không phụ thuộc dấu tiếng Việt")

                current_url = driver.current_url
                if "B2" in current_url and course_element.tag_name.lower() == 'td':
                    try:
                        parent_row = course_element.find_element(By.XPATH, "./ancestor::tr[1]")
                        radio_buttons = parent_row.find_elements(By.XPATH, ".//input[@type='radio']")
                        if radio_buttons:
                            old_element = course_element
                            course_element = radio_buttons[0]
                            print(f"🎯 Ctrl+F: Đã chuyển từ TD '{old_element.text.strip()}' sang radio button!")
                            print(f"🎯 Radio button ID: {course_element.get_attribute('id') or 'N/A'}")
                            print(f"🎯 Radio button name: {course_element.get_attribute('name') or 'N/A'}")
                            print(f"🎯 Radio button checked: {course_element.get_attribute('checked') or 'False'}")
                    except Exception as radio_search_error:
                        print(f"⚠️ Lỗi khi tìm radio button từ Ctrl+F result: {radio_search_error}")

                elif course_element.tag_name.lower() == 'input' and course_element.get_attribute('type') == 'radio':
                    print("🎯 Đã tìm thấy radio button trực tiếp bằng Ctrl+F!")
                    print(f"🎯 Radio button ID: {course_element.get_attribute('id') or 'N/A'}")
                    print(f"🎯 Radio button name: {course_element.get_attribute('name') or 'N/A'}")
                    print(f"🎯 Radio button checked: {course_element.get_attribute('checked') or 'False'}")
        except Exception as ctrl_f_error:
            print(f"⚠️ Ctrl+F search failed: {ctrl_f_error}")
            course_element = None
        
        # ✅ PHƯƠNG PHÁP 2: XPath thông thường với normalized text
        if not course_element:
            print(f"🔍 Phương pháp 2: Tìm kiếm bằng XPath...")
            
            course_selectors = [
                # ƯU TIÊN HÀNG ĐẦU: Tìm radio button trực tiếp từ tên lớp tín chỉ
                (By.XPATH, f"//tr[td[normalize-space(text())='{course_code}']]//input[@type='radio']"),
                (By.XPATH, f"//tr[td[text()='{course_code}']]//input[@type='radio']"),
            (By.XPATH, f"//tr[td[contains(normalize-space(.), '{course_code}')]]//input[@type='radio']"),
            (By.XPATH, f"//tr[.//text()[normalize-space()='{course_code}']]//input[@type='radio']"),
            
            # Tìm theo text của tên lớp tín chỉ
            (By.XPATH, f"//td[normalize-space(text())='{course_code}']"),
            (By.XPATH, f"//td[text()='{course_code}']"),
            (By.XPATH, f"//td[contains(text(), '{course_code}')]"),
            (By.XPATH, f"//*[normalize-space(text())='{course_code}']"),
            (By.XPATH, f"//span[normalize-space(text())='{course_code}']"),
            (By.XPATH, f"//div[normalize-space(text())='{course_code}']"),
            (By.XPATH, f"//label[normalize-space(text())='{course_code}']"),
            
            # Tìm theo text chính xác không chuẩn hóa
            (By.XPATH, f"//td[text()='{course_code}']"),
            (By.XPATH, f"//span[text()='{course_code}']"),
            (By.XPATH, f"//div[text()='{course_code}']"),
            (By.XPATH, f"//label[text()='{course_code}']"),
            
            # Tìm theo contains text đầy đủ
            (By.XPATH, f"//td[contains(text(), '{course_code}')]"),
            (By.XPATH, f"//span[contains(text(), '{course_code}')]"),
            (By.XPATH, f"//div[contains(text(), '{course_code}')]"),
            (By.XPATH, f"//label[contains(text(), '{course_code}')]"),
            
            # Tìm theo value attributes
            (By.XPATH, f"//input[@value='{course_code}']"),
            (By.XPATH, f"//option[@value='{course_code}']"),
            (By.XPATH, f"//input[contains(@value, '{course_code}')]"),
            
            # Tìm theo base course name (phần trước dấu chấm)
            (By.XPATH, f"//td[contains(text(), '{base_course}')]"),
            (By.XPATH, f"//span[contains(text(), '{base_course}')]"),
            
            # Tìm trong table rows chứa text
            (By.XPATH, f"//tr[contains(normalize-space(.), '{course_code}')]"),
            (By.XPATH, f"//tr[contains(., '{course_code}')]"),
            
            # Tìm theo id và name attributes với base course
            (By.XPATH, f"//input[contains(@id, '{base_course}')]"),
            (By.XPATH, f"//input[contains(@name, '{base_course}')]"),
            
            # Tìm rộng nhất
            (By.XPATH, f"//*[contains(text(), '{course_code}')]"),
        ]
        
        course_element = None
        found_selector = None
        
        # Thử tìm element với từng selector
        for i, (by_type, selector) in enumerate(course_selectors):
            try:
                print(f"   Thử selector {i+1}/{len(course_selectors)}: {selector}")
                elements = driver.find_elements(by_type, selector)
                if elements:
                    course_element = elements[0]
                    found_selector = selector
                    print(f"✅ Tìm thấy {item_type} bằng selector: {selector}")
                    print(f"📄 Element tag: '{course_element.tag_name}'")
                    print(f"📄 Element text: '{course_element.text.strip()}'")
                    print(f"📄 Element ID: '{course_element.get_attribute('id') or 'N/A'}'")
                    print(f"📄 Element type: '{course_element.get_attribute('type') or 'N/A'}'")
                    
                    # ĐẶC BIỆT CHO B2: Nếu tìm thấy text course, tìm radio button trong cùng hàng
                    current_url = driver.current_url
                    if "B2" in current_url and course_element.tag_name.lower() == 'td':
                        try:
                            # Tìm thẻ tr chứa td này
                            parent_row = course_element.find_element(By.XPATH, "./ancestor::tr[1]")
                            # Tìm radio button trong hàng đó
                            radio_buttons = parent_row.find_elements(By.XPATH, ".//input[@type='radio']")
                            if radio_buttons:
                                old_element = course_element
                                course_element = radio_buttons[0]  # Lấy radio button đầu tiên
                                print(f"🎯 Đã chuyển từ TD '{old_element.text.strip()}' sang radio button!")
                                print(f"🎯 Radio button ID: {course_element.get_attribute('id') or 'N/A'}")
                                print(f"🎯 Radio button name: {course_element.get_attribute('name') or 'N/A'}")
                                print(f"🎯 Radio button checked: {course_element.get_attribute('checked') or 'False'}")
                            else:
                                print(f"⚠️ Không tìm thấy radio button trong hàng chứa course text")
                        except Exception as radio_search_error:
                            print(f"⚠️ Lỗi khi tìm radio button: {radio_search_error}")
                    
                    # Nếu đã là radio button thì báo thông tin luôn
                    elif course_element.tag_name.lower() == 'input' and course_element.get_attribute('type') == 'radio':
                        print(f"🎯 Đã tìm thấy radio button trực tiếp!")
                        print(f"🎯 Radio button ID: {course_element.get_attribute('id') or 'N/A'}")
                        print(f"🎯 Radio button name: {course_element.get_attribute('name') or 'N/A'}")
                        print(f"🎯 Radio button checked: {course_element.get_attribute('checked') or 'False'}")
                    
                    break
                else:
                    print(f"   ❌ Không tìm thấy với selector này")
            except Exception as e:
                print(f"   ⚠️ Lỗi với selector này: {e}")
                continue
        
        if not course_element:
            print(f"❌ Không tìm thấy {item_type}: {course_code}")
            print("🔍 Thử phương pháp tìm kiếm backup - quét toàn bộ trang...")
            
            # BACKUP METHOD: Tìm trong toàn bộ trang
            try:
                all_elements = driver.find_elements(By.XPATH, "//*[text()]")
                print(f"📋 Đang quét {len(all_elements)} elements có text...")
                
                found_matches = []
                for element in all_elements:
                    try:
                        element_text = element.text.strip()
                        if element_text and (course_code in element_text or element_text == course_code):
                            found_matches.append((element, element_text))
                            print(f"🎯 MATCH tìm thấy! Element: {element.tag_name}, Text: '{element_text}'")
                            
                            # Thử element này
                            if not course_element:  # Lấy match đầu tiên
                                # Kiểm tra xem có cần tìm radio button không
                                current_url = driver.current_url
                                if "B2" in current_url and element.tag_name.lower() == 'td':
                                    try:
                                        # Tìm radio button trong cùng hàng
                                        parent_row = element.find_element(By.XPATH, "./ancestor::tr[1]")
                                        radio_buttons = parent_row.find_elements(By.XPATH, ".//input[@type='radio']")
                                        if radio_buttons:
                                            course_element = radio_buttons[0]
                                            print(f"🎯 Backup scan: Tìm thấy radio button trong hàng! ID: {course_element.get_attribute('id') or 'N/A'}")
                                        else:
                                            course_element = element
                                    except:
                                        course_element = element
                                else:
                                    course_element = element
                                found_selector = f"Backup scan - {element.tag_name} with text: '{element_text}'"
                    except:
                        continue
                
                if found_matches:
                    print(f"✅ Tìm thấy {len(found_matches)} element(s) match bằng backup scan!")
                else:
                    print("❌ Backup scan không tìm thấy gì")
                    
            except Exception as e:
                print(f"⚠️ Lỗi backup scan: {e}")
            
            # Nếu vẫn không tìm thấy, thử tìm elements chứa một phần của course code
            if not course_element:
                print("🔍 Thử tìm elements chứa một phần của course code...")
                parts_to_try = [base_course, course_code.split('.')[0], course_code.split('_')[0]]
                
                for part in parts_to_try:
                    if len(part) >= 4:  # Chỉ thử với parts đủ dài
                        try:
                            partial_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{part}')]")
                            print(f"🔍 Tìm với '{part}': {len(partial_elements)} elements")
                            
                            for elem in partial_elements[:5]:  # Chỉ kiểm tra 5 cái đầu
                                try:
                                    elem_text = elem.text.strip()
                                    if elem_text:
                                        print(f"   📄 '{elem_text}'")
                                except:
                                    pass
                        except:
                            pass
            
            # Nếu không tìm thấy, return not_found
            if not course_element:
                return "not_found"
        
        # ĐẶC BIỆT CHO B2: Click trực tiếp radio button
        current_url = driver.current_url
        if "B2" in current_url and course_element.tag_name.lower() == 'input' and course_element.get_attribute('type') == 'radio':
            try:
                print(f"🎯 B2 Page: Click trực tiếp radio button...")
                print(f"📻 Radio ID: {course_element.get_attribute('id') or 'N/A'}")
                print(f"📻 Radio name: {course_element.get_attribute('name') or 'N/A'}")
                
                # Enhanced scroll - scroll element to center and add offset for header
                print(f"🔄 Scrolling to element and avoiding header...")
                driver.execute_script("""
                    arguments[0].scrollIntoView({block: 'center', inline: 'center'});
                    window.scrollBy(0, -100);  // Offset for header
                """, course_element)
                time.sleep(1)  # Longer wait for scroll
                
                # Check if element is now visible and clickable
                location = course_element.location
                size = course_element.size
                print(f"📍 Element position: x={location['x']}, y={location['y']}")
                print(f"📏 Element size: width={size['width']}, height={size['height']}")
                
                # Try JavaScript click first (more reliable for intercepted elements)
                print(f"🖱️ Trying JavaScript click first...")
                driver.execute_script("arguments[0].click();", course_element)
                time.sleep(0.5)
                
                # Verify if selected
                if course_element.get_attribute('checked'):
                    print(f"✅ JavaScript click thành công!")
                    screenshot_name = f"b2_selected_{course_code.replace('.', '_')}"
                    take_screenshot(screenshot_name)
                    print(f"📸 Đã chụp ảnh màn hình: {screenshot_name}")
                    print(f"✅ THÀNH CÔNG: Đã chọn {item_type} '{course_code}'")
                    return "success"
                else:
                    print(f"⚠️ JavaScript click chưa chọn, thử Selenium click...")
                    try:
                        course_element.click()
                        print(f"✅ Selenium click thành công!")
                        time.sleep(0.3)
                        
                        # Final check
                        if course_element.get_attribute('checked'):
                            screenshot_name = f"b2_selected_{course_code.replace('.', '_')}"
                            take_screenshot(screenshot_name)
                            print(f"📸 Đã chụp ảnh màn hình: {screenshot_name}")
                            print(f"✅ THÀNH CÔNG: Đã chọn {item_type} '{course_code}'")
                            return "success"
                        else:
                            print(f"❌ Selenium click cũng không chọn được")
                            return "not_found"
                    except Exception as selenium_error:
                        print(f"⚠️ Selenium click failed: {selenium_error}")
                        print(f"⚠️ Nhưng JavaScript click có thể đã work, kiểm tra lại...")
                        time.sleep(0.5)
                        if course_element.get_attribute('checked'):
                            screenshot_name = f"b2_selected_{course_code.replace('.', '_')}"
                            take_screenshot(screenshot_name)
                            print(f"📸 Đã chụp ảnh màn hình: {screenshot_name}")
                            print(f"✅ THÀNH CÔNG: JavaScript click đã work!")
                            return "success"
                        else:
                            return "not_found"
                
            except Exception as e:
                print(f"❌ Lỗi click radio button: {e}")
                print(f"🔄 Thử phương pháp backup - click bằng JavaScript...")
                try:
                    driver.execute_script("arguments[0].click();", course_element)
                    time.sleep(0.5)
                    if course_element.get_attribute('checked'):
                        screenshot_name = f"b2_selected_{course_code.replace('.', '_')}"
                        take_screenshot(screenshot_name)
                        print(f"📸 Đã chụp ảnh màn hình: {screenshot_name}")
                        print(f"✅ BACKUP SUCCESS: JavaScript click worked!")
                        return "success"
                except:
                    pass
                return "not_found"
        
        # CHO CÁC PAGE KHÁC: Tìm checkbox liên quan
        print(f"🔍 Đang tìm checkbox cho element tìm được...")
        checkbox = find_related_checkbox(course_element, course_code)
        
        if not checkbox:
            print(f"❌ Không tìm thấy checkbox cho {item_type}: {course_code}")
            print("🔍 Debug: Thử tìm tất cả checkboxes trong vùng lân cận...")
            
            # Debug: Tìm tất cả checkboxes gần đó
            try:
                parent = course_element.find_element(By.XPATH, "./..")  # Element cha
                nearby_checkboxes = parent.find_elements(By.XPATH, ".//input[@type='checkbox']")
                print(f"📋 Tìm thấy {len(nearby_checkboxes)} checkbox(es) gần element này")
                
                for i, cb in enumerate(nearby_checkboxes):
                    try:
                        cb_value = cb.get_attribute("value") or ""
                        cb_name = cb.get_attribute("name") or ""
                        cb_id = cb.get_attribute("id") or ""
                        print(f"   Checkbox {i+1}: value='{cb_value}', name='{cb_name}', id='{cb_id}'")
                    except:
                        pass
            except Exception as e:
                print(f"   ⚠️ Lỗi debug checkbox: {e}")
            
            return "not_found"
        
        # Kiểm tra xem đã được chọn chưa
        is_selected = checkbox.is_selected()
        
        if is_selected:
            print(f"✅ {item_type} đã được tích sẵn, bỏ qua: {course_code}")
            return "already_selected"
        
        # Chọn checkbox
        try:
            # Scroll đến element
            driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
            time.sleep(0.5)
            
            # Click checkbox
            checkbox.click()
            print(f"✅ Đã click checkbox cho {item_type}: {course_code}")
            
            # Verify selection
            time.sleep(0.5)
            if checkbox.is_selected():
                print(f"✅ Xác nhận đã chọn {item_type}: {course_code}")
                take_screenshot(f"selected_{course_code.replace('.', '_')}")
                return "selected"
            else:
                print(f"⚠️ Click thành công nhưng chưa được chọn: {course_code}")
                return "not_found"
                
        except Exception as e:
            print(f"❌ Lỗi khi click checkbox: {e}")
            
            # Thử click bằng JavaScript
            try:
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(0.5)
                if checkbox.is_selected():
                    print(f"✅ Đã chọn bằng JavaScript: {course_code}")
                    take_screenshot(f"selected_{course_code.replace('.', '_')}")
                    return "selected"
            except:
                pass
            
            return "not_found"
        
    except Exception as e:
        print(f"❌ Lỗi khi tìm {item_type} {course_code}: {e}")
        return "not_found"

def find_related_checkbox(course_element, course_code):
    """
    Tìm checkbox HOẶC radio button liên quan đến course element
    FIX: Input không có value attribute chứa course code, nó nằm trong hàng (row) như nhau với course code
    Hỗ trợ cả B2 (radio buttons) và B3 (checkboxes)
    """
    global driver
    
    try:
        print(f"🔍 Tìm checkbox/radio button cho element: {course_element.tag_name}")
        print(f"📄 Element text: '{course_element.text.strip()}'")
        
        # Lấy thông tin course code để tìm kiếm
        base_course = course_code.split('.')[0] if '.' in course_code else course_code
        
        # 🎯 CÁCH TỐT NHẤT: Từ course_element (thường là <td> chứa tên lớp học phần), 
        #    Đi lên <tr> cha và tìm checkbox/radio trong row đó
        print(f"🔍 Cách 1: Tìm checkbox/radio button trong cùng hàng <tr> với course element...")
        try:
            # Từ course_element, tìm ancestor <tr>
            parent_row = course_element.find_element(By.XPATH, "./ancestor::tr[1]")
            print(f"✅ Tìm thấy parent row")
            
            # Tìm CHECKBOX hoặc RADIO BUTTON trong row này (ưu tiên checkbox B3, rồi radio B2)
            checkboxes_in_row = parent_row.find_elements(By.XPATH, ".//input[@type='checkbox']")
            radio_in_row = parent_row.find_elements(By.XPATH, ".//input[@type='radio']")
            
            if checkboxes_in_row:
                print(f"✅ Tìm thấy {len(checkboxes_in_row)} checkbox(es) trong hàng (B3 mode)")
                cb = checkboxes_in_row[0]
                cb_id = cb.get_attribute("id") or "N/A"
                cb_name = cb.get_attribute("name") or "N/A"
                print(f"✅ Checkbox trong hàng: id='{cb_id}', name='{cb_name}'")
                print(f"🎯 Trả về checkbox từ cùng hàng (row-based match)")
                return cb
            elif radio_in_row:
                print(f"✅ Tìm thấy {len(radio_in_row)} radio button(s) trong hàng (B2 mode)")
                radio = radio_in_row[0]
                radio_id = radio.get_attribute("id") or "N/A"
                radio_name = radio.get_attribute("name") or "N/A"
                print(f"✅ Radio button trong hàng: id='{radio_id}', name='{radio_name}'")
                print(f"🎯 Trả về radio button từ cùng hàng (row-based match)")
                return radio
        except Exception as e:
            print(f"⚠️ Không tìm thấy parent row hoặc input trong row: {e}")
        
        # Cách 2: Tìm checkbox/radio trong cùng parent element (fallback)
        print(f"🔍 Cách 2: Tìm checkbox/radio button trong parent element...")
        parent_selectors = [
            ("../input[@type='checkbox']", "checkbox"),          # Trong parent <tr>
            ("../input[@type='radio']", "radio"),
            ("../../input[@type='checkbox']", "checkbox"),       # Trong grandparent  
            ("../../input[@type='radio']", "radio"),
            ("../../../input[@type='checkbox']", "checkbox"),    # Trong great-grandparent
            ("../../../input[@type='radio']", "radio"),
        ]
        
        for selector, input_type in parent_selectors:
            try:
                inputs = course_element.find_elements(By.XPATH, selector)
                if inputs:
                    print(f"✅ Tìm thấy {len(inputs)} {input_type}(s) với selector: {selector}")
                    inp = inputs[0]
                    inp_id = inp.get_attribute("id") or "N/A"
                    inp_name = inp.get_attribute("name") or "N/A"
                    print(f"   {input_type.capitalize()}: id='{inp_id}', name='{inp_name}'")
                    print(f"🎯 Trả về {input_type} từ parent selector")
                    return inp
            except:
                continue
        
        # Cách 3: Tìm checkbox/radio theo table row (fallback khi không tìm được từ parent)
        print("🔍 Cách 3: Tìm checkbox/radio button qua table row XPath...")
        try:
            # Tìm tất cả rows chứa course_code text
            rows = driver.find_elements(By.XPATH, f"//tr[contains(., '{course_code}')]")
            if rows:
                print(f"✅ Tìm thấy {len(rows)} hàng chứa course code '{course_code}'")
                for row in rows:
                    # Ưu tiên checkbox (B3) rồi radio (B2)
                    checkboxes = row.find_elements(By.XPATH, ".//input[@type='checkbox']")
                    if checkboxes:
                        cb = checkboxes[0]
                        print(f"🎯 Trả về checkbox từ row-based search (B3)")
                        return cb
                    
                    radios = row.find_elements(By.XPATH, ".//input[@type='radio']")
                    if radios:
                        radio = radios[0]
                        print(f"🎯 Trả về radio button từ row-based search (B2)")
                        return radio
        except Exception as e:
            print(f"⚠️ Row-based XPath search failed: {e}")
        
        # 🔴 KHÔNG CÓ FALLBACK NỮA - TỪ CHỐI CHỌN NẾU KHÔNG TÌM ĐƯỢC
        print(f"❌ Không thể tìm được checkbox cho course code '{course_code}'")
        print(f"❌ Từ chối chọn checkbox để tránh lỗi chọn nhầm")
        return None
            
        return None
        
    except Exception as e:
        print(f"❌ Lỗi khi tìm checkbox: {e}")
        return None

def click_submit_button(button_id, button_text):
    """
    Tìm và click nút submit
    """
    global driver
    
    try:
        print(f"🔍 Đang tìm nút: {button_text}")
        
        # Các cách tìm button
        button_selectors = [
            (By.ID, button_id),
            (By.NAME, button_id),
            (By.XPATH, f"//input[@id='{button_id}']"),
            (By.XPATH, f"//input[@name='{button_id}']"),
            (By.XPATH, f"//input[@value='{button_text}']"),
            (By.XPATH, f"//button[contains(text(), '{button_text}')]"),
            (By.XPATH, f"//input[@type='submit' and @value='{button_text}']"),
        ]
        
        button = None
        
        for by_type, selector in button_selectors:
            try:
                element = driver.find_element(by_type, selector)
                if element and element.is_displayed():
                    button = element
                    print(f"✅ Tìm thấy nút bằng: {selector}")
                    break
            except:
                continue
        
        if not button:
            print(f"❌ Không tìm thấy nút: {button_text}")
            return False
        
        # Scroll đến button
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(1)
        
        # Click button
        try:
            button.click()
            print(f"✅ Đã click nút: {button_text}")
        except:
            # Thử JavaScript click
            driver.execute_script("arguments[0].click();", button)
            print(f"✅ Đã click nút bằng JavaScript: {button_text}")
        
        # Chờ trang load
        time.sleep(2)
        wait_for_page_load_complete()
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi click nút {button_text}: {e}")
        return False

def main(gui_mode=False):
    """Hàm chính"""
    global GUI_MODE
    GUI_MODE = gui_mode  # Set GUI_MODE để safe_input() biết
    
    print("=" * 70)
    print("🤖 ULSA AUTO LOGIN WITH TITLE CHECK")
    print("   Tự động reload trang → kiểm tra title → đăng nhập")
    print("=" * 70)
    print()
    
    try:
        # Bước 1: Load config
        print("📋 BƯỚC 1: KIỂM TRA FILE CẤU HÌNH")
        if not load_config():
            safe_input("Nhấn Enter để thoát...")
            return
        
        # Bước 2: Setup Chrome driver
        print("\n🔧 BƯỚC 2: KHỞI TẠO TRÌNH DUYỆT")
        if not setup_chrome_driver():
            safe_input("Nhấn Enter để thoát...")
            return
        
        # Bước 3: Truy cập trang đăng nhập
        print("\n🌐 BƯỚC 3: TRUY CẬP TRANG ULSA")
        login_url = "http://sinhvien.ulsa.edu.vn/Login.aspx"
        print(f"🔗 Đang truy cập: {login_url}")
        
        # Tăng timeout và retry nếu không kết nối được
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                print(f"🔄 Thử kết nối lần {attempt}/{max_retries}...")
                driver.set_page_load_timeout(60)  # Tăng timeout lên 60 giây
                driver.get(login_url)
                print(f"✅ Kết nối thành công!")
                break
            except Exception as e:
                if attempt < max_retries:
                    print(f"⚠️ Lỗi lần {attempt}: {str(e)[:100]}")
                    print(f"🔄 Đợi 5 giây trước khi thử lại...")
                    time.sleep(5)
                else:
                    print(f"❌ Không thể kết nối sau {max_retries} lần thử!")
                    print(f"💡 Giải pháp:")
                    print(f"   1. Kiểm tra kết nối internet")
                    print(f"   2. Thử truy cập {login_url} bằng trình duyệt thường")
                    print(f"   3. Website có thể đang bảo trì")
                    print(f"   4. Thử đổi mạng (4G/WiFi khác)")
                    raise
        
        time.sleep(3)
        
        initial_title = driver.title
        print(f"📄 Title ban đầu: '{initial_title}'")
        take_screenshot("initial_page")
        
        # Bước 4: Chờ title đúng bằng cách reload
        print(f"\n🔄 BƯỚC 4: CHỜ TITLE CHÍNH XÁC")
        if not wait_for_correct_title():
            print("❌ Không thể có được title đúng!")
            safe_input("Nhấn Enter để thoát...")
            return
        
        # Bước 5: Đăng nhập tự động
        print(f"\n🔐 BƯỚC 5: ĐĂNG NHẬP TỰ ĐỘNG")
        if auto_login():
            print("\n🎉 QUÁ TRÌNH HOÀN TẤT THÀNH CÔNG!")
            print("✅ Đã đăng nhập thành công vào hệ thống ULSA")
        else:
            print("\n❌ ĐĂNG NHẬP THẤT BẠI!")
            print("🔍 Vui lòng kiểm tra lại thông tin trong auto_config.json")
        
        # Bước 6: Xử lý trang B1 và B2 (nếu có)
        print("\n📚 BƯỚC 6: XỬ LÝ TRANG ĐĂNG KÝ LỚP TÍN CHỈ")
        course_result = handle_course_selection_pages()
        
        if course_result:
            print("\n🎉 QUÁ TRÌNH HOÀN TẤT THÀNH CÔNG!")
            print("✅ Đã hoàn thành tất cả các bước đăng ký")
            print("📍 Hiện tại đang ở trang B3 - kết quả đăng ký")
        else:
            print("\n⚠️ Có lỗi trong quá trình đăng ký lớp tín chỉ")
        
        # Giữ browser mở để kiểm tra
        print("\n🌐 Browser được giữ mở để bạn kiểm tra kết quả...")
        print("🔍 Bạn có thể xem lại thông tin đăng ký trên trang")
        safe_input("👆 Nhấn ENTER để đóng browser và kết thúc chương trình...")
        
    except KeyboardInterrupt:
        print("\n⚠️ Đã dừng chương trình bằng Ctrl+C")
        print("\n🌐 Browser được giữ mở để bạn kiểm tra...")
        safe_input("👆 Nhấn ENTER để đóng browser...")
    except Exception as e:
        print(f"\n❌ Lỗi tổng quát: {e}")
        print("\n🌐 Browser được giữ mở để bạn kiểm tra lỗi...")
        safe_input("👆 Nhấn ENTER để đóng browser...")
    finally:
        # Chỉ đóng browser khi user cho phép
        if driver:
            try:
                driver.quit()
                print("✅ Đã đóng trình duyệt")
            except:
                pass

if __name__ == "__main__":
    main()
