"""
Script tự động: Mở Chrome → Bạn đăng nhập → Quét sheet → Lưu Excel
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
from datetime import datetime
import time

def quet_sheet():
    print("="*70)
    print("🚀 QUÉT GOOGLE SHEET RA EXCEL")
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
        print("   2. Nhấn Enter để bắt đầu quét dữ liệu")
        print("="*70)
        input("\n👉 Nhấn Enter để bắt đầu quét... ")
        
        print("\n⏳ Đang quét dữ liệu...")
        time.sleep(3)
        
        # Scroll xuống để load hết data
        print("   📜 Đang scroll để load toàn bộ...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        
        while scroll_count < 20:  # Giới hạn 20 lần scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            scroll_count += 1
            if new_height == last_height:
                break
            last_height = new_height
            print(f"      → Scroll lần {scroll_count}...")
        
        print("   ✓ Đã scroll xong!\n")
        
        # Quét dữ liệu bằng JavaScript
        print("   🔍 Đang trích xuất dữ liệu...")
        
        script = """
        // Lấy dữ liệu từ Google Sheets cells
        var data = [];
        var rowMap = {};
        
        // Tìm tất cả các cells có class chứa data
        var cells = document.querySelectorAll('div[role="gridcell"], div[role="columnheader"], div[role="rowheader"]');
        
        cells.forEach(function(cell) {
            try {
                // Lấy vị trí row và column
                var row = cell.getAttribute('aria-rowindex');
                var col = cell.getAttribute('aria-colindex');
                
                if (row && col) {
                    var rowNum = parseInt(row);
                    var colNum = parseInt(col);
                    
                    // Lấy text
                    var text = cell.innerText || cell.textContent || '';
                    text = text.trim();
                    
                    // Lưu vào map
                    if (!rowMap[rowNum]) {
                        rowMap[rowNum] = {};
                    }
                    rowMap[rowNum][colNum] = text;
                }
            } catch(e) {}
        });
        
        // Chuyển map thành array 2D
        var maxRow = Math.max(...Object.keys(rowMap).map(Number));
        var maxCol = 0;
        
        for (var r in rowMap) {
            var cols = Object.keys(rowMap[r]).map(Number);
            maxCol = Math.max(maxCol, ...cols);
        }
        
        // Tạo mảng data
        for (var r = 1; r <= maxRow; r++) {
            var rowData = [];
            for (var c = 1; c <= maxCol; c++) {
                if (rowMap[r] && rowMap[r][c] !== undefined) {
                    rowData.push(rowMap[r][c]);
                } else {
                    rowData.push('');
                }
            }
            if (rowData.some(cell => cell !== '')) {
                data.push(rowData);
            }
        }
        
        return data;
        """
        
        data = driver.execute_script(script)
        
        # Nếu cách 1 không được, thử cách 2
        if not data or len(data) == 0:
            print("   🔄 Thử phương pháp khác...")
            
            script2 = """
            var data = [];
            
            // Thử tìm table
            var tables = document.querySelectorAll('table');
            if (tables.length > 0) {
                var rows = tables[0].querySelectorAll('tr');
                rows.forEach(function(row) {
                    var rowData = [];
                    var cells = row.querySelectorAll('td, th');
                    cells.forEach(function(cell) {
                        rowData.push((cell.innerText || cell.textContent || '').trim());
                    });
                    if (rowData.length > 0) {
                        data.push(rowData);
                    }
                });
            }
            
            // Nếu không có table, tìm grid
            if (data.length === 0) {
                var grid = document.querySelector('[role="grid"]');
                if (grid) {
                    var rows = grid.querySelectorAll('[role="row"]');
                    rows.forEach(function(row) {
                        var rowData = [];
                        var cells = row.querySelectorAll('[role="gridcell"], [role="columnheader"]');
                        cells.forEach(function(cell) {
                            rowData.push((cell.innerText || cell.textContent || '').trim());
                        });
                        if (rowData.length > 0 && rowData.some(c => c !== '')) {
                            data.push(rowData);
                        }
                    });
                }
            }
            
            return data;
            """
            
            data = driver.execute_script(script2)
        
        if not data or len(data) == 0:
            print("\n❌ Không lấy được dữ liệu!")
            print("\n💡 THỬ CÁCH KHÁC:")
            print("   Cách 1: Extensions → Apps Script (xem file google_apps_script.gs)")
            print("   Cách 2: Ctrl+A → Ctrl+C → Paste vào Excel")
            driver.quit()
            return
        
        print(f"   ✓ Đã lấy {len(data)} rows!\n")
        
        # Xử lý data - loại bỏ rows rỗng
        cleaned_data = []
        for row in data:
            if any(cell.strip() for cell in row):  # Bỏ rows toàn rỗng
                cleaned_data.append(row)
        
        if len(cleaned_data) == 0:
            print("❌ Dữ liệu rỗng sau khi làm sạch!")
            driver.quit()
            return
        
        print(f"📊 Tổng cộng: {len(cleaned_data)} rows có dữ liệu")
        
        # Tìm số cột tối đa
        max_cols = max(len(row) for row in cleaned_data)
        
        # Chuẩn hóa: thêm cells rỗng nếu row thiếu cột
        for row in cleaned_data:
            while len(row) < max_cols:
                row.append('')
        
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
        
        print("\n✅ File Excel đã sẵn sàng để sử dụng!")
        
        driver.quit()
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        print("\n💡 GIẢI PHÁP:")
        print("""
1. Đảm bảo Chrome đã cài đặt
2. Kiểm tra URL có đúng không
3. Thử cách Apps Script (dễ hơn):
   - Mở sheet → Extensions → Apps Script
   - Copy code từ file google_apps_script.gs
        """)
        try:
            driver.quit()
        except:
            pass

if __name__ == '__main__':
    quet_sheet()
