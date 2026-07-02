# -*- coding: utf-8 -*-
"""
TOOL TẠO KEY BẢN QUYỀN ĐỘC LẬP - ULSA Automation
---------------------------------------------------
Mục đích: Dùng để tích hợp với Fanpage FB Bot hoặc cấp Key nhanh.
Cách dùng:
  1. CLI: python standalone_keygen.py [MSSV] [SỐ NGÀY]
  2. Web server: python standalone_keygen.py server [CỬA]
"""

import hashlib
import json
import sys
import os
from datetime import datetime, timedelta
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# ★ CHỮ KÝ BÍ MẬT - PHẢI TRÙNG VỚI license_manager.py ★
_SECRET = "ULSA_VXT_2026_#!@BAN_QUYEN_RIENG_TU"

def generate_key(masv: str, expire_date: str) -> str:
    """Tạo key bản quyền nhúng thông tin hạn sử dụng."""
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

# ─────────────────────── WEB SERVER GIẢ LẬP API ───────────────────────

class KeygenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/gen":
            params = urllib.parse.parse_qs(parsed_path.query)
            
            masv = params.get("masv", [""])[0].strip().upper()
            days = params.get("days", ["1"])[0].strip()
            
            if not masv:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing 'masv' parameter")
                return

            try:
                days_int = int(days)
                expire_dt = datetime.now() + timedelta(days=days_int)
                expire_str = expire_dt.strftime("%Y-%m-%d %H:%M:%S")
                key = generate_key(masv, expire_str)
                
                response_data = {
                    "status": "success",
                    "masv": masv,
                    "expire": expire_str,
                    "key": key,
                    "msg": f"Key có hiệu lực trong {days_int} ngày."
                }
                
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
                
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Endpoint not found. Use /gen?masv=...&days=...")

def run_server(port=8000):
    server = HTTPServer(("0.0.0.0", port), KeygenHandler)
    print(f"🚀 SERVER DANG CHAY TAI: http://localhost:{port}")
    print(f"👉 API URL: http://localhost:{port}/gen?masv=MSSV_CUA_BAN&days=1")
    server.serve_forever()

# ─────────────────────── CHƯƠNG TRÌNH CHÍNH ───────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    
    # 1. Chế độ Server
    if len(args) >= 1 and args[0].lower() == "server":
        port = int(args[1]) if len(args) > 1 else 8000
        run_server(port)
        
    # 2. Chế độ CLI
    elif len(args) >= 1:
        masv = args[0].upper()
        days = int(args[1]) if len(args) > 1 else 1
        
        expire_dt = datetime.now() + timedelta(days=days)
        expire_str = expire_dt.strftime("%Y-%m-%d %H:%M:%S")
        key = generate_key(masv, expire_str)
        
        print(f"\n🔑 KEY CHO {masv} ({days} NGÀY):")
        print(f"📅 Hết hạn: {expire_str}")
        print(f"👉 {key}")
        print("------------------------------------------")
        
    else:
        print("\nHƯỚNG DẪN SỬ DỤNG STANDALONE KEYGEN:")
        print("1. CLI: python standalone_keygen.py [MSSV] [SỐ NGÀY]")
        print("   Ví dụ: python standalone_keygen.py 12345678 7")
        print("2. SERVER: python standalone_keygen.py server [CỬA CHỜ]")
        print("   Ví dụ: python standalone_keygen.py server 8000")
