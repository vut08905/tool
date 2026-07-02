"""
Quét Google Sheet bằng cách click từng ô và lấy data từ formula bar
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import time

def quet_tu_formula_bar():
    print("="*70)
    print("🚀 QUÉT GOOGLE SHEET TỪ FORMULA BAR")
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
        wait = WebDriverWait(driver, 10)
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
        print("   2. Nhấn Enter để bắt đầu quét")
        print("="*70)
        input("\n👉 Nhấn Enter để bắt đầu quét... ")
        
        print("\n⏳ Đang phân tích cấu trúc sheet...")
        time.sleep(2)
        
        # Tìm số rows và columns
        print("   🔍 Đang tìm số hàng và cột...")
        
        # Thử nhiều selector khác nhau
        cells = driver.find_elements(By.CSS_SELECTOR, 'div[role="gridcell"]')
        
        if not cells:
            print("   🔄 Thử selector khác...")
            cells = driver.find_elements(By.CSS_SELECTOR, '[role="gridcell"]')
        
        if not cells:
            print("   🔄 Thử selector khác...")
            cells = driver.find_elements(By.CSS_SELECTOR, '.cell')
        
        if not cells:
            print("❌ Không tìm thấy cells!")
            print("\n💡 Thử scroll xuống trong sheet và nhấn Enter...")
            input("👉 Nhấn Enter để thử lại... ")
            
            cells = driver.find_elements(By.CSS_SELECTOR, 'div[role="gridcell"], [role="gridcell"]')
        
        if not cells:
            print("❌ Vẫn không tìm thấy cells!")
            print("\n📋 Sheet có thể đang ở chế độ xem đặc biệt.")
            print("💡 Dùng Apps Script sẽ dễ hơn (xem file APPS_SCRIPT_CODE.gs)")
            driver.quit()
            return
        
        # Tìm max row và col
        max_row = 0
        max_col = 0
        cell_positions = []
        
        for cell in cells:
            try:
                aria_row = cell.get_attribute('aria-rowindex')
                aria_col = cell.get_attribute('aria-colindex')
                
                if aria_row and aria_col:
                    row = int(aria_row)
                    col = int(aria_col)
                    
                    max_row = max(max_row, row)
                    max_col = max(max_col, col)
                    cell_positions.append((row, col, cell))
            except:
                continue
        
        print(f"   ✓ Phát hiện: {max_row} rows x {max_col} columns")
        print(f"   ✓ Tổng {len(cell_positions)} cells\n")
        
        if max_row == 0 or max_col == 0:
            print("❌ Không xác định được kích thước sheet!")
            driver.quit()
            return
        
        # Tạo ma trận data
        data = [['' for _ in range(max_col)] for _ in range(max_row)]
        
        print("📥 Bắt đầu quét từng ô...")
        print(f"   (Có thể mất vài phút cho {len(cell_positions)} cells)\n")
        
        processed = 0
        
        # Quét từng cell
        for row, col, cell in cell_positions:
            try:
                # Click vào cell
                cell.click()
                time.sleep(0.1)  # Đợi formula bar update
                
                # Lấy data từ formula bar
                try:
                    formula_bar = driver.find_element(By.CSS_SELECTOR, 
                        'div.cell-input[role="combobox"], div.cell-input[contenteditable], #t-formula-bar-input')
                    cell_value = formula_bar.text.strip()
                except:
                    # Nếu không tìm thấy formula bar, lấy text từ cell
                    cell_value = cell.text.strip()
                
                # Lưu vào ma trận (convert về 0-indexed)
                data[row - 1][col - 1] = cell_value
                
                processed += 1
                
                # Hiển thị progress
                if processed % 50 == 0:
                    percent = (processed / len(cell_positions)) * 100
                    print(f"   ⏳ {processed}/{len(cell_positions)} cells ({percent:.1f}%)")
                
            except Exception as e:
                # Nếu lỗi, bỏ qua cell này
                continue
        
        print(f"\n   ✅ Đã quét xong {processed} cells!\n")
        
        # Loại bỏ rows rỗng
        cleaned_data = []
        for row in data:
            if any(cell.strip() for cell in row):
                cleaned_data.append(row)
        
        if not cleaned_data:
            print("❌ Không có dữ liệu!")
            driver.quit()
            return
        
        print(f"📊 Tổng cộng: {len(cleaned_data)} rows có dữ liệu")
        
        # Chuyển sang DataFrame
        if len(cleaned_data) > 1:
            df = pd.DataFrame(cleaned_data[1:], columns=cleaned_data[0])
        else:
            df = pd.DataFrame(cleaned_data)
        
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
        
        driver.quit()
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            driver.quit()
        except:
            pass

if __name__ == '__main__':
    quet_tu_formula_bar()
