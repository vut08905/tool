"""
Script tự động quét Google Sheet bị khóa ra Excel
Yêu cầu: Email của bạn được owner cấp quyền xem
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from datetime import datetime
import sys

def quet_google_sheet(sheet_url):
    """
    Quét Google Sheet bị khóa bằng Selenium
    """
    print("🚀 Bắt đầu quét Google Sheet...")
    print(f"📎 URL: {sheet_url}\n")
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Sử dụng Chrome profile để giữ đăng nhập (tùy chọn)
    # chrome_options.add_argument(r'--user-data-dir=C:\Users\YourName\AppData\Local\Google\Chrome\User Data')
    
    try:
        # Khởi động Chrome (không cần webdriver-manager)
        print("🌐 Đang mở Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Mở Google Sheet
        driver.get(sheet_url)
        
        print("\n" + "="*60)
        print("⚠️  QUAN TRỌNG:")
        print("1. Đăng nhập Google bằng email được cấp quyền")
        print("2. Chờ sheet load xong")
        print("3. Nhấn Enter trong terminal này để bắt đầu quét")
        print("="*60 + "\n")
        
        input("👉 Nhấn Enter khi đã vào được sheet... ")
        
        print("\n⏳ Đang đợi sheet load...")
        time.sleep(5)  # Đợi render
        
        # Thử lấy dữ liệu bằng nhiều cách
        print("📊 Đang thu thập dữ liệu...\n")
        
        data = []
        
        # Cách 1: Lấy từ table
        try:
            # Scroll để load hết data
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Lấy tất cả rows
            rows = driver.find_elements(By.CSS_SELECTOR, 'tr')
            print(f"✓ Tìm thấy {len(rows)} rows\n")
            
            for i, row in enumerate(rows):
                cells = row.find_elements(By.CSS_SELECTOR, 'td, th')
                row_data = [cell.text for cell in cells]
                if row_data:  # Bỏ qua row rỗng
                    data.append(row_data)
                
                if (i + 1) % 10 == 0:
                    print(f"   Đã xử lý {i + 1} rows...")
            
        except Exception as e:
            print(f"⚠️  Lỗi cách 1: {e}")
            
            # Cách 2: Copy toàn bộ và paste
            print("\n🔄 Thử cách 2: Sử dụng JavaScript...")
            try:
                script = """
                var rows = document.querySelectorAll('tr');
                var data = [];
                rows.forEach(function(row) {
                    var cells = row.querySelectorAll('td, th');
                    var rowData = [];
                    cells.forEach(function(cell) {
                        rowData.push(cell.innerText);
                    });
                    if (rowData.length > 0) data.push(rowData);
                });
                return data;
                """
                data = driver.execute_script(script)
                print(f"✓ Thu thập được {len(data)} rows\n")
                
            except Exception as e2:
                print(f"❌ Lỗi cách 2: {e2}")
                print("\n💡 Gợi ý: Thử copy thủ công:")
                print("   1. Ctrl+A trong sheet")
                print("   2. Ctrl+C")
                print("   3. Paste vào Excel")
                driver.quit()
                return
        
        # Kiểm tra data
        if not data or len(data) == 0:
            print("❌ Không thu thập được dữ liệu!")
            print("\n💡 Có thể sheet sử dụng cấu trúc đặc biệt.")
            print("   Thử dùng Apps Script thay thế (xem file google_apps_script.gs)")
            driver.quit()
            return
        
        print(f"\n✅ Thu thập thành công {len(data)} rows!")
        
        # Chuyển sang DataFrame
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
        else:
            df = pd.DataFrame(data)
        
        # Lưu Excel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_file = f'google_sheet_export_{timestamp}.xlsx'
        df.to_excel(excel_file, index=False, engine='openpyxl')
        
        print(f"\n" + "="*60)
        print(f"✅ ĐÃ LƯU THÀNH CÔNG!")
        print(f"📁 File: {excel_file}")
        print(f"📊 Số rows: {len(df)}")
        print(f"📋 Số columns: {len(df.columns)}")
        print("="*60)
        
        print(f"\nPreview 5 rows đầu:")
        print(df.head())
        
        driver.quit()
        return excel_file
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        print("\n💡 GIẢI PHÁP THAY THẾ:")
        print("""
1. APPS SCRIPT (Khuyến nghị):
   - Mở sheet → Extensions → Apps Script
   - Copy code từ file google_apps_script.gs
   - Run và export ra Google Drive
   
2. COPY THỦ CÔNG:
   - Mở sheet
   - Ctrl+A → Ctrl+C
   - Paste vào Excel
        """)
        try:
            driver.quit()
        except:
            pass


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║       QUÉT GOOGLE SHEET BỊ KHÓA RA EXCEL                    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        sheet_url = sys.argv[1]
    else:
        sheet_url = input("📎 Nhập URL Google Sheet: ").strip()
    
    if not sheet_url:
        print("❌ Chưa nhập URL!")
        print("\n💡 Chạy lại: python quet_sheet_khoa.py <URL>")
        sys.exit(1)
    
    # Kiểm tra URL
    if 'docs.google.com/spreadsheets' not in sheet_url:
        print("❌ URL không hợp lệ!")
        print("   URL phải có dạng: https://docs.google.com/spreadsheets/d/.../edit")
        sys.exit(1)
    
    print("\n⚠️  LƯU Ý:")
    print("   - Email của bạn phải được owner cấp quyền")
    print("   - Cần đăng nhập Google trong Chrome")
    print("   - Script sẽ mở Chrome tự động\n")
    
    time.sleep(2)
    
    quet_google_sheet(sheet_url)
