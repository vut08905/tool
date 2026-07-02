"""
Cách đơn giản nhất: Copy dữ liệu từ Google Sheet ra Excel
Không cần cài đặt gì phức tạp
"""

import pandas as pd
import json
from datetime import datetime

def tu_json_ra_excel(json_file='sheet_data.json', excel_file='output.xlsx'):
    """
    Chuyển data từ JSON (đã copy từ Google Sheet) sang Excel
    """
    try:
        # Đọc JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("❌ File JSON rỗng!")
            return
        
        # Chuyển sang DataFrame
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
        else:
            df = pd.DataFrame(data)
        
        # Lưu ra Excel
        df.to_excel(excel_file, index=False, engine='openpyxl')
        
        print(f"✅ Đã lưu {len(df)} rows vào {excel_file}")
        print(f"\nCột: {list(df.columns)}")
        print(f"\nPreview 5 rows đầu:")
        print(df.head())
        
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file {json_file}")
        print("\n📋 HƯỚNG DẪN:")
        print("1. Mở Google Sheet")
        print("2. Bôi đen toàn bộ dữ liệu (Ctrl+A)")
        print("3. Copy (Ctrl+C)")
        print("4. Mở Excel mới")
        print("5. Paste (Ctrl+V)")
        print("6. Save as Excel (.xlsx)")
        print("\nHoặc dùng function nhap_thu_cong() để nhập data trực tiếp")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")


def nhap_thu_cong():
    """
    Nhập dữ liệu thủ công và lưu Excel
    """
    print("📝 NHẬP DỮ LIỆU THỦ CÔNG")
    print("Paste toàn bộ dữ liệu từ Google Sheet (Copy từ sheet)")
    print("Nhấn Enter 2 lần để kết thúc\n")
    
    lines = []
    empty_count = 0
    
    while True:
        try:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                # Tách theo tab (khi copy từ Google Sheets)
                lines.append(line.split('\t'))
        except EOFError:
            break
    
    if not lines:
        print("❌ Không có dữ liệu!")
        return
    
    # Tạo DataFrame
    df = pd.DataFrame(lines[1:], columns=lines[0])
    
    # Lưu Excel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = f'google_sheet_data_{timestamp}.xlsx'
    df.to_excel(excel_file, index=False, engine='openpyxl')
    
    print(f"\n✅ Đã lưu {len(df)} rows vào {excel_file}")
    print(df.head())


def tu_url_google_sheet(sheet_url):
    """
    Lấy dữ liệu trực tiếp từ Google Sheet URL (nếu sheet công khai)
    """
    try:
        # Chuyển URL thành export format
        if '/edit' in sheet_url:
            # https://docs.google.com/spreadsheets/d/ID/edit
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            export_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
            
            print(f"📥 Đang tải từ: {export_url}")
            
            # Đọc trực tiếp bằng pandas
            df = pd.read_csv(export_url)
            
            # Lưu Excel
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            excel_file = f'google_sheet_{sheet_id[:8]}_{timestamp}.xlsx'
            df.to_excel(excel_file, index=False, engine='openpyxl')
            
            print(f"✅ Đã lưu {len(df)} rows vào {excel_file}")
            print(f"\nCột: {list(df.columns)}")
            print(f"\nPreview:")
            print(df.head())
            
            return excel_file
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print("\n⚠️ Sheet có thể không công khai hoặc bị khóa.")
        print("Thử cách thủ công:")
        print("1. Mở Google Sheet")
        print("2. File → Download → CSV hoặc Excel")
        print("3. Hoặc copy paste dữ liệu vào Excel trực tiếp")


def menu():
    """Menu chọn cách thức"""
    print("\n" + "="*60)
    print("🔍 QUÉT GOOGLE SHEET RA EXCEL")
    print("="*60)
    print("\n📌 CHỌN CÁCH THỨC:\n")
    print("1️⃣  Nhập URL Google Sheet (nếu sheet công khai)")
    print("2️⃣  Copy/Paste dữ liệu thủ công")
    print("3️⃣  Chuyển file JSON có sẵn sang Excel")
    print("4️⃣  Hướng dẫn copy thủ công (NHANH NHẤT)")
    print("\n0️⃣  Thoát")
    print("="*60)
    
    choice = input("\n👉 Chọn (1-4): ").strip()
    
    if choice == '1':
        url = input("\n📎 Nhập URL Google Sheet: ").strip()
        tu_url_google_sheet(url)
        
    elif choice == '2':
        nhap_thu_cong()
        
    elif choice == '3':
        json_file = input("\n📄 Nhập tên file JSON (Enter = sheet_data.json): ").strip()
        if not json_file:
            json_file = 'sheet_data.json'
        excel_file = input("📄 Tên file Excel output (Enter = output.xlsx): ").strip()
        if not excel_file:
            excel_file = 'output.xlsx'
        tu_json_ra_excel(json_file, excel_file)
        
    elif choice == '4':
        print("\n" + "="*60)
        print("📋 CÁCH NHANH NHẤT (KHÔNG CẦN CODE)")
        print("="*60)
        print("""
1. Mở Google Sheet mà bạn có quyền xem
2. Bôi đen toàn bộ dữ liệu:
   - Nhấn Ctrl+A (chọn tất cả)
   - Hoặc click ô góc trái để chọn toàn bộ
   
3. Copy dữ liệu:
   - Nhấn Ctrl+C
   
4. Mở Excel mới:
   - Mở Microsoft Excel
   - Tạo workbook mới
   
5. Paste dữ liệu:
   - Nhấn Ctrl+V
   - Chọn "Keep source formatting" nếu được hỏi
   
6. Save as Excel:
   - File → Save As
   - Chọn định dạng .xlsx
   - Đặt tên và lưu

✅ XONG! Không cần code gì cả!
        """)
        print("="*60)
        
    else:
        print("\n👋 Thoát!")
        return


if __name__ == '__main__':
    # Chạy menu
    menu()
    
    # Hoặc gọi trực tiếp:
    # tu_url_google_sheet('URL_GOOGLE_SHEET_CUA_BAN')
    # nhap_thu_cong()
    # tu_json_ra_excel('sheet_data.json', 'output.xlsx')
