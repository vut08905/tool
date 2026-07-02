"""
Cách HIỆU QUẢ NHẤT: Tự động copy từ Google Sheet vào clipboard rồi lưu Excel
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from datetime import datetime
import time
import pyperclip

def quet_sheet_bang_copy():
    print("="*70)
    print("🚀 QUÉT GOOGLE SHEET RA EXCEL (Copy Method)")
    print("="*70)
    
    # Nhập URL
    print("\n📎 Nhập URL Google Sheet:")
    sheet_url = input("   → ").strip()
    
    if not sheet_url:
        print("❌ Chưa nhập URL!")
        return
    
    print("\n⏳ Đang khởi động Chrome...")
    
    # Setup Chrome
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=options)
        print("✅ Chrome đã mở!")
        
        # Mở Google
        print("\n🌐 Mở Google để đăng nhập...")
        driver.get("https://accounts.google.com")
        
        print("\n" + "="*70)
        print("👤 VUI LÒNG:")
        print("   1. Đăng nhập Google bằng email được cấp quyền")
        print("   2. Sau khi đăng nhập xong, nhấn Enter ở đây")
        print("="*70)
        input("\n👉 Nhấn Enter sau khi đã đăng nhập xong... ")
        
        # Mở Google Sheet
        print(f"\n📊 Đang mở Google Sheet...")
        driver.get(sheet_url)
        
        print("\n" + "="*70)
        print("📋 VUI LÒNG:")
        print("   1. Chờ sheet load xong hoàn toàn")
        print("   2. Nhấn Enter để script tự động copy dữ liệu")
        print("="*70)
        input("\n👉 Nhấn Enter để bắt đầu... ")
        
        print("\n⏳ Đang copy dữ liệu...")
        time.sleep(2)
        
        # Click vào cell đầu tiên để focus
        try:
            first_cell = driver.find_element(By.CSS_SELECTOR, 'div[role="gridcell"]')
            first_cell.click()
            time.sleep(1)
        except:
            pass
        
        # Tự động Ctrl+A (chọn tất cả)
        print("   📋 Đang chọn tất cả dữ liệu...")
        actions = ActionChains(driver)
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        time.sleep(1)
        
        # Tự động Ctrl+C (copy)
        print("   📋 Đang copy...")
        actions = ActionChains(driver)
        actions.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        time.sleep(2)
        
        # Lấy data từ clipboard
        print("   📋 Đang đọc clipboard...")
        try:
            clipboard_data = pyperclip.paste()
            
            if not clipboard_data or len(clipboard_data) < 10:
                print("\n❌ Clipboard rỗng hoặc không có dữ liệu!")
                print("\n💡 THỬ COPY THỦ CÔNG:")
                print("   1. Trong Google Sheet đang mở")
                print("   2. Nhấn Ctrl+A")
                print("   3. Nhấn Ctrl+C")
                print("   4. Nhấn Enter ở đây")
                input("\n👉 Nhấn Enter sau khi đã copy thủ công... ")
                clipboard_data = pyperclip.paste()
            
            if not clipboard_data:
                print("❌ Vẫn không có dữ liệu trong clipboard!")
                driver.quit()
                return
            
            print(f"   ✓ Đã lấy {len(clipboard_data)} ký tự từ clipboard!\n")
            
            # Parse clipboard data (tab-separated)
            lines = clipboard_data.strip().split('\n')
            data = []
            for line in lines:
                row = line.split('\t')
                data.append(row)
            
            print(f"📊 Tổng cộng: {len(data)} rows")
            
            if len(data) == 0:
                print("❌ Không có dữ liệu!")
                driver.quit()
                return
            
            # Chuyển sang DataFrame
            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
            else:
                df = pd.DataFrame(data)
            
            # Lưu Excel
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            excel_file = f'google_sheet_{timestamp}.xlsx'
            
            print(f"\n💾 Đang lưu vào Excel...")
            df.to_excel(excel_file, index=False, engine='openpyxl')
            
            print("\n" + "="*70)
            print("✅ HOÀN THÀNH!")
            print("="*70)
            print(f"📁 File: {excel_file}")
            print(f"📊 Rows: {len(df)}")
            print(f"📋 Columns: {len(df.columns)}")
            print("="*70)
            
            print(f"\n📄 Preview 10 rows đầu:")
            print(df.head(10).to_string())
            
            print("\n✅ File Excel đã sẵn sàng!")
            
        except Exception as e:
            print(f"\n❌ Lỗi đọc clipboard: {e}")
            print("\n💡 CÀI ĐẶT THÊM: pip install pyperclip")
        
        driver.quit()
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        print("\n💡 CÁCH NHANH NHẤT:")
        print("""
1. Mở Google Sheet trong Chrome
2. Đăng nhập email được cấp quyền
3. Nhấn Ctrl+A (chọn tất cả)
4. Nhấn Ctrl+C (copy)
5. Mở Excel
6. Nhấn Ctrl+V (paste)
7. Save as .xlsx

HOẶC dùng Apps Script:
- Extensions → Apps Script
- Copy code từ file google_apps_script.gs
        """)
        try:
            driver.quit()
        except:
            pass

if __name__ == '__main__':
    quet_sheet_bang_copy()
