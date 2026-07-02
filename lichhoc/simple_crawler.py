#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple ULSA Schedule Crawler - Version đơn giản
Dành cho người mới bắt đầu
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime

def main():
    print("🎓 ULSA Schedule Crawler - Simple Version")
    print("=" * 50)
    
    # Thiết lập browser
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    
    try:
        # Bước 1: Mở trang đăng nhập ULSA
        print("🔗 Đang mở trang đăng nhập ULSA...")
        driver.get("http://sinhvien.ulsa.edu.vn/Login.aspx")
        driver.maximize_window()
        
        print("\n📋 QUY TRÌNH ĐĂNG NHẬP:")
        print("1. 🔐 Đăng nhập vào hệ thống ULSA")
        print("2. ✅ Đợi chuyển đến trang chính (SinhVien.aspx)")
        print("3. 🏠 Bạn sẽ thấy trang dashboard sinh viên")
        
        input("\n👉 Sau khi đăng nhập THÀNH CÔNG, nhấn Enter để tiếp tục...")
        
        # Bước 2: Mở tab mới với trang lịch học
        print("\n📅 Đang mở tab mới với trang lịch học...")
        driver.execute_script("window.open('http://sinhvien.ulsa.edu.vn/TraCuuLichHocSinhVien.aspx', '_blank');")
        
        # Chuyển sang tab mới
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)  # Đợi trang load
        
        print("✅ Đã mở tab mới với trang tra cứu lịch học")
        print("💡 Bây giờ bạn ở tab TraCuuLichHocSinhVien.aspx")
        print("📋 Lịch học sẽ tự động hiển thị!")
        print("⏰ Đợi 3 giây để trang load hoàn toàn...")
        time.sleep(3)  # Đợi thêm để trang load
        
        input("\n👉 Khi thấy bảng lịch học đã hiển thị, nhấn Enter để bắt đầu crawl...")
        
        # Tìm bảng lịch học với ưu tiên ID "grd"
        print("🔍 Đang tìm bảng lịch học...")
        time.sleep(2)
        
        table_found = False
        table_selector = ""
        
        # Thử tìm bảng theo thứ tự ưu tiên (dựa trên HTML thực tế ULSA)
        selectors = [
            ("grd", "ID: grd (Bảng chính ULSA)"),
            ("gvDSLopMo", "ID: gvDSLopMo"), 
            ("GridView1", "ID: GridView1")
        ]
        
        for selector, description in selectors:
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, f"#{selector} tr")
                if len(rows) > 1:
                    print(f"✅ Tìm thấy bảng: {description}")
                    table_selector = f"#{selector}"
                    table_found = True
                    break
            except:
                continue
        
        if not table_found:
            print("❌ Không tìm thấy bảng lịch học!")
            print("💡 Kiểm tra:")
            print("   - Đã đăng nhập thành công chưa?")
            print("   - Đang ở tab TraCuuLichHocSinhVien.aspx chưa?")
            print("   - Bảng đã load xong chưa?")
            return
        
        # Crawl dữ liệu với pagination (xử lý nhiều trang)
        print("📊 Bắt đầu crawl dữ liệu...")
        
        data = []
        page_count = 1
        
        while True:
            print(f"\n📄 Đang xử lý trang {page_count}...")
            
            # Lấy tất cả dòng từ trang hiện tại
            current_rows = driver.find_elements(By.CSS_SELECTOR, f"{table_selector} tr")
            print(f"📝 Tìm thấy {len(current_rows)} dòng (bao gồm header)")
            
            # Xử lý từng dòng (bỏ header)
            new_records = 0
            for i, row in enumerate(current_rows[1:], 1):  # Bỏ header
                cells = row.find_elements(By.TAG_NAME, "td")
                
                # Bỏ qua dòng pagination
                if "Trang sau" in row.text:
                    continue
                    
                if len(cells) >= 9:  # ULSA có 9 cột
                    # Xử lý dữ liệu trống
                    giao_vien = cells[6].text.strip()
                    if giao_vien == "" or giao_vien == "\u00a0":
                        giao_vien = "Chưa có thông tin"
                    
                    phong_hoc = cells[7].text.strip() 
                    if phong_hoc == "" or phong_hoc == "\u00a0":
                        phong_hoc = "Chưa có thông tin"
                    
                    data.append({
                        "STT": len(data) + 1,
                        "Mã học phần": cells[0].text.strip(),
                        "Tên học phần": cells[1].text.strip(), 
                        "Số tín chỉ": cells[2].text.strip(),
                        "Tên lớp tín chỉ": cells[3].text.strip(),
                        "Ca học": cells[4].text.strip().replace('\n', ' | '),
                        "Lịch học": cells[5].text.strip().replace('\n', ' | '),
                        "Giáo viên": giao_vien,
                        "Phòng học": phong_hoc,
                        "Còn trống": cells[8].text.strip(),
                        "Thời gian crawl": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    new_records += 1
            
            print(f"✅ Trang {page_count}: {new_records} môn học mới")
            
            # Tìm nút "Trang sau"
            try:
                next_link = driver.find_element(By.LINK_TEXT, "Trang sau")
                if next_link.is_displayed():
                    print("👆 Tìm thấy nút 'Trang sau', đang chuyển trang...")
                    next_link.click()
                    time.sleep(3)  # Đợi trang load
                    page_count += 1
                    
                    # Progress update
                    if len(data) % 20 == 0:
                        print(f"📈 Tổng đã crawl: {len(data)} môn học")
                else:
                    print("✅ Đã crawl hết tất cả các trang")
                    break
            except:
                print("✅ Không tìm thấy nút 'Trang sau' - Đã crawl hết")
                break
        
        if data:
            # Lưu Excel
            filename = f"lich_hoc_ulsa_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
            
            print(f"\n🎉 THÀNH CÔNG!")
            print(f"✅ Đã crawl {len(data)} môn học từ {page_count} trang")
            print(f"💾 Đã lưu vào: {filename}")
            print(f"📍 Vị trí: {filename}")
            
            # Hiển thị preview
            print("\n📋 Preview 5 môn đầu:")
            for i in range(min(5, len(data))):
                ma = data[i]['Mã học phần']
                ten = data[i]['Tên học phần']
                print(f"   {i+1}. {ma} - {ten}")
                
            if len(data) > 5:
                print(f"   ... và {len(data) - 5} môn khác")
        else:
            print("❌ Không có dữ liệu được crawl!")
            print("💡 Kiểm tra lại:")
            print("   - Bảng lịch học đã hiển thị chưa?")
            print("   - Có dữ liệu trong bảng không?")
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    finally:
        input("\n👉 Nhấn Enter để đóng browser và tất cả các tab...")
        # Đóng tất cả các tab
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        driver.quit()

if __name__ == "__main__":
    main()
