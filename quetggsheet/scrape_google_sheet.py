"""
Phương pháp 2: Sử dụng Python với Selenium để scrape dữ liệu
Yêu cầu: pip install selenium webdriver-manager gspread oauth2client
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def scrape_google_sheet_with_selenium(sheet_url, output_file='sheet_data.json'):
    """
    Scrape Google Sheet bằng Selenium (yêu cầu đăng nhập thủ công)
    """
    # Setup Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    # options.add_argument('--headless')  # Bỏ comment nếu muốn chạy ẩn
    
    # Sử dụng profile Chrome có sẵn để giữ session đăng nhập
    # options.add_argument(r'--user-data-dir=C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data')
    # options.add_argument('--profile-directory=Default')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print("Đang mở Google Sheet...")
        driver.get(sheet_url)
        
        # Đợi đăng nhập thủ công (nếu cần)
        print("Vui lòng đăng nhập Google nếu cần. Nhấn Enter sau khi đã vào được sheet...")
        input()
        
        # Đợi sheet load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.grid-container'))
        )
        
        print("Đang scrape dữ liệu...")
        time.sleep(3)  # Đợi render hoàn toàn
        
        # Lấy tất cả cells
        cells = driver.find_elements(By.CSS_SELECTOR, 'div.cell')
        
        data = []
        current_row = []
        last_row = None
        
        for cell in cells:
            try:
                # Lấy vị trí cell
                aria_label = cell.get_attribute('aria-label')
                text = cell.text
                
                # Parse row number từ aria-label
                # Format: "A1" hoặc tương tự
                if aria_label:
                    # Tách row number
                    row_num = ''.join(filter(str.isdigit, aria_label.split()[0]))
                    
                    if last_row and row_num != last_row:
                        data.append(current_row)
                        current_row = []
                    
                    current_row.append(text)
                    last_row = row_num
            except:
                continue
        
        if current_row:
            data.append(current_row)
        
        # Lưu data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Đã lưu {len(data)} rows vào {output_file}")
        print(f"Preview: {data[:3]}")
        
        return data
        
    except Exception as e:
        print(f"Lỗi: {e}")
        return None
    
    finally:
        driver.quit()


def scrape_with_screenshot(sheet_url):
    """
    Phương pháp backup: Chụp màn hình và OCR
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(sheet_url)
        print("Đăng nhập và nhấn Enter...")
        input()
        
        time.sleep(3)
        
        # Chụp màn hình
        driver.save_screenshot('sheet_screenshot.png')
        print("✓ Đã chụp màn hình: sheet_screenshot.png")
        
        # Có thể dùng OCR như pytesseract để đọc text từ ảnh
        
    finally:
        driver.quit()


# Sử dụng
if __name__ == '__main__':
    SHEET_URL = 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit'
    
    # Phương pháp 1: Scrape trực tiếp
    data = scrape_google_sheet_with_selenium(SHEET_URL)
    
    # Phương pháp 2: Chụp màn hình
    # scrape_with_screenshot(SHEET_URL)
