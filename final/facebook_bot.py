# -*- coding: utf-8 -*-
"""
HỆ THỐNG FACEBOOK BOT TỰ ĐỘNG CẤP KEY - ULSA Automation
---------------------------------------------------
Mục tiêu: Khi khách nhắn MSSV, Bot tự động trả về Key trải nghiệm 24h.
Cần cài đặt: pip install flask requests
"""

import hashlib
import re
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

# ─────────────────────── CẤU HÌNH QUAN TRỌNG ───────────────────────

# 1. Lấy từ: developers.facebook.com -> Messenger -> Settings -> Access Tokens
PAGE_ACCESS_TOKEN = "DÁN_PAGE_ACCESS_TOKEN_CỦA_BẠN_VÀO_ĐÂY"

# 2. Bạn tự đặt (Phải khớp với chuỗi "Verify Token" khi cài Webhook trên FB)
VERIFY_TOKEN = "my_secret_token_ulsa"

# 3. Chữ ký bí mật (Phải trùng với Tool chính)
_SECRET = "ULSA_VXT_2026_#!@BAN_QUYEN_RIENG_TU"

# ──────────────────────── LOGIC TẠO KEY ──────────────────────────

def generate_key(masv: str, expire_date: str) -> str:
    """Tạo key bản quyền nhúng thông tin hạn sử dụng."""
    try:
        dt = datetime.strptime(expire_date, "%Y-%m-%d %H:%M:%S")
    except Exception:
        dt = datetime.now()
        
    hex_ts = f"{int(dt.timestamp()):08X}"
    raw = f"{masv.upper()}|{hex_ts}|{_SECRET}"
    h = hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
    return hex_ts + h

def send_message(recipient_id, message_text):
    """Gửi tin nhắn trả lời qua Facebook Graph API."""
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    resp = requests.post(url, json=payload)
    return resp.json()

# ──────────────────────── WEBHOOK HANDLER ────────────────────────

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # 1. Xác thực Webhook (Facebook Challenge)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ XÁC THỰC WEBHOOK THÀNH CÔNG!")
            return challenge, 200
        else:
            return "Forbidden", 403

    # 2. Xử lý tin nhắn (Facebook Push)
    if request.method == "POST":
        data = request.json
        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    # Lấy ID người gửi và nội dung tin nhắn
                    sender_id = messaging_event["sender"]["id"]
                    if "message" in messaging_event:
                        text = messaging_event["message"].get("text", "").strip()
                        print(f"📩 Nhận tin nhắn từ {sender_id}: {text}")

                        # Tìm MSSV trong tin nhắn (Ví dụ: Tìm chuỗi số từ 8-11 ký tự)
                        match = re.search(r'\b\d{8,11}\b', text)
                        if match:
                            masv = match.group(0)
                            
                            # Sinh Key 24h
                            expire_dt = datetime.now() + timedelta(days=1)
                            expire_str = expire_dt.strftime("%Y-%m-%d %H:%M:%S")
                            key = generate_key(masv, expire_str)
                            
                            reply = (f"🎉 Chào bạn! Đây là Key dùng thử 24h cho MSSV: {masv}\n\n"
                                     f"🔑 Key: {key}\n"
                                     f"📅 Hết hạn: {expire_str}\n\n"
                                     "Hãy copy Key và dán vào Tool để kích hoạt nhé!")
                            send_message(sender_id, reply)
                        else:
                            # Nếu tin nhắn không chứa MSSV
                            if "nội dung chào" not in text.lower():
                                send_message(sender_id, "Chào bạn! Để nhận Key dùng thử 1 ngày, vui lòng nhập Mã sinh viên của bạn (ví dụ: 211234567).")
            
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    # Chạy Webhook trên cổng 5000
    print("🚀 FB BOT WEBHOOK DANG KHOI DONG...")
    app.run(port=5000, debug=True)
