"""
Quét nhiều phạm vi từ Google Sheet ra nhiều file Excel riêng biệt
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
        time.sleep(30)

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

def parse_range(range_str):
    """Parse range như A16:H425 thành start_col, start_row, end_col, end_row"""
    range_str = range_str.strip().upper()
    start_cell, end_cell = range_str.split(':')
    
    start_col = ''.join(c for c in start_cell if c.isalpha())
    start_row = int(''.join(c for c in start_cell if c.isdigit()))
    end_col = ''.join(c for c in end_cell if c.isalpha())
    end_row = int(''.join(c for c in end_cell if c.isdigit()))
    
    return start_col, start_row, end_col, end_row

def quet_mot_range(driver, name_box, formula_bar_selector, range_str, file_prefix):
    """Quét một phạm vi và lưu ra file Excel"""
    
    print(f"\n{'='*70}")
    print(f"📊 ĐANG QUÉT PHẠM VI: {range_str}")
    print(f"{'='*70}")
    
    start_col, start_row, end_col, end_row = parse_range(range_str)
    start_col_num = column_to_number(start_col)
    end_col_num = column_to_number(end_col)
    
    total_rows = end_row - start_row + 1
    total_cols = end_col_num - start_col_num + 1
    total_cells = total_rows * total_cols
    
    print(f"   ✓ Phạm vi: {start_col}{start_row}:{end_col}{end_row}")
    print(f"   ✓ Kích thước: {total_rows} rows x {total_cols} cols = {total_cells} cells")
    print(f"   ⏱️  Ước tính: ~{total_cells * 0.2 / 60:.1f} phút\n")
    
    # Tạo ma trận data
    data = []
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
                time.sleep(0.15)
                
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
        
        data.append(row_data)
    
    elapsed_time = (time.time() - start_time) / 60
    print(f"\n   ✅ Hoàn thành phạm vi này! Quét {processed} cells trong {elapsed_time:.1f} phút\n")
    
    # Loại bỏ rows rỗng cuối
    while data and not any(cell.strip() for cell in data[-1]):
        data.pop()
    
    if not data:
        print(f"   ⚠️  Không có dữ liệu trong phạm vi {range_str}")
        return None
    
    print(f"   📊 Tổng: {len(data)} rows có dữ liệu")
    
    # Chuyển sang DataFrame
    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=data[0])
    else:
        df = pd.DataFrame(data)
    
    # Lưu Excel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = f'{file_prefix}_{range_str.replace(":", "_")}_{timestamp}.xlsx'
    
    print(f"   💾 Đang lưu vào {excel_file}...")
    df.to_excel(excel_file, index=False, engine='openpyxl')
    
    print(f"   ✅ Đã lưu file: {excel_file}")
    print(f"   📊 Rows: {len(df)} | Columns: {len(df.columns)}")
    
    return excel_file

def quet_nhieu_range():
    print("="*70)
    print("🚀 QUÉT NHIỀU PHẠM VI TỪ GOOGLE SHEET")
    print("="*70)
    
    # Nhập URL
    print("\n📎 Nhập URL Google Sheet:")
    sheet_url = input("   → ").strip()
    
    if not sheet_url:
        print("❌ Chưa nhập URL!")
        return
    
    # Nhập các phạm vi
    print("\n📏 Nhập các phạm vi cần quét (cách nhau bởi dấu phẩy):")
    print("   Ví dụ: A16:H425, A893:H915")
    ranges_input = input("   → ").strip()
    
    if not ranges_input:
        print("❌ Chưa nhập phạm vi!")
        return
    
    # Parse ranges
    ranges = [r.strip() for r in ranges_input.split(',')]
    
    print(f"\n✅ Sẽ quét {len(ranges)} phạm vi:")
    for i, r in enumerate(ranges, 1):
        print(f"   {i}. {r}")
    
    print("\n⏳ Đang khởi động Chrome...")
    
    # Setup Chrome
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    try:
        # Bật chống sleep
        prevent_sleep()
        awake_thread = threading.Thread(target=keep_awake, daemon=True)
        awake_thread.start()
        print("   ✓ Đã bật chế độ chống sleep màn hình")
        
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
        
        # Formula Bar selector
        formula_bar_selector = (
            'div.cell-input[role="combobox"], '
            'div.cell-input[contenteditable], '
            '#t-formula-bar-input, '
            'div[id*="formula"]'
        )
        
        # Quét từng phạm vi
        excel_files = []
        total_start_time = time.time()
        
        for i, range_str in enumerate(ranges, 1):
            print(f"\n{'='*70}")
            print(f"📍 PHẠM VI {i}/{len(ranges)}")
            print(f"{'='*70}")
            
            excel_file = quet_mot_range(
                driver, 
                name_box, 
                formula_bar_selector, 
                range_str, 
                f'sheet_part{i}'
            )
            
            if excel_file:
                excel_files.append(excel_file)
        
        total_elapsed = (time.time() - total_start_time) / 60
        
        # Tổng kết
        print("\n" + "="*70)
        print("✅ HOÀN THÀNH TẤT CẢ!")
        print("="*70)
        print(f"⏱️  Tổng thời gian: {total_elapsed:.1f} phút")
        print(f"📁 Đã tạo {len(excel_files)} file Excel:")
        
        for i, file in enumerate(excel_files, 1):
            print(f"   {i}. {file}")
            # Mở file Excel
            try:
                os.startfile(file)
                print(f"      ✓ Đã mở file")
            except:
                pass
        
        print("\n" + "="*70)
        print("⚠️  QUAN TRỌNG:")
        print("   - Chrome VẪN ĐANG MỞ để bạn kiểm tra")
        print("   - Tất cả file Excel đã được mở")
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
    quet_nhieu_range()
