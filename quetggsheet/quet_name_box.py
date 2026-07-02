"""
Quét Google Sheet bằng cách:
1. Nhập địa chỉ cell vào Name Box (vd: A1, B5, H1083)
2. Lấy dữ liệu từ Formula Bar
3. Lưu vào Excel
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
import os
import ctypes
import threading

# Chống sleep màn hình Windows
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def prevent_sleep():
    """Chống máy tính sleep khi quét"""
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
        print("   ✓ Đã bật chế độ chống sleep màn hình")
    except:
        pass

def allow_sleep():
    """Cho phép máy tính sleep lại"""
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    except:
        pass

def keep_awake():
    """Thread chạy ngầm để giữ màn hình không sleep"""
    while True:
        prevent_sleep()
        time.sleep(30)  # Refresh mỗi 30 giây

def column_to_number(col):
    """Chuyển cột A, B, AA... thành số"""
    num = 0
    for char in col:
        num = num * 26 + (ord(char.upper()) - ord('A') + 1)
    return num

def number_to_column(num):
    """Chuyển số thành cột A, B, AA..."""
    result = ""
    while num > 0:
        num -= 1
        result = chr(num % 26 + ord('A')) + result
        num //= 26
    return result

def quet_bang_name_box():
    print("="*70)
    print("🚀 QUÉT GOOGLE SHEET BẰNG NAME BOX + FORMULA BAR")
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
    
    try:
        # Bật chống sleep
        prevent_sleep()
        
        # Khởi động thread giữ màn hình sáng
        awake_thread = threading.Thread(target=keep_awake, daemon=True)
        awake_thread.start()
        
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 15)
        print("✅ Chrome đã mở!")
        
        # Đăng nhập
        print("\n🌐 Mở Google để đăng nhập...")
        driver.get("https://accounts.google.com")
        
        print("\n" + "="*70)
        print("👤 VUI LÒNG:")
        print("   1. Đăng nhập Google bằng email được cấp quyền")
        print("   2. Nhấn Enter sau khi đăng nhập xong")
        print("="*70)
        input("\n👉 Nhấn Enter... ")
        
        # Mở Sheet
        print(f"\n📊 Đang mở Google Sheet...")
        driver.get(sheet_url)
        
        print("\n" + "="*70)
        print("📋 VUI LÒNG:")
        print("   1. Chờ sheet load xong hoàn toàn")
        print("   2. Nhấn Enter để bắt đầu quét")
        print("="*70)
        input("\n👉 Nhấn Enter... ")
        
        time.sleep(3)
        
        # Tìm Name Box
        print("\n🔍 Đang tìm Name Box...")
        name_box = None
        
        try:
            name_box = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input#t-name-box, input.waffle-name-box')
            ))
            print("   ✓ Đã tìm thấy Name Box!")
        except:
            print("   ❌ Không tìm thấy Name Box!")
            driver.quit()
            return
        
        # Tìm Formula Bar
        print("🔍 Đang tìm Formula Bar...")
        formula_bar_selector = (
            'div.cell-input[role="combobox"], '
            'div.cell-input[contenteditable], '
            '#t-formula-bar-input, '
            'div[id*="formula"]'
        )
        
        # Xác định phạm vi quét
        print("\n📏 Xác định phạm vi dữ liệu:")
        print("   Nhập phạm vi (vd: A1:Z100) hoặc Enter để tự động")
        range_input = input("   → ").strip().upper()
        
        if range_input and ':' in range_input:
            # Parse range
            start_cell, end_cell = range_input.split(':')
            start_col = ''.join(c for c in start_cell if c.isalpha())
            start_row = int(''.join(c for c in start_cell if c.isdigit()))
            end_col = ''.join(c for c in end_cell if c.isalpha())
            end_row = int(''.join(c for c in end_cell if c.isdigit()))
        else:
            # Tự động detect - thử vài cells để tìm phạm vi
            print("   🔍 Đang tự động phát hiện phạm vi...")
            start_col = 'A'
            start_row = 1
            end_col = 'Z'
            end_row = 100
            
            # Thử tìm cell cuối cùng có data
            test_ranges = [10, 50, 100, 500, 1000]
            for test_row in test_ranges:
                name_box.clear()
                name_box.send_keys(f'A{test_row}')
                name_box.send_keys(Keys.RETURN)
                time.sleep(0.3)
                
                try:
                    formula_bar = driver.find_element(By.CSS_SELECTOR, formula_bar_selector)
                    if formula_bar.text.strip():
                        end_row = test_row + 50
                    else:
                        break
                except:
                    break
        
        start_col_num = column_to_number(start_col)
        end_col_num = column_to_number(end_col)
        
        total_cells = (end_row - start_row + 1) * (end_col_num - start_col_num + 1)
        
        print(f"\n   ✓ Phạm vi: {start_col}{start_row}:{end_col}{end_row}")
        print(f"   ✓ Tổng: {end_row - start_row + 1} rows x {end_col_num - start_col_num + 1} cols = {total_cells} cells")
        print(f"   ⏱️  Ước tính: ~{total_cells * 0.2 / 60:.1f} phút\n")
        
        input("👉 Nhấn Enter để bắt đầu quét... ")
        
        # Tạo ma trận data
        data = []
        
        print("\n📥 Đang quét dữ liệu...\n")
        
        processed = 0
        start_time = time.time()
        
        for row in range(start_row, end_row + 1):
            row_data = []
            
            for col_num in range(start_col_num, end_col_num + 1):
                col = number_to_column(col_num)
                cell_address = f'{col}{row}'
                
                try:
                    # Nhập địa chỉ vào Name Box
                    name_box.clear()
                    name_box.send_keys(cell_address)
                    name_box.send_keys(Keys.RETURN)
                    time.sleep(0.15)  # Đợi formula bar update
                    
                    # Lấy dữ liệu từ Formula Bar
                    try:
                        formula_bar = driver.find_element(By.CSS_SELECTOR, formula_bar_selector)
                        cell_value = formula_bar.text.strip()
                    except:
                        cell_value = ''
                    
                    row_data.append(cell_value)
                    
                except Exception as e:
                    row_data.append('')
                
                processed += 1
                
                # Hiển thị progress
                if processed % 20 == 0:
                    percent = (processed / total_cells) * 100
                    elapsed = time.time() - start_time
                    speed = processed / elapsed if elapsed > 0 else 0
                    eta = (total_cells - processed) / speed if speed > 0 else 0
                    
                    print(f"   ⏳ {cell_address}: {processed}/{total_cells} ({percent:.1f}%) - ETA: {eta/60:.1f}m")
            
            # Thêm TẤT CẢ rows, kể cả rỗng (để quét đúng phạm vi)
            data.append(row_data)
        
        print(f"\n   ✅ Hoàn thành! Đã quét {processed} cells trong {(time.time() - start_time)/60:.1f} phút\n")
        
        if not data:
            print("❌ Không có dữ liệu!")
            input("\n👉 Nhấn Enter để đóng...")
            allow_sleep()
            driver.quit()
            return
        
        # Loại bỏ rows rỗng cuối
        while data and not any(cell.strip() for cell in data[-1]):
            data.pop()
        
        print(f"📊 Tổng cộng: {len(data)} rows (đã loại bỏ rows rỗng cuối)")
        
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
        
        print(f"\n📄 Preview:")
        print(df.head(10).to_string())
        
        print("\n✅ File Excel đã sẵn sàng!")
        
        # Mở file Excel tự động
        print(f"\n📂 Đang mở file Excel...")
        try:
            os.startfile(excel_file)
            print("   ✓ Đã mở Excel!")
        except Exception as e:
            print(f"   ⚠️  Không thể tự động mở: {e}")
            print(f"   💡 Mở thủ công: {os.path.abspath(excel_file)}")
        
        print("\n" + "="*70)
        print("⚠️  QUAN TRỌNG:")
        print("   - Chrome VẪN ĐANG MỞ để bạn kiểm tra")
        print("   - File Excel đã được mở")
        print("   - Kiểm tra dữ liệu xem đã đủ chưa")
        print("   - Nhấn Enter để đóng Chrome")
        print("="*70)
        
        input("\n👉 Nhấn Enter để đóng Chrome... ")
        
        allow_sleep()
        driver.quit()
        print("\n✅ Đã đóng Chrome. Hoàn tất!")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
        
        input("\n👉 Nhấn Enter để đóng...")
        
        allow_sleep()
        try:
            driver.quit()
        except:
            pass

if __name__ == '__main__':
    quet_bang_name_box()
