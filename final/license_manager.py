# -*- coding: utf-8 -*-
"""
Hệ thống quản lý bản quyền - ULSA Automation Tool
---------------------------------------------------
Cơ chế MỚI:
  - Bản quyền gắn theo: Mã Sinh Viên + Ngày Hết Hạn
  - Key = sha256(MASV + NGAYHH + SECRET)[:24].upper()
  - 1 Sinh viên có thể dùng trên nhiều máy.
"""

import hashlib
import json
import os
import requests
from datetime import datetime

# ★ Chữ ký bí mật của NGƯỜI BÁN - KHÔNG BAO GIỜ CHIA SẺ ★
_SECRET = "ULSA_VXT_2026_#!@BAN_QUYEN_RIENG_TU"

LICENSE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "license.dat")


# ─────────────────────── Lấy Thời Gian Thực ───────────────────────

def get_real_time() -> datetime:
    """Lấy thời gian từ máy tính cục bộ.
    Key đã được xác minh bằng SHA-256 nên không cần kiểm tra giờ internet."""
    return datetime.now()


# ─────────────────────── Tạo & Kiểm tra Key ───────────────────────

def generate_key(masv: str, expire_date: str) -> str:
    """
    Tạo key bản quyền nhúng thông tin hạn sử dụng.
    Cấu trúc: [8 ký tự Hex Timestamp][16 ký tự Hash]
    """
    try:
        if len(expire_date) > 10:
            dt = datetime.strptime(expire_date, "%Y-%m-%d %H:%M:%S")
        else:
            dt = datetime.strptime(expire_date, "%Y-%m-%d")
    except Exception:
        dt = datetime.now()
        
    hex_ts = f"{int(dt.timestamp()):08X}"
    raw = f"{masv.upper()}|{hex_ts}|{_SECRET}"
    h = hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
    return hex_ts + h


def verify_and_extract_key(masv: str, key: str) -> tuple[bool, str]:
    """Kiểm tra key và trích xuất ngày hết hạn. Trả về (True, expire_date_str) hoặc (False, '')"""
    key = key.upper().strip()
    if len(key) != 24:
        return False, ""
    
    hex_ts = key[:8]
    provided_hash = key[8:]
    
    expected_hash = hashlib.sha256(f"{masv.upper()}|{hex_ts}|{_SECRET}".encode()).hexdigest()[:16].upper()
    
    if provided_hash == expected_hash:
        try:
            ts = int(hex_ts, 16)
            expire_dt = datetime.fromtimestamp(ts)
            return True, expire_dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    return False, ""

def verify_key(masv: str, expire_date: str, key: str) -> bool:
    """Hàm giữ lại để tương thích ngược. Trả về True nếu Key hợp lệ."""
    ok, _ = verify_and_extract_key(masv, key)
    return ok


# ─────────────────────── Đọc / Ghi License File ───────────────────────

def save_license(masv: str, expire_date: str, key: str):
    """Lưu thông tin bản quyền vào license.dat."""
    data = {
        "masv": masv.upper(),
        "expire_date": expire_date,
        "key": key.upper().strip()
    }
    with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_license() -> dict | None:
    """Đọc file license.dat. Trả về dict hoặc None nếu không có hoặc lỗi."""
    if not os.path.exists(LICENSE_FILE):
        return None
    try:
        with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


# ─────────────────────── Hàm Kiểm tra Chính ───────────────────────

def check_license() -> dict:
    """
    Kiểm tra toàn bộ tính hợp lệ của bản quyền.
    Trả về dict:
      { 'valid': bool, 'masv': str, 'expire_date': str,
        'days_left': int, 'reason': str }
    """
    lic = load_license()

    if not lic:
        return {"valid": False, "masv": "", "expire_date": "", "days_left": 0,
                "reason": "Chưa có bản quyền"}

    # Kiểm tra Key & trích xuất lại ngày hết hạn chống giả mạo file dat
    ok, extracted_expire = verify_and_extract_key(lic["masv"], lic["key"])
    if not ok:
        return {"valid": False, "masv": "", "expire_date": "", "days_left": 0,
                "reason": "Key bản quyền không hợp lệ hoặc đã bị thay đổi"}
    
    lic["expire_date"] = extracted_expire

    # Kiểm tra thời hạn
    try:
        expire_dt = datetime.strptime(lic["expire_date"], "%Y-%m-%d %H:%M:%S")
    except Exception:
        return {"valid": False, "reason": "Định dạng ngày hết hạn lỗi"}
        
    now = get_real_time()
    # Tính toán chính xác thời gian còn lại
    diff = expire_dt - now
    days_left = diff.days

    if now >= expire_dt:
        return {"valid": False, "masv": lic["masv"], "expire_date": lic["expire_date"],
                "days_left": 0, "reason": "Bản quyền đã hết hạn"}

    return {
        "valid": True,
        "masv": lic["masv"],
        "expire_date": lic["expire_date"],
        "days_left": days_left,
        "reason": "OK"
    }


def activate(masv: str, expire_date: str, key: str) -> tuple[bool, str]:
    """
    Kích hoạt bản quyền. Vẫn nhận expire_date cho tương thích, 
    nhưng sẽ dùng ngày trích xuất từ Key làm chuẩn.
    """
    ok, extracted_expire = verify_and_extract_key(masv, key)
    if not ok:
        return False, "Mã kích hoạt không đúng. Vui lòng kiểm tra lại!"
    save_license(masv, extracted_expire, key)
    return True, extracted_expire

