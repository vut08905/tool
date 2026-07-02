#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ULSA Auto Login with Save Credentials
Đăng nhập tự động với tính năng lưu thông tin
"""

import time
import json
import base64
import os
import shutil
import subprocess
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

def check_chrome_installed():
    """Kiểm tra Chrome đã cài chưa"""
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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    local_paths = [
        os.path.join(current_dir, "drivers", "chromedriver.exe"),
        os.path.join(parent_dir, "drivers", "chromedriver.exe"),
        os.path.join(current_dir, "chromedriver.exe"),
        os.path.join(parent_dir, "chromedriver.exe"),
    ]
    
    for path in local_paths:
        if os.path.exists(path):
            print(f"✅ Tìm thấy ChromeDriver local: {path}")
            return path
    
    print("📥 Không tìm thấy ChromeDriver local, đang tải về...")
    try:
        driver_path = ChromeDriverManager().install()
        print(f"✅ Đã tải ChromeDriver: {driver_path}")
        return driver_path
    except Exception as e:
        print(f"❌ Lỗi tải ChromeDriver: {e}")
        drivers_dir = os.path.join(parent_dir, "drivers")
        if not os.path.exists(drivers_dir):
            os.makedirs(drivers_dir, exist_ok=True)
        print(f"\n💡 TIP: Tải chromedriver.exe về: {drivers_dir}")
        print("   Tải tại: https://googlechromelabs.github.io/chrome-for-testing/")
        raise

def get_chrome_version():
    """Lấy phiên bản Chrome"""
    try:
        is_installed, chrome_path = check_chrome_installed()
        if not is_installed:
            return None
        result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True, timeout=5)
        return result.stdout.strip().split()[-1]
    except Exception:
        return None

def auto_update_chrome():
    """Tự động mở Chrome update hoặc tải mới"""
    print("\n" + "="*60)
    print("🔧 TỰ ĐỘNG KHẮC PHỤC LỖI CHROME")
    print("="*60)
    
    is_installed, chrome_path = check_chrome_installed()
    
    if is_installed:
        print("✅ Đã phát hiện Chrome")
        version = get_chrome_version()
        if version:
            print(f"📌 Phiên bản: {version}")
        
        print("\n🔄 Mở trang cập nhật Chrome...")
        try:
            subprocess.Popen([chrome_path, "chrome://settings/help"])
            print("✅ Đã mở Chrome Settings")
            print("💡 Hãy đợi update xong, sau đó chạy lại!")
            return True
        except Exception as e:
            print(f"⚠️ Lỗi: {e}")
            return False
    else:
        print("❌ Không tìm thấy Chrome")
        print("\n📥 Mở trang tải Chrome...")
        try:
            webbrowser.open("https://www.google.com/chrome/")
            print("✅ Hãy tải và cài Chrome, sau đó chạy lại!")
            return True
        except Exception as e:
            print(f"⚠️ Lỗi: {e}")
            return False

class ULSAAutoLoginWithSave:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.config_file = "auto_config.json"
        self.config = self.load_config()
        self.login_url = "http://sinhvien.ulsa.edu.vn/Login.aspx"
    
    def load_config(self):
        """Load cấu hình từ file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self.get_default_config()
    
    def save_config(self):
        """Lưu cấu hình vào file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    def get_default_config(self):
        """Cấu hình mặc định"""
        return {
            "login_config": {
                "auto_save_credentials": False,
                "remember_last_username": True,
                "auto_submit": True,
                "wait_time_after_submit": 5
            },
            "saved_data": {
                "last_username": "",
                "encrypted_password": ""
            }
        }
    
    def simple_encrypt(self, text):
        """Mã hóa đơn giản"""
        return base64.b64encode(text.encode()).decode()
    
    def simple_decrypt(self, encrypted):
        """Giải mã đơn giản"""
        try:
            return base64.b64decode(encrypted).decode()
        except:
            return ""
    
    def setup_browser(self):
        """Thiết lập trình duyệt với auto-update ChromeDriver"""
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print("🔧 Đang thiết lập trình duyệt...")
                
                chrome_options = Options()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                driver_path = get_chromedriver_path()
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                self.wait = WebDriverWait(self.driver, 15)
                print("✅ Trình duyệt đã sẵn sàng!")
                return True
                
            except (AttributeError, TypeError) as e:
                if "'NoneType' object has no attribute 'split'" in str(e) or "split" in str(e):
                    retry_count += 1
                    print(f"❌ Lỗi thiết lập: {str(e)}")
                    print(f"🔄 Đang thử lại lần {retry_count}/{max_retries}...")
                    
                    if retry_count < max_retries:
                        print("🧹 Đang xóa cache ChromeDriver cũ...")
                        try:
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
                        print("❌ LỖI: Không thể khởi tạo ChromeDriver")
                        print("="*60)
                        
                        # Tự động mở Chrome update
                        auto_update_chrome()
                        
                        print("\n⏸️  Ứng dụng tạm dừng để update Chrome...")
                        print("💡 Sau khi update xong, chạy lại app!")
                        print("="*60)
                        input("\n👉 Nhấn Enter để thoát...")
                        return False
                else:
                    print(f"❌ Lỗi thiết lập: {str(e)}")
                    return False
                    
            except Exception as e:
                retry_count += 1
                print(f"❌ Lỗi thiết lập: {str(e)}")
                if retry_count < max_retries:
                    print(f"🔄 Đang thử lại lần {retry_count}/{max_retries}...")
                    time.sleep(2)
                    continue
                return False
        
        return False
    
    def navigate_to_login(self):
        """Điều hướng đến trang đăng nhập"""
        try:
            print(f"🌐 Đang truy cập: {self.login_url}")
            self.driver.get(self.login_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("✅ Đã truy cập thành công!")
            return True
        except Exception as e:
            print(f"❌ Lỗi truy cập: {str(e)}")
            return False
    
    def get_credentials(self):
        """Lấy thông tin đăng nhập"""
        print("\n" + "="*60)
        print("🎓 THÔNG TIN ĐĂNG NHẬP")
        print("="*60)
        
        # Kiểm tra thông tin đã lưu
        last_username = self.config.get("saved_data", {}).get("last_username", "")
        saved_password = self.config.get("saved_data", {}).get("encrypted_password", "")
        
        if last_username:
            print(f"💾 Tìm thấy tài khoản đã lưu: {last_username}")
            use_saved = input("Sử dụng tài khoản đã lưu? (y/n): ").strip().lower()
            
            if use_saved == 'y' and saved_password:
                password = self.simple_decrypt(saved_password)
                if password:
                    print("✅ Sử dụng thông tin đã lưu")
                    return {
                        'username': last_username,
                        'password': password,
                        'save_info': True
                    }
        
        # Nhập thông tin mới
        while True:
            username = input("👤 Mã sinh viên: ").strip()
            if username:
                break
            print("⚠️ Vui lòng nhập mã sinh viên!")
        
        while True:
            password = input("🔐 Mật khẩu: ").strip()
            if password:
                break
            print("⚠️ Vui lòng nhập mật khẩu!")
        
        # Hỏi có lưu thông tin không
        save_info = input("💾 Lưu thông tin đăng nhập? (y/n): ").strip().lower() == 'y'
        
        if save_info:
            self.config["saved_data"]["last_username"] = username
            self.config["saved_data"]["encrypted_password"] = self.simple_encrypt(password)
            self.save_config()
            print("✅ Đã lưu thông tin đăng nhập")
        
        return {
            'username': username,
            'password': password,
            'save_info': save_info
        }
    
    def auto_fill_and_submit(self, credentials):
        """Tự động điền và submit form"""
        try:
            print("\n🤖 BẮT ĐẦU ĐĂNG NHẬP TỰ ĐỘNG...")
            print("="*60)
            
            # Step 1: Fill username
            print("📝 Đang điền mã sinh viên...")
            username_field = self.wait.until(EC.element_to_be_clickable((By.ID, "txtusername")))
            username_field.clear()
            time.sleep(0.5)
            
            # Type naturally
            for char in credentials['username']:
                username_field.send_keys(char)
                time.sleep(0.1)
            
            print("✅ Đã điền mã sinh viên")
            
            # Step 2: Fill password
            print("🔐 Đang điền mật khẩu...")
            password_field = self.driver.find_element(By.ID, "txtpassword")
            password_field.clear()
            time.sleep(0.5)
            
            for char in credentials['password']:
                password_field.send_keys(char)
                time.sleep(0.1)
            
            print("✅ Đã điền mật khẩu")
            
            # Step 3: Take screenshot before submit
            self.take_screenshot("before_submit.png")
            
            # Step 4: Submit form
            print("🚀 Đang thực hiện đăng nhập...")
            
            # Try multiple submit methods
            submit_success = False
            
            # Method 1: Click login button
            try:
                login_button = self.driver.find_element(By.ID, "btnDangNhap")
                login_button.click()
                submit_success = True
                print("✅ Đã click nút đăng nhập")
            except:
                # Method 2: Press Enter
                try:
                    password_field.send_keys(Keys.RETURN)
                    submit_success = True
                    print("✅ Đã nhấn Enter")
                except:
                    # Method 3: JavaScript submit
                    try:
                        self.driver.execute_script("document.forms[0].submit();")
                        submit_success = True
                        print("✅ Đã submit bằng JavaScript")
                    except:
                        pass
            
            if not submit_success:
                print("❌ Không thể submit form")
                return False
            
            # Step 5: Wait and check result
            print("⏳ Đang chờ phản hồi...")
            time.sleep(self.config.get("login_config", {}).get("wait_time_after_submit", 5))
            
            return self.check_login_result()
            
        except Exception as e:
            print(f"❌ Lỗi trong quá trình đăng nhập: {str(e)}")
            return False
    
    def check_login_result(self):
        """Kiểm tra kết quả đăng nhập"""
        try:
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            print("\n📊 KẾT QUẢ ĐĂNG NHẬP")
            print("="*60)
            print(f"🔗 URL: {current_url}")
            print(f"📄 Tiêu đề: {page_title}")
            
            # Take screenshot of result
            self.take_screenshot("login_result.png")
            
            # Check if still on login page
            if "Login.aspx" in current_url:
                # Check for error messages
                page_source = self.driver.page_source.lower()
                error_keywords = ["sai", "lỗi", "error", "incorrect", "invalid"]
                
                if any(keyword in page_source for keyword in error_keywords):
                    print("❌ ĐĂNG NHẬP THẤT BẠI - Sai thông tin!")
                    return False
                else:
                    print("⚠️ Vẫn ở trang đăng nhập - Có thể cần thời gian xử lý")
                    return False
            else:
                print("🎉 ĐĂNG NHẬP THÀNH CÔNG!")
                print("✅ Đã được chuyển hướng khỏi trang đăng nhập")
                return True
                
        except Exception as e:
            print(f"❌ Lỗi kiểm tra kết quả: {str(e)}")
            return False
    
    def take_screenshot(self, filename):
        """Chụp ảnh màn hình"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, f"{timestamp}_{filename}")
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot: {screenshot_path}")
        except:
            pass
    
    def show_menu(self):
        """Hiển thị menu sau khi đăng nhập"""
        print("\n" + "="*60)
        print("🎯 MENU THAO TÁC")
        print("="*60)
        print("1. Tiếp tục sử dụng hệ thống")
        print("2. Xóa thông tin đã lưu")
        print("3. Thoát")
        print("-" * 60)
        
        choice = input("👆 Chọn thao tác (1-3): ").strip()
        
        if choice == "2":
            self.clear_saved_data()
        elif choice == "3":
            return False
        
        return True
    
    def clear_saved_data(self):
        """Xóa thông tin đã lưu"""
        try:
            self.config["saved_data"]["last_username"] = ""
            self.config["saved_data"]["encrypted_password"] = ""
            self.save_config()
            print("✅ Đã xóa thông tin đã lưu")
        except:
            print("❌ Lỗi khi xóa thông tin")
    
    def keep_browser_open(self):
        """Giữ trình duyệt mở"""
        print("\n" + "="*60)
        print("🌐 TRÌNH DUYỆT ĐANG MỞ")
        print("="*60)
        print("Bạn có thể sử dụng hệ thống bình thường")
        print("Nhấn Enter để đóng...")
        
        try:
            input()
        except KeyboardInterrupt:
            print("\nDừng bằng Ctrl+C")
    
    def close_browser(self):
        """Đóng trình duyệt"""
        try:
            if self.driver:
                self.driver.quit()
                print("✅ Đã đóng trình duyệt")
        except:
            pass

def main():
    """Hàm chính"""
    print("=" * 70)
    print("🤖 ULSA AUTO LOGIN WITH SAVE CREDENTIALS")
    print("   Đăng nhập tự động với tính năng lưu thông tin")
    print("=" * 70)
    
    automation = ULSAAutoLoginWithSave()
    
    try:
        # Setup browser
        if not automation.setup_browser():
            return
        
        # Navigate to login page
        if not automation.navigate_to_login():
            return
        
        # Get credentials
        credentials = automation.get_credentials()
        if not credentials:
            return
        
        # Auto fill and submit
        success = automation.auto_fill_and_submit(credentials)
        
        if success:
            # Show menu and keep browser open
            if automation.show_menu():
                automation.keep_browser_open()
        else:
            print("\n❌ Đăng nhập thất bại")
            automation.keep_browser_open()
        
    except KeyboardInterrupt:
        print("\n⚠️ Đã dừng chương trình")
    except Exception as e:
        print(f"\n❌ Lỗi: {str(e)}")
    finally:
        automation.close_browser()

if __name__ == "__main__":
    main()
