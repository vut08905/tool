# -*- coding: utf-8 -*-
"""
★ TOOL TẠO KEY - CHỈ DÀNH CHO NGƯỜI BÁN ★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hướng dẫn:
  1. Mở CMD hoặc Terminal trong thư mục này
  2. Chạy: python tao_key.py
  3. Nhập Mã Máy và Mã SV của khách hàng
  4. Nhập số ngày cấp phép (1 ngày = 50.000đ)
  5. Copy KEY → gửi lại cho khách
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hashlib
from datetime import datetime, timedelta

# ★ PHẢI GIỐNG HOÀN TOÀN VỚI license_manager.py ★
_SECRET = "ULSA_VXT_2026_#!@BAN_QUYEN_RIENG_TU"


def generate_key(hwid: str, masv: str, expire_date: str) -> str:
    raw = f"{hwid}|{masv.upper()}|{expire_date}|{_SECRET}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24].upper()


def main():
    print("=" * 55)
    print("   🔑  TOOL TẠO KEY BẢN QUYỀN - ULSA AUTOMATION  ")
    print("   ★  CHỈ DÀNH CHO NGƯỜI BÁN - BẢO MẬT TUYỆT ĐỐI  ★")
    print("=" * 55)
    print()

    # Nhập thông tin
    hwid   = input("📟 Mã Máy Khách (HWID)  : ").strip().upper()
    masv   = input("🎓 Mã Sinh Viên         : ").strip().upper()

    print()
    so_ngay_str = input("📅 Số ngày kích hoạt (Mặc định: 1): ").strip()
    so_ngay = int(so_ngay_str) if so_ngay_str.isdigit() and int(so_ngay_str) > 0 else 1

    # Tính ngày hết hạn (từ ngày HÔM NAY, hết sau `so_ngay` ngày)
    expire_dt   = datetime.now() + timedelta(days=so_ngay)
    expire_date = expire_dt.strftime("%Y-%m-%d")

    # Tạo key
    key = generate_key(hwid, masv, expire_date)

    print()
    print("=" * 55)
    print(f"  📋 THÔNG TIN KEY ĐƯỢC TẠO")
    print("=" * 55)
    print(f"  Mã Máy    : {hwid}")
    print(f"  Mã SV     : {masv}")
    print(f"  Số ngày   : {so_ngay} ngày")
    print(f"  Hết hạn   : {expire_date}")
    print()
    print(f"  🔑 NGÀY HẾT HẠN : {expire_date}")
    print(f"  🔑 MÃ KÍCH HOẠT : {key}")
    print()
    print("  ➜ Gửi 2 thông tin trên cho khách!")
    print("=" * 55)

    os.system("pause")


if __name__ == "__main__":
    main()
