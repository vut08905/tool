#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple ULSA Schedule Crawler
Dựa trên script gốc của bạn, được cải tiến thêm
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
from datetime import datetime

def main():
    print("🎓 SIMPLE ULSA SCHEDULE CRAWLER")
    print("Dựa trên script gốc - Đơn giản và hiệu quả!")
    print("=" * 50)
    
    # Setup Chrome driver
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--disable-logging')
    options.add_argument('--silent')
    
    try:
        driver = webdriver.Chrome(options=options)
        print("✅ Đã khởi tạo Chrome driver thành công")
    except Exception as e:
        print(f"❌ Lỗi khởi tạo driver: {e}")
        print("💡 Hãy đảm bảo Chrome và ChromeDriver đã được cài đặt")
        return

    try:
        # Bước 1: Mở trang login trong tab mới
        print("\n🔗 Đang mở trang ULSA trong tab mới...")
        driver.execute_script("window.open('http://sinhvien.ulsa.edu.vn/TraCuuLichHocSinhVien.aspx', '_blank');")
        
        # Chuyển sang tab mới
        driver.switch_to.window(driver.window_handles[-1])
        driver.maximize_window()
        
        print("✅ Đã mở tab mới với trang lịch học ULSA")
        
        print("\n📋 HƯỚNG DẪN:")
        print("1. 🔐 Đăng nhập vào hệ thống ULSA (trong tab mới)")
        print("2. 📅 Chọn học kỳ cần crawl dữ liệu")
        print("3. 🔍 Nhấn nút 'Tra cứu' để hiển thị bảng")
        print("4. ⏰ Đợi bảng lịch học hiển thị hoàn toàn")
        print("💡 Tab mới sẽ giúp bạn thấy dữ liệu rõ ràng hơn!")
        print("\n🎯 Dựa trên dữ liệu thực từ ULSA, script đã được tối ưu!")
        
        input("\n👉 Khi bảng đã hiện ra rõ ràng trong tab mới, nhấn Enter để bắt đầu lấy dữ liệu...")

        # Bước 2: Tìm bảng lịch học
        print("\n🔍 Đang tìm bảng lịch học...")
        
        # Kiểm tra bảng với ID "grd" (từ dữ liệu thực)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "grd"))
            )
            print("✅ Tìm thấy bảng lịch học với ID 'grd' (đúng cấu trúc ULSA)")
            table_id = "grd"
            table_found = True
        except TimeoutException:
            print("❌ Không tìm thấy bảng với ID 'grd'")
            
            # Fallback: thử các selector khác
            table_selectors = [
                ("gvDSLopMo", "ID: gvDSLopMo"),
                ("GridView1", "ID: GridView1")
            ]
            
            table_found = False
            for selector, description in table_selectors:
                try:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.ID, selector))
                    )
                    print(f"✅ Tìm thấy bảng: {description}")
                    table_id = selector
                    table_found = True
                    break
                except TimeoutException:
                    print(f"❌ Không tìm thấy: {description}")
                    continue
        
        if not table_found:
            print("❌ Không tìm thấy bảng lịch học. Kiểm tra lại:")
            print("   - Đã đăng nhập thành công chưa?")
            print("   - Đã chọn học kỳ chưa?")
            print("   - Đã nhấn 'Tra cứu' chưa?")
            return

        # Bước 3: Thu thập dữ liệu từ bảng
        print(f"\n📊 Bắt đầu thu thập dữ liệu từ bảng #{table_id}...")
        data = []
        page_count = 1

        while True:
            print(f"\n📄 Đang xử lý trang {page_count}...")
            start_count = len(data)  # Đếm số môn học trước khi xử lý trang này
            
            # Lấy tất cả các dòng trong bảng
            rows = driver.find_elements(By.CSS_SELECTOR, f"#{table_id} tr")
            print(f"📝 Số dòng tìm được: {len(rows)} (bao gồm header)")

            # Xử lý từng dòng (bỏ qua header và pagination)
            for idx, row in enumerate(rows):
                # Bỏ qua header (dòng đầu tiên)
                if idx == 0:  
                    continue
                    
                cols = row.find_elements(By.TAG_NAME, "td")
                
                # Kiểm tra xem có phải dòng pagination không
                row_text = row.text.strip()
                if "Trang sau" in row_text or len(cols) < 9:
                    continue
                
                # Đảm bảo có đúng 9 cột như cấu trúc thực của ULSA
                if len(cols) >= 9:
                    # Lấy dữ liệu từ các cột theo cấu trúc thực
                    ma_hoc_phan = cols[0].text.strip()
                    ten_hoc_phan = cols[1].text.strip()
                    so_tin_chi = cols[2].text.strip()
                    ten_lop_tin_chi = cols[3].text.strip()
                    ca_hoc = cols[4].text.strip().replace('\n', ' | ')
                    lich_hoc = cols[5].text.strip().replace('\n', ' | ')
                    
                    # Xử lý cột Giáo viên (có thể trống với &nbsp;)
                    giao_vien = cols[6].text.strip()
                    if giao_vien == "" or giao_vien == "\u00a0" or giao_vien == "&nbsp;":
                        giao_vien = "Chưa có thông tin"
                    
                    # Xử lý cột Phòng học (có thể trống với &nbsp;)
                    phong_hoc = cols[7].text.strip()
                    if phong_hoc == "" or phong_hoc == "\u00a0" or phong_hoc == "&nbsp;":
                        phong_hoc = "Chưa có thông tin"
                    
                    con_trong = cols[8].text.strip()
                    
                    # Tạo record dữ liệu
                    row_data = {
                        "STT": len(data) + 1,
                        "Mã học phần": ma_hoc_phan,
                        "Tên học phần": ten_hoc_phan,
                        "Số tín chỉ": so_tin_chi,
                        "Tên lớp tín chỉ": ten_lop_tin_chi,
                        "Ca học": ca_hoc,
                        "Lịch học": lich_hoc,
                        "Giáo viên": giao_vien,
                        "Phòng học": phong_hoc,
                        "Còn trống": con_trong,
                        "Ngày crawl": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    data.append(row_data)
                    
                    # Progress update mỗi 10 môn
                    if len(data) % 10 == 0:
                        print(f"   📈 Đã xử lý {len(data)} môn học...")
                        print(f"   📌 Môn mới nhất: {ma_hoc_phan} - {ten_hoc_phan}")

            current_count = len(data) - start_count
            print(f"✅ Trang {page_count}: {current_count} môn học mới")

            # Tìm nút "Trang sau" để chuyển trang
            try:
                print("🔍 Đang tìm nút 'Trang sau'...")
                next_found = False
                
                # Tìm link "Trang sau" theo cấu trúc thực của ULSA
                try:
                    next_link = driver.find_element(By.LINK_TEXT, "Trang sau")
                    href = next_link.get_attribute("href")
                    
                    if next_link.is_displayed() and "javascript:__doPostBack" in str(href):
                        print("👆 Tìm thấy nút 'Trang sau', đang chuyển trang...")
                        
                        # Click vào link "Trang sau"
                        driver.execute_script("arguments[0].click();", next_link)
                        time.sleep(4)  # Đợi trang load
                        
                        # Kiểm tra xem có chuyển trang thành công không
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, table_id))
                        )
                        
                        next_found = True
                        print("✅ Chuyển trang thành công!")
                        
                except NoSuchElementException:
                    print("❌ Không tìm thấy link 'Trang sau'")
                
                if not next_found:
                    print("✅ Đã crawl hết tất cả các trang - Hoàn thành!")
                    break
                    
                page_count += 1
                
            except Exception as e:
                print(f"⚠️ Lỗi khi tìm nút chuyển trang: {e}")
                print("💡 Có thể đã hết trang hoặc lỗi mạng")
                break

        # Bước 4: Ghi ra file Excel
        if data:
            # Tạo tên file với timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lich_hoc_ulsa_simple_{timestamp}.xlsx"
            
            # Tạo DataFrame và lưu
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False, sheet_name='Lịch học')
            
            print(f"\n🎉 THÀNH CÔNG!")
            print(f"✅ Đã lưu {len(data)} môn học vào: {filename}")
            print(f"📊 Tổng số trang đã crawl: {page_count}")
            
            # Hiển thị preview
            print(f"\n📋 Preview 5 môn đầu tiên:")
            for i in range(min(5, len(data))):
                ma = data[i]["Mã học phần"]
                ten = data[i]["Tên học phần"]
                print(f"   {i+1}. {ma} - {ten}")
                
        else:
            print("❌ Không có dữ liệu nào được lấy!")
            print("💡 Kiểm tra:")
            print("   - Đã bấm 'Tra cứu' và bảng đã hiển thị chưa?")
            print("   - Bảng có dữ liệu không?")

    except KeyboardInterrupt:
        print("\n⚠️ Người dùng dừng crawl")
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
    finally:
        input("\n👉 Nhấn Enter để đóng browser và tất cả các tab...")
        # Đóng tất cả các tab
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        driver.quit()

if __name__ == "__main__":
    main()
