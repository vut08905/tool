# -*- coding: utf-8 -*-
"""
GUI tổng hợp - Tất cả chức năng trong 1 màn hình
Bao gồm: Nhập tài khoản, Chọn lớp, Theo dõi tiến trình, Pause/Resume
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import sys
import subprocess
import threading
import time
from datetime import datetime, timedelta
import pandas as pd
from fuzzywuzzy import fuzz, process
import re
import requests
import urllib.parse
import io
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False
import license_manager

# ─────────────────── Thông tin ngân hàng người bán ───────────────────
BANK_BIN   = "970418"   # BIDV
BANK_STK   = "96247VUXUANTOAN"
BANK_NAME  = "VU XUAN TOAN"
BANK_STK_CHECK = "8818325418" # Số tài khoản thực để gọi API SePay (BIDV)
GIA_TIEN   = 50000      # VNĐ
SO_NGAY    = 1          # Ngày hết hạn gốc
APP_VERSION = "4.3"     # Phiên bản cứng của bản Build này
CLOUD_URL  = "https://gist.githubusercontent.com/vutoan412002/676ef281d1f67d86710038ba4ee1eee0/raw/ulsa_config.json"
SEPAY_API_KEY = "EZ0I9WV4CSDW3WSYEBMY0N9HABRRPUKQO2NZZGCS78AS38TXROILHLO6FCN1ZJDY"

# Đọc cấu hình local nếu Admin đã từng lưu
_cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_config.json")
if os.path.exists(_cfg_path):
    try:
        with open(_cfg_path, "r", encoding="utf-8") as f:
            _cnf = json.load(f)
            GIA_TIEN = int(_cnf.get("gia_tien", GIA_TIEN))
            SO_NGAY  = int(_cnf.get("so_ngay", SO_NGAY))
            CLOUD_URL = _cnf.get("url", CLOUD_URL)
    except Exception: pass


# ═══════════════════════════════════════════════════════════════
#  MÀN HÌNH KÍCH HOẠT BẢN QUYỀN
# ═══════════════════════════════════════════════════════════════
class LicenseWindow:
    """Cửa sổ kích hoạt bản quyền hiện ra trước khi mở Tool chính."""

    def __init__(self, root_tk, on_activated_callback):
        self.root = root_tk
        self.on_activated = on_activated_callback
        self._qr_img = None  # giữ tham chiếu để không bị GC xóa
        self._checking_status = False

        self.win = tk.Toplevel(root_tk)
        self.win.title("🔑 Kích Hoạt Bản Quyền - ULSA Automation")
        self.win.geometry("600x750")
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)
        self.win.grab_set()  # Chặn tương tác với cửa sổ phía sau
        self.win.configure(bg="#1a1a2e")

        self._build_ui()
        self._load_cloud_config()

    def _load_cloud_config(self):
        """Tải cấu hình Cloud ngầm và đè lên giao diện"""
        if not CLOUD_URL: return
        def fetch():
            global GIA_TIEN, SO_NGAY
            try:
                import time
                import math
                
                # Hàm check url trả về JSON với requests, bỏ qua SSL verification
                url = f"{CLOUD_URL}?t={int(time.time())}"
                resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, verify=False, timeout=15)
                data = resp.json()
                
                if "gia_tien" in data:
                    GIA_TIEN = int(data["gia_tien"])
                if "so_ngay" in data:
                    SO_NGAY = int(data["so_ngay"])
                
                # Cập nhật nhãn Giá tiền trên Main Thread
                label_text = f"ULSA Automation Tool  ·  {GIA_TIEN:,.0f} đ / {SO_NGAY} ngày"
                self.win.after(0, lambda: self.price_label.config(text=label_text))
                
                # Check thông báo khóa app bản cũ
                my_ver = APP_VERSION
                cloud_ver = data.get("version", my_ver)
                update_url = data.get("update_url", "")
                if cloud_ver != my_ver:
                    msg = data.get("thong_bao", f"Đã có phiên bản {cloud_ver}. Vui lòng tải bản mới để dùng tiếp!")
                    self.win.after(0, lambda m=msg, u=update_url: self._show_update_block(m, u))
                    return

                # Check thông báo thường - CHỈ hiện nếu phần nội dung RIÊNG biệt với thông báo cập nhật
                # (không hiện khi đúng phiên bản – đã tắt thông báo kilosaurusnhau)
                notice = data.get("thong_bao", "").strip()
                # Tắt hoàn toàn thông báo nếu đúng phiên bản - chỉ show khi có phiên bản khác
                    
                # Reload QR nếu Mã Sinh Viên đã nhập (để update số tiền mới)
                masv = self.masv_var.get().strip()
                if len(masv) >= 5:
                    self.win.after(0, lambda: self._on_masv_change(None))
            except Exception: pass
            
        threading.Thread(target=fetch, daemon=True).start()

    def _show_update_block(self, msg, update_url):
        if not update_url:
            messagebox.showerror("Bảo trì / Cập nhật", msg, parent=self.win)
            self.root.destroy()
            return

        up_win = tk.Toplevel(self.win)
        up_win.title("Có Phiên Bản Mới!")
        up_win.geometry("400x230")
        up_win.resizable(False, False)
        up_win.configure(bg="#1a1a2e")
        up_win.grab_set()
        
        # Ép tắt tool nếu tắt cửa sổ update
        up_win.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())

        tk.Label(up_win, text="🚀 PHÁT HIỆN BẢN CẬP NHẬT",
                 font=("Segoe UI", 12, "bold"), fg="#e94560", bg="#1a1a2e").pack(pady=(15, 5))
        
        tk.Label(up_win, text=msg, font=("Segoe UI", 10), fg="#eaeaea", bg="#1a1a2e",
                 wraplength=350, justify="center").pack(pady=5)

        import tkinter.ttk as ttk
        prog_style = ttk.Style()
        prog_style.theme_use('default')
        prog_style.configure("TProgressbar", thickness=10)
        
        prog = ttk.Progressbar(up_win, orient="horizontal", length=300, mode="determinate", style="TProgressbar")
        prog.pack(pady=10)
        
        lbl_status = tk.Label(up_win, text="Vui lòng bấm nút để cập nhật...", fg="#aaa", bg="#1a1a2e", font=("Segoe UI", 9))
        lbl_status.pack()

        def do_update():
            btn.config(state="disabled")
            lbl_status.config(text="Đang tải dữ liệu. Vui lòng không tắt App...")
            
            def download_thread():
                import sys
                import subprocess
                
                current_exe = sys.executable
                if not current_exe.lower().endswith(".exe"):
                    self.win.after(0, lambda: messagebox.showerror("Lỗi Update", "Chức năng này chỉ chạy trên file .exe đã đóng gói!", parent=up_win))
                    self.win.after(0, lambda: btn.config(state="normal"))
                    self.win.after(0, lambda: lbl_status.config(text="Lỗi môi trường (Chưa build EXE)."))
                    return
                
                try:
                    new_exe = os.path.join(os.path.dirname(current_exe), "__update_temp.exe")
                    
                    with requests.get(update_url, headers={'User-Agent': 'ULSA/1.0'}, stream=True, timeout=15, verify=False) as r:
                        r.raise_for_status()
                        file_size = int(r.headers.get('Content-Length', 0))
                        
                        down_bytes = 0
                        block_size = 8192
                        
                        with open(new_exe, "wb") as f:
                            for chunk in r.iter_content(chunk_size=block_size):
                                if chunk:
                                    f.write(chunk)
                                    down_bytes += len(chunk)
                                    if file_size > 0:
                                        percent = int((down_bytes * 100) / file_size)
                                        self.win.after(0, lambda p=percent: prog.config(value=p))
                                        self.win.after(0, lambda p=percent: lbl_status.config(text=f"Đang tải... {p}%"))

                    # Tạo file bat để thay thế (Mở terminal riêng biệt minh bạch)
                    bat_path = os.path.join(os.path.dirname(current_exe), "updater.bat")
                    bat_content = f'''@echo off
cd /d "%~dp0"
title Auto Updater - DangKyTinChi
color 0A
echo ==========================================
echo   HE THONG DANG CAP NHAT PHIEN BAN MOI!
echo ==========================================
echo  Xin vui long doi giay lat. Khong duoc tat!
echo.
:loop
ping 127.0.0.1 -n 2 > nul
del "{current_exe}" >nul 2>&1
if exist "{current_exe}" goto loop
ren "{new_exe}" "{os.path.basename(current_exe)}"
explorer "{current_exe}"
del "%~f0"'''
                    with open(bat_path, "w", encoding="utf-8") as bf:
                        bf.write(bat_content)
                    
                    self.win.after(0, lambda: lbl_status.config(text="Đang khởi động lại ứng dụng..."))
                    
                    os.startfile(bat_path)
                    self.win.after(500, lambda: self.root.destroy())
                    
                except Exception as e:
                    self.win.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi tải cập nhật:\n{e}", parent=up_win))
                    self.win.after(0, lambda: btn.config(state="normal"))
                    self.win.after(0, lambda: lbl_status.config(text="Tải thất bại."))

            threading.Thread(target=download_thread, daemon=True).start()

        btn = tk.Button(up_win, text="🚀 BẮT ĐẦU CẬP NHẬT", font=("Segoe UI", 10, "bold"), fg="white", bg="#4ade80",
                        activebackground="#22c55e", cursor="hand2", command=do_update, relief="flat")
        btn.pack(pady=10, ipadx=10, ipady=4)
        
    def _build_ui(self):
        bg       = "#1a1a2e"
        card_bg  = "#16213e"
        accent   = "#0f3460"
        gold     = "#e94560"
        text_col = "#eaeaea"
        green    = "#4ade80"

        # ── Tiêu đề ──
        tk.Label(self.win, text="🔐 KÍCH HOẠT BẢN QUYỀN",
                 font=("Segoe UI", 16, "bold"), fg=gold, bg=bg
                 ).pack(pady=(18, 2))
                 
        self.price_label = tk.Label(self.win, text=f"ULSA Automation Tool  ·  {GIA_TIEN:,.0f} đ / {SO_NGAY} ngày",
                                    font=("Segoe UI", 10), fg="#aaa", bg=bg)
        self.price_label.pack(pady=(0, 12))

        # ── Card Mã Máy ──
        card = tk.Frame(self.win, bg=card_bg, bd=0, highlightbackground="#0f3460",
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(card, text="🎓  Mã sinh viên của bạn:",
                 font=("Segoe UI", 9), fg="#aaa", bg=card_bg
                 ).pack(anchor="w", padx=12, pady=(10, 2))

        self.masv_var = tk.StringVar()
        masv_entry = tk.Entry(card, textvariable=self.masv_var,
                              font=("Segoe UI", 12, "bold"), bg="#0d1b2a", fg=green,
                              bd=0, relief="flat", justify="center")
        masv_entry.pack(fill="x", padx=12, pady=(0, 10), ipady=6)
        masv_entry.bind("<KeyRelease>", self._on_masv_change)

        # ── QR Code ──
        qr_label_title = tk.Label(self.win, text="📱  Quét QR để chuyển khoản:",
                                  font=("Segoe UI", 9), fg="#aaa", bg=bg)
        qr_label_title.pack(anchor="w", padx=24)

        self.qr_label = tk.Label(self.win, bg=bg, text="← Nhập mã sinh viên\nđể hiển thị mã QR",
                                 fg="#555", font=("Segoe UI", 10))
        self.qr_label.pack(pady=4)

        # ── Nút Tự Động Kích Hoạt ──
        self.auto_btn = tk.Button(
            self.win, text="🚀  KIỂM TRA THANH TOÁN (Tự Động)",
            font=("Segoe UI", 10, "bold"), fg="#1a1a2e", bg=green,
            activebackground="#22c55e", activeforeground="white",
            relief="flat", cursor="hand2",
            command=self._check_payment
        )
        self.auto_btn.pack(fill="x", padx=24, pady=(5, 10), ipady=8)

        # ── Card Nhập Key ──
        card3 = tk.Frame(self.win, bg=card_bg, bd=0, highlightbackground="#0f3460",
                         highlightthickness=1)
        card3.pack(fill="x", padx=24, pady=(6, 0))

        tk.Label(card3, text="🔑  Hoặc nhập mã kích hoạt (nếu có):",
                 font=("Segoe UI", 9), fg="#aaa", bg=card_bg
                 ).pack(anchor="w", padx=12, pady=(10, 2))

        expire_row = tk.Frame(card3, bg=card_bg)
        expire_row.pack(fill="x", padx=12, pady=(0, 4))
        tk.Label(expire_row, text="Ngày HH (YYYY-MM-DD):",
                 font=("Segoe UI", 9), fg="#aaa", bg=card_bg).pack(side="left")
        self.expire_var = tk.StringVar()
        tk.Entry(expire_row, textvariable=self.expire_var,
                 font=("Segoe UI", 11), bg="#0d1b2a", fg=text_col,
                 bd=0, relief="flat", width=14, justify="center"
                 ).pack(side="left", padx=8, ipady=4)

        self.key_var = tk.StringVar()
        key_entry = tk.Entry(card3, textvariable=self.key_var,
                             font=("Consolas", 11), bg="#0d1b2a", fg=gold,
                             bd=0, relief="flat", justify="center")
        key_entry.pack(fill="x", padx=12, pady=(0, 10), ipady=6)

        # ── Nút Kích Hoạt Thủ Công ──
        activate_btn = tk.Button(
            self.win, text="✅  XÁC NHẬN MÃ KEY",
            font=("Segoe UI", 10, "bold"), fg="white", bg="#0f3460",
            activebackground="#16213e", activeforeground="white",
            relief="flat", cursor="hand2",
            command=self._activate
        )
        activate_btn.pack(fill="x", padx=24, pady=(12, 4), ipady=8)

        tk.Label(self.win,
                 text="Sau khi chuyển khoản, hãy bấm nút xanh để tự động mở khóa.\nSử dụng BIDV - VU XUAN TOAN - " + BANK_STK,
                 font=("Segoe UI", 8), fg="#555", bg=bg, justify="center"
                 ).pack(pady=(0, 10))

    def _on_masv_change(self, event=None):
        """Cập nhật mã QR khi người dùng nhập mã sinh viên."""
        masv = self.masv_var.get().strip()
        if len(masv) < 3:
            self.qr_label.config(image="", text="← Nhập mã sinh viên để hiển thị mã QR",
                                 fg="#555", font=("Segoe UI", 10))
            return
        # Định dạng nội dung: ULSA [MASV]
        noi_dung = f"ULSA {masv.upper()}"
        self._load_qr(noi_dung)

    def _load_qr(self, noi_dung: str):
        """Tải QR code từ VietQR API và hiển thị."""
        if not PIL_OK:
            self.qr_label.config(
                text=f"QR: Chuyển {GIA_TIEN:,}đ\nSTK: {BANK_STK}\nBIDV - {BANK_NAME}\nNội dung: {noi_dung}",
                fg="#4ade80", font=("Consolas", 9), image="")
            return

        def fetch():
            try:
                # Dùng giao diện BIDV: 970418
                url = (f"https://img.vietqr.io/image/{BANK_BIN}-{BANK_STK}-compact2.png"
                       f"?amount={GIA_TIEN}&addInfo={urllib.parse.quote(noi_dung)}"
                       f"&accountName={urllib.parse.quote(BANK_NAME)}")
                resp = requests.get(url, timeout=6)
                data = resp.content
                img   = Image.open(io.BytesIO(data)).resize((200, 200))
                photo = ImageTk.PhotoImage(img)
                self._qr_img = photo  # giữ tham chiếu
                self.qr_label.config(image=photo, text="")
            except Exception:
                self.qr_label.config(
                    text=f"STK: {BANK_STK}  ·  BIDV\n{BANK_NAME}\nSố tiền: {GIA_TIEN:,}đ\nNội dung: {noi_dung}",
                    fg="#4ade80", font=("Consolas", 8), image="")

        threading.Thread(target=fetch, daemon=True).start()

    def _check_payment(self):
        """Gọi API SePay để tự động kiểm tra thanh toán."""
        if self._checking_status: return
        
        masv = self.masv_var.get().strip().upper()
        if not masv:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Mã Sinh Viên để kiểm tra!", parent=self.win)
            return

        self._checking_status = True
        self.auto_btn.config(text="⏳ Đang kiểm tra...", state="disabled")
        
        def run_check():
            try:
                # Gọi API SePay v2 (userapi.sepay.vn)
                url = f"https://userapi.sepay.vn/v2/transactions?account_number={BANK_STK_CHECK}&limit=500"
                print(f"[Debug-VXT-V2] Calling SePay: {url}")
                
                headers = {
                    "Authorization": f"Bearer {SEPAY_API_KEY}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                resp = requests.get(url, headers=headers, timeout=10)
                res_body = resp.text
                print(f"[Debug] SePay Response: {res_body}")
                res_data = resp.json()
                
                # SePay v2: status="success", mảng dữ liệu nằm trong "data"
                if res_data.get("status") != "success":
                    raise Exception(res_data.get("messages", "Lỗi phản hồi từ SePay (v2)"))

                transactions = res_data.get("data", [])
                print(f"[Debug] Tìm thấy {len(transactions)} giao dịch.")
                found_valid = False
                
                for tx in transactions:
                    # SePay v2 dùng amount_in và transaction_content
                    amount  = float(tx.get("amount_in", 0) or tx.get("amount", 0))
                    content = tx.get("transaction_content", "").upper()
                    
                    if (amount >= GIA_TIEN and 
                        masv in content and
                        "ULSA" in content):
                        
                        # Thành công! Tính toán Key bản quyền (24 giờ tính từ khi chuyển khoản)
                        tx_date_str = tx.get("transaction_date", "")
                        try:
                            # SePay v2 format: "2026-03-26 17:38:53"
                            tx_dt = datetime.strptime(tx_date_str, "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            # Fallback nếu lỗi định dạng → dùng giờ hiện tại
                            tx_dt = datetime.now()

                        expire_dt = tx_dt + timedelta(days=SO_NGAY)

                        # Bỏ qua giao dịch quá cũ (thời gian hết hạn <= thời gian thực hiện tại)
                        if expire_dt <= license_manager.get_real_time():
                            continue
                        
                        expire_str = expire_dt.strftime("%Y-%m-%d %H:%M:%S")
                        key = license_manager.generate_key(masv, expire_str)
                        
                        # Kích hoạt luôn
                        success, reason = license_manager.activate(masv, expire_str, key)
                        if success:
                            found_valid = True
                            self.win.after(0, lambda m=masv, e=expire_str: self._on_auto_success(m, e))
                            break
                
                if not found_valid:
                    # Kiểm tra xem có gần đây có giao dịch nhưng số tiền không khớp
                    self.win.after(0, lambda: messagebox.showinfo(
                        "Chưa tìm thấy", 
                        f"⏳ Hệ thống chưa tìm thấy giao dịch chuyển khoản {GIA_TIEN:,.0f}đ với nội dung:\n"
                        f"ULSA {masv}\n\n"
                        "ℹ️ Nếu bạn đang gia hạn (tài khoản hết hạn), vui lòng chuyển khoản với nội dung \"ULSA {masv}\" sau đó bam nút kiểm tra lại.\n\n"
                        "Nếu bạn vừa chuyển, vui lòng đợi 1-2 phút rồi bấm lại!", 
                        parent=self.win))

            except Exception as e:
                self.win.after(0, lambda ex=e: messagebox.showerror("Lỗi", f"Lỗi kiểm tra: {str(ex)}", parent=self.win))
            finally:
                self._checking_status = False
                self.win.after(0, lambda: self.auto_btn.config(text="🚀  KIỂM TRA THANH TOÁN (Tự Động)", state="normal"))

        threading.Thread(target=run_check, daemon=True).start()

    def _on_auto_success(self, masv, expire_date):
        messagebox.showinfo("🎉 Kích Hoạt Tự Đụng!", 
                            f"Đã xác nhận thanh toán! Hệ thống đã tự động kích hoạt.\n"
                            f"Mã SV: {masv}\n"
                            f"Hết hạn: {expire_date}", parent=self.win)
        self.win.destroy()
        self.on_activated(masv)

    def _activate(self):
        import hashlib as _hl
        masv        = self.masv_var.get().strip()
        expire_date = self.expire_var.get().strip()
        key         = self.key_var.get().strip()

        # ── Kiểm tra Admin bí mật (SHA256, không lưu pw thô) ──
        _ADMIN_MASV  = "e6aca6c948ccc606e7d2a88beaa47b7e310225dfe03f2e9e3c8f606121adf3ba"
        _ADMIN_DATE  = "f2dde83d6e76822cd287d31dcbc8883908d5a2627b0446b2708db1ecf71d4840"
        _ADMIN_KEY   = "9483037705192d58256ee7d1a200dfeb346a407b47debac74b21e7cd8d23323d"

        def _h(s): return _hl.sha256(s.encode()).hexdigest()

        if (_h(masv) == _ADMIN_MASV and
            _h(expire_date) == _ADMIN_DATE and
            _h(key) == _ADMIN_KEY):
            # Mở trang Admin – ẩn cửa sổ kích hoạt
            self.win.withdraw()
            AdminWindow(self.root, on_close_callback=lambda: self.win.deiconify())
            return

        if not masv:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Mã Sinh Viên!", parent=self.win)
            return
        # Bỏ kiểm tra expire_date vì giờ lấy từ Key
        if not key:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Mã Kích Hoạt!", parent=self.win)
            return

        ok, reason = license_manager.activate(masv, expire_date, key)
        if ok:
            # Kiểm tra xem mã này tuy đúng chữ ký nhưng có bị hết hạn ở quá khứ hay không
            res = license_manager.check_license()
            if not res["valid"]:
                messagebox.showerror("❌ Đã hết hạn", f"Mã hợp lệ nhưng đã hết hạn!\nChi tiết: {res['reason']}", parent=self.win)
                import os
                if os.path.exists(license_manager.LICENSE_FILE):
                    try:
                        os.remove(license_manager.LICENSE_FILE)
                    except: pass
                return
                
            messagebox.showinfo("🎉 Thành Công!",
                                f"Kích hoạt bản quyền thành công!\n"
                                f"Mã SV: {masv.upper()}\n"
                                f"Hết hạn: {reason}",
                                parent=self.win)
            self.win.destroy()
            self.on_activated(masv.upper())
        else:
            messagebox.showerror("❌ Kích Hoạt Thất Bại", reason, parent=self.win)

    def _on_close(self):
        """Đóng cửa sổ kích hoạt → thoát hẳn ứng dụng."""
        self.root.destroy()


# ═══════════════════════════════════════════════════════════════
#  MÀN HÌNH ADMIN BÍ MẬT
# ═══════════════════════════════════════════════════════════════
class AdminWindow:
    """Cửa sổ quản trị Admin ẩn - Chỉ Admin mới biết cách vào."""

    CLOUD_CFG_URL = "https://gist.githubusercontent.com/vutoan412002/676ef281d1f67d86710038ba4ee1eee0/raw/ulsa_config.json"
    # ↑ Link gốc để đọc Cloud config

    def __init__(self, root_tk, on_close_callback=None):
        self.root = root_tk
        self.on_close = on_close_callback

        self.win = tk.Toplevel(root_tk)
        self.win.title("⚙️ ULSA Admin Panel")
        self.win.geometry("700x580")
        self.win.resizable(False, False)
        self.win.configure(bg="#0d1117")
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)
        self.win.grab_set()

        self._build_ui()
        self._load_cloud_config()

    # ─────────────── UI ───────────────
    def _build_ui(self):
        bg     = "#0d1117"
        card   = "#161b22"
        accent = "#238636"
        txt    = "#c9d1d9"
        red    = "#da3633"

        header = tk.Frame(self.win, bg="#161b22", pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="⚙️  ULSA ADMIN PANEL",
                 font=("Consolas", 16, "bold"), bg="#161b22", fg="#58a6ff").pack()
        tk.Label(header, text="🔒  Khu vực bảo mật – Chỉ quản trị viên",
                 font=("Consolas", 9), bg="#161b22", fg="#8b949e").pack()

        nb = ttk.Notebook(self.win)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # ── Tab 1: Sinh Key ──
        t1 = tk.Frame(nb, bg=bg)
        nb.add(t1, text="  🔑 Sinh Key thủ công  ")
        self._build_keygen_tab(t1, bg, card, accent, txt)

        # ── Tab 2: Cấu hình Cloud ──
        t2 = tk.Frame(nb, bg=bg)
        nb.add(t2, text="  ☁️ Cấu hình Cloud  ")
        self._build_cloud_tab(t2, bg, card, accent, txt)

        # ── Tab 3: Danh sách Key đã cấp ──
        t3 = tk.Frame(nb, bg=bg)
        nb.add(t3, text="  📋 Lịch sử Key  ")
        self._build_history_tab(t3, bg, card, txt)

        # Close button
        tk.Button(self.win, text="❌  Đóng Admin Panel", command=self._on_close,
                  bg=red, fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=10, pady=5).pack(pady=(0, 10))

    def _build_keygen_tab(self, parent, bg, card, accent, txt):
        """Tab sinh Key thủ công cho bất kỳ Mã SV nào."""
        frm = tk.Frame(parent, bg=card, padx=20, pady=20)
        frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def lbl(text, bold=False):
            tk.Label(frm, text=text,
                     font=("Segoe UI", 10, "bold" if bold else "normal"),
                     bg=card, fg=txt).pack(anchor="w", pady=(6, 0))

        lbl("🎓  Mã Sinh Viên người nhận Key:", bold=True)
        self.gen_masv = tk.Entry(frm, font=("Consolas", 12), bg="#21262d", fg="#79c0ff",
                                 insertbackground="white", relief="flat")
        self.gen_masv.pack(fill=tk.X, pady=4)

        lbl("📅  Ngày hết hạn (YYYY-MM-DD HH:MM:SS):", bold=True)
        self.gen_expire = tk.Entry(frm, font=("Consolas", 12), bg="#21262d", fg="#79c0ff",
                                   insertbackground="white", relief="flat")
        # Gợi ý: 1 ngày từ bây giờ
        default_exp = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        self.gen_expire.insert(0, default_exp)
        self.gen_expire.pack(fill=tk.X, pady=4)

        # Shortcut: nhanh N ngày
        quick = tk.Frame(frm, bg=card)
        quick.pack(anchor="w", pady=4)
        tk.Label(quick, text="⚡ Nhanh: ", bg=card, fg="#8b949e",
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        for d, label in [(1, "1 ngày"), (7, "7 ngày"), (30, "30 ngày"), (365, "1 năm")]:
            day = d
            tk.Button(quick, text=label, font=("Segoe UI", 9), bg="#21262d", fg="#79c0ff",
                      relief="flat", padx=6, pady=2, cursor="hand2",
                      command=lambda x=day: self._set_days(x)).pack(side=tk.LEFT, padx=3)

        tk.Button(frm, text="⚙️  SINH KEY", command=self._generate_key,
                  bg=accent, fg="white", font=("Segoe UI", 11, "bold"),
                  relief="flat", padx=10, pady=8, cursor="hand2").pack(fill=tk.X, pady=12)

        lbl("📋  Key sinh ra (Gửi cho người dùng):", bold=True)
        self.gen_result = tk.Text(frm, height=3, font=("Consolas", 11), bg="#21262d",
                                  fg="#3fb950", insertbackground="white", relief="flat",
                                  state="disabled")
        self.gen_result.pack(fill=tk.X, pady=4)

        tk.Button(frm, text="📋 Copy Key", command=self._copy_key,
                  bg="#30363d", fg=txt, font=("Segoe UI", 9),
                  relief="flat", padx=8, pady=4, cursor="hand2").pack(anchor="e")

    def _build_cloud_tab(self, parent, bg, card, accent, txt):
        """Tab xem và lưu cấu hình Cloud."""
        frm = tk.Frame(parent, bg=card, padx=20, pady=20)
        frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def row(label, var_name, default=""):
            tk.Label(frm, text=label, bg=card, fg=txt,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8,0))
            e = tk.Entry(frm, font=("Consolas", 11), bg="#21262d", fg="#79c0ff",
                         insertbackground="white", relief="flat")
            e.insert(0, default)
            e.pack(fill=tk.X, pady=3)
            setattr(self, var_name, e)

        row("💰  Giá tiền (VNĐ):", "cfg_gia", str(GIA_TIEN))
        row("📅  Số ngày cấp mặc định:", "cfg_ngay", "1")
        row("🏷️  Phiên bản hiện tại (vd: 1.2):", "cfg_ver", "1.2")
        row("🔗  URL Cloud Config (GitHub Gist raw):", "cfg_url", self.CLOUD_CFG_URL)

        tk.Label(frm, text="📢  Thông báo bảo trì (để trống = không thông báo):",
                 bg=card, fg=txt, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8,0))
        self.cfg_notice = tk.Text(frm, height=3, font=("Consolas", 10), bg="#21262d",
                                  fg="#f0e68c", insertbackground="white", relief="flat")
        self.cfg_notice.pack(fill=tk.X, pady=3)

        btn_row = tk.Frame(frm, bg=card)
        btn_row.pack(fill=tk.X, pady=10)
        tk.Button(btn_row, text="☁️  Tải lại từ Cloud", command=self._load_cloud_config,
                  bg="#21262d", fg=txt, font=("Segoe UI", 9),
                  relief="flat", padx=8, cursor="hand2").pack(side=tk.LEFT, padx=(0,8))
        tk.Button(btn_row, text="💾  Lưu vào máy (Local)", command=self._save_local_config,
                  bg=accent, fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=8, cursor="hand2").pack(side=tk.LEFT)

        self.cloud_status = tk.Label(frm, text="", bg=card, fg="#8b949e",
                                     font=("Consolas", 9))
        self.cloud_status.pack(anchor="w", pady=4)

    def _build_history_tab(self, parent, bg, card, txt):
        """Tab xem lịch sử Key đã sinh ra."""
        frm = tk.Frame(parent, bg=bg)
        frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = ("Thời gian", "Mã SV", "Hết hạn", "Key")
        self.hist_tree = ttk.Treeview(frm, columns=cols, show="headings")
        for c in cols:
            self.hist_tree.heading(c, text=c)
            self.hist_tree.column(c, width=150 if c != "Key" else 220)

        vsb = ttk.Scrollbar(frm, orient="vertical", command=self.hist_tree.yview)
        self.hist_tree.configure(yscrollcommand=vsb.set)
        self.hist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._load_key_history()

    # ─────────────── Logic ───────────────
    def _set_days(self, days: int):
        exp = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        self.gen_expire.delete(0, tk.END)
        self.gen_expire.insert(0, exp)

    def _generate_key(self):
        masv   = self.gen_masv.get().strip().upper()
        expire = self.gen_expire.get().strip()
        if not masv or not expire:
            messagebox.showwarning("Thiếu", "Vui lòng nhập Mã SV và Ngày hết hạn!", parent=self.win)
            return
        key = license_manager.generate_key(masv, expire)
        # Hiển thị
        self.gen_result.config(state="normal")
        self.gen_result.delete("1.0", tk.END)
        self.gen_result.insert("1.0", key)
        self.gen_result.config(state="disabled")
        # Lưu lịch sử
        self._save_key_history(masv, expire, key)
        self._load_key_history()

    def _copy_key(self):
        key = self.gen_result.get("1.0", tk.END).strip()
        if key:
            self.win.clipboard_clear()
            self.win.clipboard_append(key)
            messagebox.showinfo("Đã copy!", "Key đã được copy vào clipboard!", parent=self.win)

    def _load_cloud_config(self):
        """Đọc cấu hình từ Cloud URL trong nền."""
        def fetch():
            try:
                url = self.CLOUD_CFG_URL
                headers = {"User-Agent": "ULSA-Admin/1.0"}
                resp = requests.get(url, headers=headers, timeout=6, verify=False)
                data = resp.json()
                # Cập nhật UI trên main thread
                self.win.after(0, lambda d=data: self._apply_cloud_config(d))
            except Exception as ex:
                self.win.after(0, lambda: self.cloud_status.config(
                    text=f"⚠️ Không đọc được Cloud: {ex}", fg="#f85149"))

        threading.Thread(target=fetch, daemon=True).start()

    def _apply_cloud_config(self, data: dict):
        for attr, key in [("cfg_gia", "gia_tien"), ("cfg_ngay", "so_ngay"),
                          ("cfg_ver", "version"), ("cfg_url", "url")]:
            if hasattr(self, attr) and key in data:
                w = getattr(self, attr)
                w.delete(0, tk.END)
                w.insert(0, str(data[key]))
        if hasattr(self, "cfg_notice") and "thong_bao" in data:
            self.cfg_notice.delete("1.0", tk.END)
            self.cfg_notice.insert("1.0", data.get("thong_bao", ""))
        self.cloud_status.config(text="✅ Đã đồng bộ từ Cloud thành công!", fg="#3fb950")

    def _save_local_config(self):
        """Lưu cấu hình vào file local để App cập nhật khi bật."""
        try:
            cfg = {
                "gia_tien": int(self.cfg_gia.get().strip() or GIA_TIEN),
                "so_ngay": int(self.cfg_ngay.get().strip() or 1),
                "version": self.cfg_ver.get().strip() or "1.2",
                "url": self.cfg_url.get().strip(),
                "thong_bao": self.cfg_notice.get("1.0", tk.END).strip(),
                "updated_at": datetime.now().isoformat()
            }
            cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_config.json")
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            self.cloud_status.config(text=f"💾 Đã lưu vào: {cfg_path}", fg="#3fb950")
            messagebox.showinfo("Thành công", f"Cấu hình đã lưu!\nGiá: {cfg['gia_tien']:,}đ | {cfg['so_ngay']} ngày", parent=self.win)
        except Exception as ex:
            messagebox.showerror("Lỗi", str(ex), parent=self.win)

    def _save_key_history(self, masv, expire, key):
        """Ghi lịch sử Key đã cấp vào file JSON."""
        hist_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_key_history.json")
        history = []
        if os.path.exists(hist_file):
            try:
                with open(hist_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                pass
        history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "masv": masv, "expire": expire, "key": key
        })
        try:
            with open(hist_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load_key_history(self):
        """Load lịch sử Key lên Treeview."""
        hist_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_key_history.json")
        for row in self.hist_tree.get_children():
            self.hist_tree.delete(row)
        if not os.path.exists(hist_file):
            return
        try:
            with open(hist_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            for item in reversed(history):
                self.hist_tree.insert("", "end", values=(
                    item.get("time", ""), item.get("masv", ""),
                    item.get("expire", ""), item.get("key", "")))
        except Exception:
            pass

    def _on_close(self):
        self.win.destroy()
        if self.on_close:
            self.on_close()




class CompleteGUI:
    def __init__(self, root, licensed_masv: str = "", expire_date: str = "", days_left: int = 0):
        self.root = root
        self.licensed_masv = licensed_masv.strip().upper()
        self.expire_date = expire_date
        self.days_left = days_left

        # Đường dẫn dựa trên vị trí file GUI
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(script_dir, "automation", "auto_config.json")
        print(f"📁 Config file: {self.config_file}")

        self.folder_name = os.path.basename(script_dir)
        self.root.title(f"🎯 ULSA Automation – {self.folder_name}")
        self.root.geometry("1280x800")
        self.root.minsize(1000, 700)

        self.process = None
        self.apply_styles()
        self.setup_ui()
        self.load_existing_config()
        self.update_title()
        
        # Bắt đầu đếm ngược thời gian bản quyền
        if self.licensed_masv:
            self.update_countdown()

        # ── Khóa ô Mã Sinh Viên sau khi UI đã load ──
        if self.licensed_masv:
            self.student_id_entry.delete(0, tk.END)
            self.student_id_entry.insert(0, self.licensed_masv)
            self.student_id_entry.config(state="disabled")

    def apply_styles(self):
        """Áp dụng theme và font chữ thống nhất cho toàn ứng dụng"""
        style = ttk.Style()
        style.theme_use('vista')  # Vista theme đẹp nhất trên Windows
        
        FONT_MAIN   = ('Segoe UI', 10)
        FONT_BOLD   = ('Segoe UI', 10, 'bold')
        FONT_TITLE  = ('Segoe UI', 13, 'bold')
        FONT_SMALL  = ('Segoe UI', 9)
        ACCENT      = '#0078D4'   # Màu xanh Microsoft
        ACCENT_DARK = '#005A9E'
        BG_LIGHT    = '#F3F3F3'
        
        # Notebook tabs
        style.configure('TNotebook',        background=BG_LIGHT)
        style.configure('TNotebook.Tab',    font=FONT_BOLD, padding=[14, 6])
        
        # Labels
        style.configure('TLabel',           font=FONT_MAIN)
        style.configure('Title.TLabel',     font=FONT_TITLE, foreground=ACCENT)
        style.configure('Section.TLabel',   font=FONT_BOLD, foreground='#333')
        style.configure('Hint.TLabel',      font=FONT_SMALL, foreground='#666')
        
        # LabelFrames
        style.configure('TLabelframe',      font=FONT_BOLD)
        style.configure('TLabelframe.Label',font=FONT_BOLD, foreground=ACCENT)
        
        # Buttons – Kiểu mặc định
        style.configure('TButton', font=FONT_MAIN, padding=[8, 5])
        
        # Button màu xanh nổi bật (dùng cho nút chức năng chính)
        style.configure('Accent.TButton',   font=FONT_BOLD, padding=[10, 6],
                        foreground='black', background=ACCENT)
        style.map('Accent.TButton',
                  background=[('active', ACCENT_DARK), ('pressed', ACCENT_DARK)],
                  relief=[('pressed', 'sunken')])
        
        # Treeview
        style.configure('Treeview',         font=FONT_MAIN, rowheight=26)
        style.configure('Treeview.Heading', font=FONT_BOLD, foreground='#333')
        style.map('Treeview',               background=[('selected', ACCENT)],
                                            foreground=[('selected', 'white')])
        
        # Entry
        style.configure('TEntry',           font=FONT_MAIN, padding=[4, 4])
        
        # ProgressBar
        style.configure('TProgressbar',     troughcolor='#E0E0E0', background=ACCENT)
    
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        self.config_frame = ttk.Frame(self.notebook, padding=0)
        self.notebook.add(self.config_frame, text="  ⚙️ Cấu hình & Lớp học  ")
        
        self.monitor_frame = ttk.Frame(self.notebook, padding=0)
        self.notebook.add(self.monitor_frame, text="  📊 Theo dõi Automation  ")
        
        self.setup_config_tab()
        self.setup_monitor_tab()

        # ── Thanh trạng thái bản quyền (Status Bar) ──
        self.status_bar = ttk.Frame(self.root, padding=(10, 5))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        sep = ttk.Separator(self.root, orient='horizontal')
        sep.pack(side=tk.BOTTOM, fill=tk.X)
        
        lic_text = f"🛡️ Bản quyền: {self.licensed_masv} | ⌛ Đang tính toán thời gian..."
        
        self.lic_info_label = ttk.Label(self.status_bar, text=lic_text, font=('Segoe UI', 9), foreground='#555')
        self.lic_info_label.pack(side=tk.LEFT)
        
        # Nút Đăng xuất
        self.logout_btn = ttk.Button(self.status_bar, text="🚪 Đăng xuất", command=self.logout_license)
        self.logout_btn.pack(side=tk.LEFT, padx=(15, 0))
        
        ttk.Label(self.status_bar, text=f"VXT ULSA Automation v{APP_VERSION}", font=('Segoe UI', 8, 'italic'), foreground='#999').pack(side=tk.RIGHT)

    def logout_license(self):
        """Tắt bản quyền và đưa về màn hình kích hoạt (không restart process)."""
        ans = messagebox.askyesno("Đăng xuất", 
                                  "Bạn có chắc chắn muốn đăng xuất?\nThao tác này sẽ hiển thị lại màn hình kích hoạt.", 
                                  parent=self.root)
        if not ans:
            return

        # Xóa file license
        if os.path.exists(license_manager.LICENSE_FILE):
            try:
                os.remove(license_manager.LICENSE_FILE)
            except Exception:
                pass

        # Ẩn toàn bộ UI hiện tại – không destroy root
        self.root.withdraw()

        # Callback sau khi kích hoạt thành công
        def on_reactivated(masv: str):
            res = license_manager.check_license()
            exp   = res.get("expire_date", "N/A")
            days  = res.get("days_left", 0)

            # Đóng hết widget cũ và tạo lại GUI mới trên cùng root
            self.root.deiconify()
            for widget in self.root.winfo_children():
                widget.destroy()
            new_app = CompleteGUI(self.root, licensed_masv=masv, expire_date=exp, days_left=days)
            new_app.log_message(f"✅ Đăng nhập lại thành công | Mã SV: {masv} | Hết hạn: {exp}")

        LicenseWindow(self.root, on_reactivated)

    def update_countdown(self):
        """Cập nhật đếm ngược thời gian bản quyền theo giây/phút/giờ/ngày"""
        if not self.expire_date:
            return
            
        try:
            # Parse ngày hết hạn
            if len(self.expire_date) > 10:
                expire_dt = datetime.strptime(self.expire_date, "%Y-%m-%d %H:%M:%S")
            else:
                expire_dt = datetime.strptime(self.expire_date, "%Y-%m-%d")
            
            # Thời gian hiện tại
            now = datetime.now()
            diff = expire_dt - now
            
            if diff.total_seconds() <= 0:
                self.lic_info_label.config(text=f"🛡️ Bản quyền: {self.licensed_masv} | 🛑 ĐÃ HẾT HẠN", foreground='red')
                return

            days = diff.days
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            time_str = f"{days}n {hours}h {minutes}p {seconds}s"
            self.lic_info_label.config(text=f"🛡️ Bản quyền: {self.licensed_masv} | ⏳ Còn: {time_str}")
            
            # Chạy lại sau 1 giây
            self.root.after(1000, self.update_countdown)
        except Exception:
            pass
    
    def setup_config_tab(self):
        """Tab cấu hình – Bố cục 2 cột: Trái (Nhập liệu) | Phải (Danh sách lớp)"""
        
        # ── Container chính (fill toàn tab, không cần scroll)
        main = ttk.Frame(self.config_frame, padding=(10, 8))
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=4, minsize=420)   # cột trái
        main.columnconfigure(1, weight=6, minsize=520)   # cột phải
        main.rowconfigure(0, weight=1)
        
        # ─────────────────────── CỘT TRÁI ───────────────────────
        left = ttk.Frame(main, padding=(0, 0, 8, 0))
        left.grid(row=0, column=0, sticky='nsew')
        left.rowconfigure(2, weight=1)   # Bulk input giãn dọc
        left.columnconfigure(0, weight=1) # Giãn ngang
        
        # ①  Đăng nhập
        login_frame = ttk.LabelFrame(left, text='  👤 Thông tin đăng nhập  ', padding=(12, 8))
        login_frame.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        login_frame.columnconfigure(1, weight=1)
        
        ttk.Label(login_frame, text='🎓 Mã sinh viên:').grid(row=0, column=0, sticky='w', pady=4)
        self.student_id_entry = ttk.Entry(login_frame)
        self.student_id_entry.grid(row=0, column=1, sticky='ew', padx=(8, 0), pady=4)
        
        ttk.Label(login_frame, text='🔐 Mật khẩu:').grid(row=1, column=0, sticky='w', pady=4)
        self.password_entry = ttk.Entry(login_frame, show='*')
        self.password_entry.grid(row=1, column=1, sticky='ew', padx=(8, 0), pady=4)
        
        ttk.Label(login_frame, text='📂 File lịch học:').grid(row=2, column=0, sticky='w', pady=4)
        path_row = ttk.Frame(login_frame)
        path_row.grid(row=2, column=1, sticky='ew', padx=(8, 0), pady=4)
        path_row.columnconfigure(0, weight=1)
        
        self.excel_path_entry = ttk.Entry(path_row)
        self.excel_path_entry.grid(row=0, column=0, sticky='ew')
        self.excel_path_entry.insert(0, 'lophoc.xlsx')
        
        ttk.Button(path_row, text='📁 Chọn...', command=self.browse_excel).grid(
            row=0, column=1, padx=(6, 0))
        
        # ②  Nút lưu / tải cấu hình
        cfg_row = ttk.Frame(left)
        cfg_row.grid(row=1, column=0, sticky='ew', pady=(0, 8))
        
        ttk.Button(cfg_row, text='💾 Lưu cấu hình', command=self.save_config).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        ttk.Button(cfg_row, text='📂 Tải cấu hình', command=self.load_config).pack(
            side=tk.LEFT, expand=True, fill=tk.X)
        
        # ③  Nhập nhanh (Paste)
        bulk_frame = ttk.LabelFrame(left, text='  📋 Nhập nhanh – Dán mã lớp  ', padding=(10, 6))
        bulk_frame.grid(row=2, column=0, sticky='nsew')
        bulk_frame.rowconfigure(1, weight=1)
        bulk_frame.columnconfigure(0, weight=1)
        
        ttk.Label(bulk_frame,
                  text='💡 Dán nhiều dòng mã lớp – hệ thống tự tìm trong Excel',
                  style='Hint.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 4))
        
        self.bulk_input = scrolledtext.ScrolledText(
            bulk_frame, width=50, height=7, font=('Consolas', 10),
            wrap=tk.WORD, relief='solid', bd=1)
        self.bulk_input.grid(row=1, column=0, sticky='nsew')
        
        placeholder = 'THML0723H_D21QL.03_LT\nCNSO1322H_D21QL.09_LT\n...'
        self.bulk_input.insert('1.0', placeholder)
        self.bulk_input.config(foreground='gray')
        
        def on_focus_in(e):
            if self.bulk_input.get('1.0', 'end-1c') == placeholder:
                self.bulk_input.delete('1.0', tk.END)
                self.bulk_input.config(foreground='black')
        
        def on_focus_out(e):
            if not self.bulk_input.get('1.0', 'end-1c').strip():
                self.bulk_input.insert('1.0', placeholder)
                self.bulk_input.config(foreground='gray')
        
        self.bulk_input.bind('<FocusIn>', on_focus_in)
        self.bulk_input.bind('<FocusOut>', on_focus_out)
        
        parse_row = ttk.Frame(bulk_frame)
        parse_row.grid(row=2, column=0, sticky='ew', pady=(6, 0))
        
        ttk.Button(parse_row, text='🔍 Phân tích & Thêm vào danh sách',
                   style='Accent.TButton',
                   command=self.parse_and_add_courses).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(parse_row, text='🗑️ Xóa',
                   command=self.clear_bulk_input).pack(side=tk.LEFT)
        
        # ─────────────────────── CỘT PHẢI ───────────────────────
        right = ttk.Frame(main, padding=(8, 0, 0, 0))
        right.grid(row=0, column=1, sticky='nsew')
        right.rowconfigure(1, weight=1)   # Treeview giãn theo chiều dọc
        right.columnconfigure(0, weight=1)
        
        # Header danh sách
        hdr = ttk.Frame(right)
        hdr.grid(row=0, column=0, sticky='ew', pady=(0, 4))
        ttk.Label(hdr, text='📚 Danh sách lớp đã chọn', style='Title.TLabel').pack(side=tk.LEFT)
        ttk.Button(hdr, text='🗑️ Xóa lớp chọn', command=self.delete_course).pack(side=tk.RIGHT)
        
        # Treeview
        tree_frame = ttk.Frame(right)
        tree_frame.grid(row=1, column=0, sticky='nsew')
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        columns = ('STT', 'Môn học', 'Lớp')
        self.course_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='extended')
        
        self.course_tree.heading('STT',      text='#')
        self.course_tree.heading('Môn học',  text='Mã môn học')
        self.course_tree.heading('Lớp',      text='Tên lớp tín chỉ')
        
        self.course_tree.column('STT',     width=36, stretch=False, anchor='center')
        self.course_tree.column('Môn học', width=160, stretch=False)
        self.course_tree.column('Lớp',     width=320, stretch=True)
        
        vsb = ttk.Scrollbar(tree_frame, orient='vertical',   command=self.course_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.course_tree.xview)
        self.course_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.course_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Thanh nút chức năng dưới Treeview
        action_bar = ttk.Frame(right)
        action_bar.grid(row=2, column=0, sticky='ew', pady=(8, 0))
        
        btns = [
            ('🔍 Kiểm tra mã & lớp',     self.check_course_and_class),
            ('📅 Kiểm tra trùng lịch',    self.check_schedule_only),
            ('💡 Gợi ý lớp thay thế',     self.suggest_alternative_classes),
            ('🗓️ Xem thời khóa biểu',     self.show_timetable),
        ]
        for label, cmd in btns:
            tk.Button(action_bar, text=label, command=cmd,
                      bg='#0078D4', fg='white', activebackground='#005A9E',
                      activeforeground='white', font=('Segoe UI', 9, 'bold'),
                      relief='flat', cursor='hand2', padx=6, pady=5).pack(
                side=tk.LEFT, expand=True, fill=tk.X, padx=3)

    def browse_excel(self):
        """Mở hộp thoại để chọn file Excel lịch học"""
        filename = filedialog.askopenfilename(
            title="Chọn file Excel lịch học",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        if filename:
            self.excel_path_entry.delete(0, tk.END)
            self.excel_path_entry.insert(0, filename)
            self.log_message(f"📅 Đã chọn file lịch học: {filename}")
    
    def setup_monitor_tab(self):
        """Tab theo dõi tiến trình với pause/resume"""
        
        main = ttk.Frame(self.monitor_frame, padding=(12, 8))
        main.pack(fill=tk.BOTH, expand=True)
        
        # ── Trạng thái tổng quan
        status_frame = ttk.LabelFrame(main, text='  📈 Trạng thái hệ thống  ', padding=(12, 8))
        status_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Dòng 1: Status + Step + Time
        row1 = ttk.Frame(status_frame)
        row1.pack(fill=tk.X, pady=(0, 6))
        
        self.status_label = ttk.Label(row1, text='● SẴN SÀNG',
                                      font=('Segoe UI', 11, 'bold'), foreground='#107C10')
        self.status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.step_label = ttk.Label(row1, text='🔄 Chưa bắt đầu')
        self.step_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.time_label = ttk.Label(row1, text='⏰ --:--:--',
                                    font=('Segoe UI', 10, 'bold'), foreground='#555')
        self.time_label.pack(side=tk.RIGHT)
        
        # Dòng 2: Thanh tiến độ
        row2 = ttk.Frame(status_frame)
        row2.pack(fill=tk.X)
        
        self.progress = ttk.Progressbar(row2, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.progress_label = ttk.Label(row2, text='0%', width=5)
        self.progress_label.pack(side=tk.RIGHT)
        
        # ── Điều khiển
        ctrl = ttk.LabelFrame(main, text='  🎮 Điều khiển Automation  ', padding=(12, 6))
        ctrl.pack(fill=tk.X, pady=(0, 8))
        
        self.start_btn = tk.Button(ctrl, text='🚀 Bắt đầu', bg='#0078D4', fg='white',
                                    activebackground='#005A9E', activeforeground='white',
                                    font=('Segoe UI', 9, 'bold'), relief='flat', cursor='hand2',
                                    command=self.start_automation, width=18, padx=6, pady=4)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 6))
        
        self.stop_btn = tk.Button(ctrl, text='🛑 Dừng', bg='#d9534f', fg='white',
                                  activebackground='#c9302c', activeforeground='white',
                                  font=('Segoe UI', 9, 'bold'), relief='flat', cursor='hand2',
                                  command=self.stop_automation, width=12, padx=6, pady=4)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 20))
        
        self.pause_btn = tk.Button(ctrl, text='⏸ Tạm dừng', bg='#f0ad4e', fg='white',
                                   activebackground='#ec971f', activeforeground='white',
                                   font=('Segoe UI', 9, 'bold'), relief='flat', cursor='hand2',
                                   command=self.pause_automation, width=14, padx=6, pady=4)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 6))
        
        self.resume_btn = tk.Button(ctrl, text='▶ Tiếp tục', bg='#5cb85c', fg='white',
                                    activebackground='#449d44', activeforeground='white',
                                    font=('Segoe UI', 9, 'bold'), relief='flat', cursor='hand2',
                                    command=self.resume_automation, width=14, padx=6, pady=4)
        self.resume_btn.pack(side=tk.LEFT)
        
        # ── Khu vực log
        log_frame = ttk.LabelFrame(main, text='  📋 Nhật ký hoạt động  ', padding=(6, 4))
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, font=('Consolas', 10), wrap=tk.WORD,
            relief='flat', bd=1, bg='#FAFAFA', fg='#111111')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Trạng thái ban đầu
        self.pause_btn.config(state='disabled')
        self.resume_btn.config(state='disabled')
        self.stop_btn.config(state='disabled')
        
        self.log_message('🎯 Hệ thống đã sẵn sàng!')
        self.log_message('💡 Chuyển sang tab "Cấu hình & Lớp học" để thiết lập trước')
        
        self.update_time()


    
    def add_course(self):
        """Thêm lớp tín chỉ vào danh sách"""
        subject = self.subject_entry.get().strip()
        class_name = self.class_entry.get().strip()
        
        if not subject or not class_name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ tên môn học và tên lớp!")
            return
        
        # Kiểm tra trùng lặp trước khi thêm
        if not self.check_and_handle_duplicates(subject, class_name):
            return
        
        # Thêm vào treeview
        item_count = len(self.course_tree.get_children())
        self.course_tree.insert('', 'end', values=(item_count + 1, subject, class_name))
        
        # Clear inputs
        self.subject_entry.delete(0, tk.END)
        self.class_entry.delete(0, tk.END)
        
        messagebox.showinfo("Thành công", f"Đã thêm: {subject} - {class_name}")
        
        # Kiểm tra trùng lặp sau khi thêm xong tất cả
        self.check_duplicates_after_adding()
    
    def delete_course(self):
        """Xóa lớp đã chọn"""
        selected = self.course_tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn lớp cần xóa!")
            return
        
        for item in selected:
            self.course_tree.delete(item)
        
        # Cập nhật lại STT
        for i, child in enumerate(self.course_tree.get_children()):
            self.course_tree.item(child, values=(i + 1, 
                                                self.course_tree.item(child)['values'][1],
                                                self.course_tree.item(child)['values'][2]))
        
        messagebox.showinfo("Thành công", "Đã xóa lớp đã chọn!")
    
    def parse_and_add_courses(self):
        """Phân tích dữ liệu paste nhiều dòng, tự động tìm kiếm trong Excel và thêm vào danh sách"""
        raw_text = self.bulk_input.get('1.0', 'end-1c').strip()
        
        if not raw_text or raw_text == 'THML0723H_D21QL.03_LT\nCNSO1322H_D21QL.09_LT\n...':
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng paste dữ liệu vào ô nhập!")
            return
        
        # Kiểm tra file Excel
        excel_file = self.excel_path_entry.get().strip()
        if not excel_file:
            excel_file = "lophoc.xlsx"
            
        if not os.path.exists(excel_file):
            messagebox.showerror("Lỗi", f"Không tìm thấy file {excel_file}!\nVui lòng chọn file lịch học chính xác ở phần Thông tin đăng nhập.")
            return
        
        try:
            # Đọc Excel
            self.log_message("📂 Đang đọc file Excel để tìm kiếm...")
            df = pd.read_excel(excel_file)
            
            lines = raw_text.split('\n')
            
            added_count = 0
            skipped_count = 0
            not_found = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Bỏ qua nếu dòng toàn số (mã sinh viên)
                if line.isdigit():
                    skipped_count += 1
                    continue
                
                # Bỏ qua dòng quá ngắn (< 5 ký tự)
                if len(line) < 5:
                    skipped_count += 1
                    continue
                
                # Tách riêng 1 cụm có vẻ giống tên lớp nhất từ đoạn dài thòng lọng nếu có
                class_name_match = re.search(r'\b([A-ZĐĂÂÊÔƠƯA-Za-z0-9РТ]{3,12}[_\-\s]?[A-ZĐĂÂÊÔƠƯA-Za-z0-9\.РТ]{3,20}[_\-\s]?(?:LT|TH|BT|L|T|B)?)\b', line, re.IGNORECASE)
                search_target = class_name_match.group(1).strip() if class_name_match else line

                self.log_message(f"🔍 Phân tích dòng: '{line}'")
                
                # Tiền xử lý - làm sạch chuỗi: CHỈ lấy chữ và số, bỏ qua mọi dấu chấm, gạch ngang, gạch dưới, khoảng trắng...
                input_clean = re.sub(r'[^A-Za-z0-9]', '', search_target).upper()
                
                # Bỏ qua nếu sau khi dọn sạch không còn gì
                if not input_clean:
                    skipped_count += 1
                    continue

                best_score = 0
                best_cls = None
                best_subject_code = None
                
                # Quét qua TOÀN BỘ các lớp tín chỉ trong file Excel để tìm chuỗi gần giống nhất
                all_classes = df['Tên lớp tín chỉ'].dropna().unique().tolist()
                
                # ── Thuật toán tìm kiếm uu tiên mã môn trước ──
                # Bước 1: Tìm chính xác 100% (case-insensitive, bỏ kyï tự đặc biệt)
                for cls in all_classes:
                    if not isinstance(cls, str): continue
                    cls_clean = re.sub(r'[^A-Za-z0-9]', '', cls).upper()
                    if input_clean == cls_clean:
                        best_score = 100
                        best_cls = cls
                        break

                if not best_cls:
                    # Bước 2: Tìm theo mã môn - prefix trước dấu _
                    # Tính prefix của input (phần trước _ đầu tiên, hoặc toàn bộ nếu không có _)
                    input_prefix = search_target.split('_')[0].upper() if '_' in search_target else input_clean[:7]
                    input_prefix_clean = re.sub(r'[^A-Za-z0-9]', '', input_prefix)

                    for cls in all_classes:
                        if not isinstance(cls, str): continue
                        cls_clean = re.sub(r'[^A-Za-z0-9]', '', cls).upper()
                        cls_prefix = re.sub(r'[^A-Za-z0-9]', '', cls.split('_')[0]).upper() if '_' in cls else cls_clean[:7]

                        # Điểm cơ bản
                        base_score = max(
                            fuzz.ratio(input_clean, cls_clean),
                            fuzz.token_sort_ratio(input_clean, cls_clean)
                        )

                        # Bonus lớn nếu prefix (mã môn) giống nhau - tránh XULA ra KPDL
                        prefix_bonus = 0
                        if input_prefix_clean and cls_prefix:
                            if input_prefix_clean == cls_prefix:
                                prefix_bonus = 40  # Bonus lớn để ưu tiên tuyệt đối
                            elif cls_prefix.startswith(input_prefix_clean) or input_prefix_clean.startswith(cls_prefix):
                                prefix_bonus = 20

                        final_score = min(base_score + prefix_bonus, 100)

                        if final_score > best_score:
                            best_score = final_score
                            best_cls = cls
                
                # Log top 3 ứng viên
                if best_cls:
                    self.log_message(f"  📊 Kết quả tốt nhất: {best_cls} ({best_score}%)")
                if best_cls and best_score >= 60:
                    row = df[df['Tên lớp tín chỉ'] == best_cls].iloc[0]
                    subject_code = row['Mã học phần']
                    subject_name = row['Tên học phần']
                    
                    item_count = len(self.course_tree.get_children())
                    self.course_tree.insert('', 'end', values=(item_count + 1, subject_code, best_cls))
                    added_count += 1
                    
                    # Thông báo trực quan ra Log để người dùng tự tin
                    self.log_message(f"  ✅ Tìm thấy khớp lệnh cao ({best_score}%): {best_cls} | Môn: {subject_name}")
                    if input_clean != re.sub(r'[^A-Za-z0-9]', '', best_cls).upper():
                        self.log_message(f"      ⚠️ Input ảo: '{line}' → Đã tự động cập nhật chuẩn thành: '{best_cls}'")
                else:
                    self.log_message(f"  ❌ Không tìm thấy lớp nào trên toàn hệ thống giống với '{line}' (Khớp tối đa: {best_score}%)")
                    not_found.append(line)
                    skipped_count += 1
                    messagebox.showwarning("Cảnh báo", f"❌ Không thể phân tích mã lớp này:\n'{line}'\n\nHệ thống đã cố đoán nhưng dữ liệu quá lạ hoặc môn này không tồn tại trong file lịch học.")
            
            # Kiểm tra và xử lý trùng lặp sau khi thêm tất cả
            self.log_message("🔍 Kiểm tra trùng lặp...")
            self.check_duplicates_after_adding()
            
            # Hiển thị kết quả
            result_msg = f"✅ Đã thêm {added_count} lớp\n"
            result_msg += f"⏭️ Đã bỏ qua {skipped_count} dòng\n"
            
            if not_found:
                result_msg += f"\n❌ Không tìm thấy:\n"
                result_msg += "\n".join([f"  - {item}" for item in not_found[:5]])
                if len(not_found) > 5:
                    result_msg += f"\n  ... và {len(not_found) - 5} lớp khác"
            
            if added_count > 0:
                messagebox.showinfo("Hoàn thành", result_msg)
                self.clear_bulk_input()
            else:
                messagebox.showwarning("Kết quả", result_msg)
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi đọc Excel: {e}")
            self.log_message(f"❌ Lỗi: {e}")
            import traceback
            self.log_message(traceback.format_exc())
    
    def clear_bulk_input(self):
        """Xóa nội dung ô nhập bulk"""
        self.bulk_input.delete('1.0', tk.END)
        placeholder = 'THML0723H_D21QL.03_LT\nCNSO1322H_D21QL.09_LT\n...'
        self.bulk_input.insert('1.0', placeholder)
        self.bulk_input.config(foreground='gray')
    
    def check_and_handle_duplicates(self, subject, class_name):
        """Kiểm tra trùng lặp trước khi thêm (cho add_course thủ công)"""
        for child in self.course_tree.get_children():
            values = self.course_tree.item(child)['values']
            if len(values) >= 3:
                existing_subject = values[1].strip()
                existing_class = values[2].strip()
                
                # Trùng hoàn toàn
                if existing_subject == subject and existing_class == class_name:
                    messagebox.showwarning("Trùng lặp", f"Lớp này đã tồn tại:\n{subject} - {class_name}")
                    return False
        return True
    
    def check_duplicates_after_adding(self):
        """Kiểm tra và xử lý trùng lặp sau khi thêm hàng loạt"""
        courses = []
        
        # Thu thập tất cả lớp
        for child in self.course_tree.get_children():
            values = self.course_tree.item(child)['values']
            if len(values) >= 3:
                courses.append({
                    'id': child,
                    'subject': values[1].strip(),
                    'class': values[2].strip()
                })
        
        # Tìm trùng lặp
        exact_duplicates = []  # Trùng hoàn toàn (môn + lớp)
        subject_duplicates = {}  # Cùng môn, khác lớp
        
        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                c1 = courses[i]
                c2 = courses[j]
                
                # Trùng hoàn toàn
                if c1['subject'] == c2['subject'] and c1['class'] == c2['class']:
                    if (c1['id'], c2['id']) not in exact_duplicates:
                        exact_duplicates.append((c1['id'], c2['id']))
                
                # Cùng môn, khác lớp
                elif c1['subject'] == c2['subject']:
                    key = c1['subject']
                    if key not in subject_duplicates:
                        subject_duplicates[key] = []
                    # Tránh trùng lặp trong danh sách
                    if c1 not in subject_duplicates[key]:
                        subject_duplicates[key].append(c1)
                    if c2 not in subject_duplicates[key]:
                        subject_duplicates[key].append(c2)
        
        # Xử lý trùng hoàn toàn - Tự động xóa
        removed_exact = []
        if exact_duplicates:
            for dup_id1, dup_id2 in exact_duplicates:
                try:
                    # Lấy thông tin trước khi xóa
                    values = self.course_tree.item(dup_id2)['values']
                    removed_exact.append(f"{values[1]} - {values[2]}")
                    # Xóa item thứ 2, giữ item đầu tiên
                    self.course_tree.delete(dup_id2)
                except:
                    pass
            
            # Cập nhật lại STT
            self.update_course_numbers()
            
            if removed_exact:
                msg = f"🗑️ ĐÃ TỰ ĐỘNG XÓA {len(removed_exact)} LỚP TRÙNG LẶP:\n\n"
                msg += "\n".join([f"  • {item}" for item in removed_exact])
                self.log_message(f"🗑️ Đã tự động xóa {len(removed_exact)} lớp trùng lặp hoàn toàn")
                messagebox.showinfo("Đã xóa trùng lặp", msg)
        
        # Xử lý cùng môn, khác lớp - Tự động xóa lớp sau, giữ lớp đầu
        removed_subject = []
        if subject_duplicates:
            for subject, courses_list in subject_duplicates.items():
                # Giữ lớp đầu tiên, xóa các lớp sau
                for i in range(1, len(courses_list)):
                    try:
                        course = courses_list[i]
                        removed_subject.append(f"{course['subject']} - {course['class']}")
                        self.course_tree.delete(course['id'])
                    except:
                        pass
            
            # Cập nhật lại STT
            self.update_course_numbers()
            
            if removed_subject:
                msg = f"🗑️ ĐÃ TỰ ĐỘNG XÓA {len(removed_subject)} LỚP TRÙNG MÔN:\n\n"
                msg += "\n".join([f"  • {item}" for item in removed_subject])
                msg += f"\n\n💡 Đã giữ lại lớp đầu tiên của mỗi môn"
                self.log_message(f"🗑️ Đã tự động xóa {len(removed_subject)} lớp trùng môn")
                messagebox.showinfo("Đã xóa trùng môn", msg)
    
    def update_course_numbers(self):
        """Cập nhật lại số thứ tự trong Treeview"""
        for i, child in enumerate(self.course_tree.get_children(), start=1):
            values = list(self.course_tree.item(child)['values'])
            values[0] = i
            self.course_tree.item(child, values=values)
    
    def show_duplicate_subject_dialog(self, subject_duplicates):
        """Hiển thị dialog cho user chọn lớp cần xóa khi cùng môn nhưng khác lớp"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚠️ Phát hiện trùng môn học")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_text = "⚠️ PHÁT HIỆN CÁC MÔN HỌC BỊ TRÙNG\n\n"
        title_text += "Các môn học sau có nhiều lớp khác nhau.\n"
        title_text += "Vui lòng chọn lớp cần XÓA (giữ lớp không tích chọn):"
        
        title_label = ttk.Label(main_frame, text=title_text, font=('Arial', 11, 'bold'), justify=tk.LEFT)
        title_label.pack(pady=(0, 10))
        
        # Scrollable frame
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Checkboxes cho từng môn
        to_delete = []
        
        for subject, courses_list in subject_duplicates.items():
            subject_frame = ttk.LabelFrame(scrollable_frame, text=f" 📚 Môn: {subject} ", padding="10")
            subject_frame.pack(fill=tk.X, pady=10, padx=5)
            
            ttk.Label(subject_frame, text=f"Có {len(courses_list)} lớp khác nhau. Chọn lớp cần XÓA:", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
            
            for course in courses_list:
                var = tk.BooleanVar(value=False)
                checkbox = ttk.Checkbutton(subject_frame, 
                                          text=f"❌ Xóa: {course['class']}", 
                                          variable=var)
                checkbox.pack(anchor=tk.W, pady=2)
                to_delete.append({'var': var, 'id': course['id'], 'class': course['class']})
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def on_ok():
            deleted_count = 0
            for item in to_delete:
                if item['var'].get():
                    try:
                        self.course_tree.delete(item['id'])
                        deleted_count += 1
                        self.log_message(f"🗑️ Đã xóa: {item['class']}")
                    except:
                        pass
            
            if deleted_count > 0:
                self.update_course_numbers()
                messagebox.showinfo("Hoàn thành", f"Đã xóa {deleted_count} lớp được chọn!")
            
            dialog.destroy()
        
        def on_skip():
            self.log_message("⏭️ Bỏ qua xử lý trùng môn")
            dialog.destroy()
        
        ok_btn = ttk.Button(btn_frame, text="✅ Xóa các lớp đã chọn", command=on_ok, width=20)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        skip_btn = ttk.Button(btn_frame, text="⏭️ Bỏ qua", command=on_skip, width=20)
        skip_btn.pack(side=tk.LEFT, padx=5)
    
    def show_class_selection_dialog(self, subject_code, subject_name, original_class, available_classes, df):
        """Hiển thị dialog cho user chọn lớp thay thế, tự động chọn sau 60s"""
        dialog = tk.Toplevel(self.root)
        dialog.title("💡 Chọn lớp thay thế")
        dialog.geometry("900x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Biến lưu kết quả
        result = {'selected_class': None, 'cancelled': False}
        countdown = {'value': 60}
        
        # Frame chính
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_text = f"⚠️ Không tìm thấy lớp: {original_class}\n\n"
        title_text += f"📚 Môn: {subject_name} (Mã: {subject_code})\n\n"
        title_text += f"💡 Các lớp còn lại của môn này:\n"
        title_text += f"   ✅ = Phù hợp với thời khóa biểu\n"
        title_text += f"   🔴 = Trùng lịch\n\n"
        title_text += f"🎯 Hành động:\n"
        title_text += f"   • Chọn lớp + bấm OK → Lưu lớp đó\n"
        title_text += f"   • Đợi 60s → Tự động chọn lớp phù hợp nhất\n"
        title_text += f"   • Bấm Hủy → Bỏ qua lớp này"
        
        title_label = ttk.Label(main_frame, text=title_text, font=('Arial', 10), justify=tk.LEFT)
        title_label.pack(pady=(0, 10))
        
        # Countdown label
        countdown_label = ttk.Label(main_frame, 
                                   text=f"⏱️ Tự động chọn lớp phù hợp sau: {countdown['value']}s", 
                                   font=('Arial', 12, 'bold'), foreground='red')
        countdown_label.pack(pady=5)
        
        # Frame với scrollbar (KHÔNG expand để còn chỗ cho nút)
        list_frame = ttk.LabelFrame(main_frame, text=" 📋 CÁC LỚP CÒN LẠI ", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=False, pady=10)
        
        canvas = tk.Canvas(list_frame, height=350)  # Giới hạn chiều cao
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Radio buttons
        var = tk.StringVar(value="")
        
        # Lấy lịch học hiện tại để check trùng
        current_schedules = []
        for child in self.course_tree.get_children():
            values = self.course_tree.item(child)['values']
            if len(values) >= 3:
                class_name = values[2].strip()
                matching_rows = df[df['Tên lớp tín chỉ'] == class_name]
                if not matching_rows.empty:
                    row = matching_rows.iloc[0]
                    ca_hoc = str(row['Ca học']) if 'Ca học' in df.columns else ""
                    lich_hoc = str(row['Lịch học']) if 'Lịch học' in df.columns else ""
                    schedule = f"{ca_hoc}\n{lich_hoc}".strip()
                    
                    if schedule and schedule != "\nnan":
                        current_schedules.append(schedule)
        
        # Hiển thị từng lớp và tìm lớp phù hợp nhất
        best_class = None  # Lớp phù hợp nhất (không trùng lịch, có slot trống)
        
        for idx, row in available_classes.iterrows():
            class_name = row['Tên lớp tín chỉ']  # TÊN LỚP ĐẦY ĐỦ (vd: CNSO1322H_D21QL.01_LT)
            ca_hoc = str(row['Ca học']) if 'Ca học' in df.columns else ""
            lich_hoc = str(row['Lịch học']) if 'Lịch học' in df.columns else ""
            schedule = f"{ca_hoc}\n{lich_hoc}".strip()
            if not schedule or schedule == "nan":
                schedule = "Chưa có lịch"
            
            slots = row['Còn trống'] if pd.notna(row['Còn trống']) else "?"
            
            # Check trùng lịch với thời khóa biểu hiện tại
            has_conflict = False
            if schedule != "Chưa có lịch":
                for existing_schedule in current_schedules:
                    if schedule == existing_schedule or self.check_time_overlap(schedule, existing_schedule):
                        has_conflict = True
                        break
            
            # Tạo frame cho từng option
            option_frame = ttk.Frame(scrollable_frame)
            option_frame.pack(fill=tk.X, pady=5, padx=5)
            
            conflict_icon = "🔴 TRÙNG LỊCH " if has_conflict else "✅ PHÙ HỢP "
            text = f"{conflict_icon}{class_name}\n    📅 Lịch: {schedule}\n    💺 Còn trống: {slots}"
            
            radio = ttk.Radiobutton(option_frame, text=text, variable=var, value=class_name)
            radio.pack(anchor=tk.W)
            
            # Tìm lớp phù hợp nhất: Không trùng lịch + Có slot trống
            if not has_conflict and best_class is None:
                best_class = class_name
                var.set(class_name)  # Tự động chọn sẵn lớp phù hợp nhất
        
        # Nếu không có lớp nào phù hợp, chọn lớp đầu tiên
        if var.get() == "" and not available_classes.empty:
            first_class = available_classes.iloc[0]['Tên lớp tín chỉ']
            var.set(first_class)
            self.log_message(f"  ⚠️ Tất cả lớp đều trùng lịch, tự động chọn: {first_class}")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def on_ok():
            selected = var.get()
            if selected:
                result['selected_class'] = selected
                dialog.destroy()
            else:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn một lớp!")
        
        def on_cancel():
            result['cancelled'] = True
            dialog.destroy()
        
        def update_countdown():
            if countdown['value'] > 0 and dialog.winfo_exists():
                countdown['value'] -= 1
                countdown_label.config(text=f"⏱️ Tự động chọn lớp phù hợp sau: {countdown['value']}s")
                dialog.after(1000, update_countdown)
            elif countdown['value'] == 0 and dialog.winfo_exists():
                # Hết thời gian → Tự động chọn lớp phù hợp nhất (đã được chọn sẵn)
                selected = var.get()
                if selected:
                    result['selected_class'] = selected
                    self.log_message(f"  ⏰ HẾT 60s → Tự động chọn lớp phù hợp với TKB: {selected}")
                    dialog.destroy()
                else:
                    result['cancelled'] = True
                    self.log_message(f"  ⚠️ Không có lớp nào được chọn")
                    dialog.destroy()
        
        ok_btn = ttk.Button(btn_frame, text="✅ OK", command=on_ok, width=15)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="❌ Hủy", command=on_cancel, width=15)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bắt đầu đếm ngược
        update_countdown()
        
        # Đợi dialog đóng
        dialog.wait_window()
        
        # Trả về kết quả
        if result['cancelled']:
            return None
        return result['selected_class']
    
    def save_config(self):
        """Lưu cấu hình vào file JSON đúng chuẩn auto_config.json (login_info, course_selections)"""
        student_id = self.student_id_entry.get().strip()
        password = self.password_entry.get().strip()
        if not student_id or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ mã sinh viên và mật khẩu!")
            return
        # Thu thập danh sách lớp
        subject_names = []
        class_names = []
        for child in self.course_tree.get_children():
            values = self.course_tree.item(child)['values']
            # Chỉ lưu nếu cả subject và class đều có dữ liệu
            if len(values) >= 3 and values[1] and values[2]:
                subject_names.append(values[1])
                class_names.append(values[2])
        if not subject_names or not class_names:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng thêm ít nhất 1 lớp tín chỉ!")
            return
        if len(subject_names) != len(class_names):
            messagebox.showerror("Lỗi dữ liệu", "Số lượng tên môn học và tên lớp không khớp!")
            return
        config_data = {
            "login_info": {
                "student_id": student_id,
                "password": password
            },
            "course_selections": {
                "subject_names_b1": subject_names,
                "class_names_b2": class_names
            },
            "created_time": datetime.now().isoformat(),
            "excel_file_path": self.excel_path_entry.get().strip()
        }
        # Giữ lại automation_settings nếu có
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                if 'automation_settings' in old_data:
                    config_data['automation_settings'] = old_data['automation_settings']
        except Exception:
            pass
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Thành công", f"Đã lưu cấu hình vào {self.config_file}!")
            self.log_message(f"💾 Đã lưu cấu hình: {len(subject_names)} lớp vào file: {os.path.abspath(self.config_file)}")
            # Cập nhật tiêu đề sau khi lưu
            self.update_title()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cấu hình: {e}\nFile: {os.path.abspath(self.config_file)}")
            self.log_message(f"❌ Lỗi lưu file: {os.path.abspath(self.config_file)}: {e}")
    
    def load_config(self):
        """Load cấu hình từ file"""
        self.load_existing_config()
    
    def load_existing_config(self):
        """Load cấu hình hiện có (login_info, course_selections) và tự động load vào Treeview"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                # Load login info
                login_info = config_data.get('login_info', {})
                self.student_id_entry.delete(0, tk.END)
                self.student_id_entry.insert(0, login_info.get('student_id', ''))
                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, login_info.get('password', ''))
                
                # Load Excel file path
                excel_path = config_data.get('excel_file_path', 'lophoc.xlsx')
                self.excel_path_entry.delete(0, tk.END)
                self.excel_path_entry.insert(0, excel_path)
                # Load courses từ course_selections vào Treeview
                self.course_tree.delete(*self.course_tree.get_children())
                course_selections = config_data.get('course_selections', {})
                subject_names = course_selections.get('subject_names_b1', [])
                class_names = course_selections.get('class_names_b2', [])
                for i, (subject, class_name) in enumerate(zip(subject_names, class_names)):
                    self.course_tree.insert('', 'end', values=(
                        i + 1,
                        subject,
                        class_name
                    ))
                self.log_message(f"📂 Đã load cấu hình: {len(subject_names)} lớp")
        except Exception as e:
            self.log_message(f"⚠️ Không thể load cấu hình: {e}")
    
    def update_title(self):
        """Cập nhật tiêu đề cửa sổ với tên thư mục và mã sinh viên"""
        try:
            student_id = self.student_id_entry.get().strip()
            if student_id:
                self.root.title(f"🎯 {self.folder_name} : {student_id}")
            else:
                self.root.title(f"🎯 {self.folder_name}")
        except Exception as e:
            print(f"⚠️ Lỗi cập nhật tiêu đề: {e}")
    
    def update_time(self):
        """Cập nhật thời gian real-time"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=f"⏰ Thời gian: {current_time}")
        self.root.after(1000, self.update_time)
    
    def log_message(self, message):
        """Thêm message vào log nếu widget đã khởi tạo"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            self.root.update()
        else:
            print(log_entry)
    
    def start_automation(self):
        """Bắt đầu automation và phân luồng kiểm tra môi trường chạy tránh freeze"""
        import threading
        
        # 1. Kiểm tra cấu hình trước khi chạy
        if not os.path.exists(self.config_file):
            from tkinter import messagebox
            messagebox.showwarning("Chưa có cấu hình", "Vui lòng lưu cấu hình trước khi chạy!", parent=self.root)
            return
            
        # Khóa nút bấm và báo hiệu
        self.start_btn.config(state='disabled')
        self.log_message("⏳ Phân tích môi trường...")
        self.root.update()

        def _run_env_checks_thread():
            try:
                # ── Kiểm tra bản quyền Online ──
                import license_manager
                res = license_manager.check_license()
                if not res.get("valid", False):
                    self.root.after(0, lambda: _handle_invalid_license(res))
                    return
                
                # ── Kiểm tra mức độ sẵn sàng của Google Chrome ──
                chrome_version = None
                chrome_needs_install = False
                chrome_error = None
                try:
                    import winreg as _winreg
                    def _get_chrome_ver():
                        for key_path in [r"SOFTWARE\Google\Chrome\BLBeacon", r"SOFTWARE\WOW6432Node\Google\Chrome\BLBeacon"]:
                            try:
                                key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, key_path)
                                ver, _ = _winreg.QueryValueEx(key, "version")
                                _winreg.CloseKey(key)
                                return ver
                            except Exception:
                                pass
                        for c_path in [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]:
                            if os.path.exists(c_path):
                                return "đã cài"
                        return None
                    chrome_version = _get_chrome_ver()
                    if not chrome_version:
                        chrome_needs_install = True
                except Exception as e:
                    chrome_error = str(e)

                # ── Ra quyết định tiếp diễn ──
                if chrome_error:
                    self.root.after(0, lambda: self.log_message(f"⚠️ Lỗi kiểm tra Chrome: {chrome_error}"))
                    self.root.after(0, _proceed)
                elif chrome_needs_install:
                    self.root.after(0, lambda: self.log_message("⚠️ Chưa phát hiện Google Chrome! Đang tự động tải & Cài đặt..."))
                    _download_and_install_chrome_blocking()
                else:
                    self.root.after(0, lambda: self.log_message(f"✅ Google Chrome đã sẵn sàng (version: {chrome_version})"))
                    self.root.after(0, _proceed)
                    
            except Exception as e:
                self.root.after(0, lambda e=e: self.log_message(f"❌ Lỗi phân tích môi trường: {str(e)}"))
                self.root.after(0, lambda: self.start_btn.config(state='normal'))

        def _download_and_install_chrome_blocking():
            import urllib.request, tempfile, subprocess
            try:
                self.root.after(0, lambda: self.log_message("📥 Bắt đầu tải Google Chrome từ máy chủ... (vui lòng chờ)"))
                url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
                tmp_dir = tempfile.gettempdir()
                save_path = os.path.join(tmp_dir, "chrome_installer.exe")
                
                def _progress(count, block_size, total_size):
                    if total_size > 0:
                        pct = min(int(count * block_size * 100 / total_size), 100)
                        if pct % 25 == 0:
                            self.root.after(0, lambda p=pct: self.log_message(f"  ↓ Đang tải Chrome: {p}%"))
                            
                urllib.request.urlretrieve(url, save_path, _progress)
                self.root.after(0, lambda: self.log_message("⚙️ Đã tải xong! Đang tự động cài ẩn Google Chrome (khoảng 30-60s)..."))
                subprocess.run([save_path, "/silent", "/install"], check=False)
                self.root.after(0, lambda: self.log_message("✅ Cài đặt Google Chrome hoàn tất!"))
                self.root.after(0, _proceed)
            except Exception as e:
                self.root.after(0, lambda e=e: self.log_message(f"❌ Lỗi khi tự cài Chrome: {e}"))
                self.root.after(0, lambda: self.log_message("⚠️ Tiến trình vẫn sẽ tiếp tục mở automation..."))
                self.root.after(0, _proceed)

        def _handle_invalid_license(res):
            from tkinter import messagebox
            messagebox.showerror(
                "❌ Bản quyền đã hết hạn",
                f"Bản quyền của bạn đã hết hạn!\nChi tiết: {res.get('reason', '')}\n\n"
                "Hệ thống sẽ Đăng xuất để bạn vào màn hình Kích hoạt gia hạn.", parent=self.root
            )
            import os
            try:
                import license_manager
                if os.path.exists(license_manager.LICENSE_FILE):
                    os.remove(license_manager.LICENSE_FILE)
            except:
                pass
            
            self.root.withdraw()
            from final.complete_gui import LicenseWindow, CompleteGUI
            import license_manager
            
            def on_reactivated(masv: str):
                res2 = license_manager.check_license()
                exp = res2.get("expire_date", "N/A")
                days = res2.get("days_left", 0)
                self.root.deiconify()
                # Remove all old widgets to prevent duplicates
                for widget in self.root.winfo_children():
                    widget.destroy()
                CompleteGUI(self.root, licensed_masv=masv, expire_date=exp, days_left=days)

            LicenseWindow(self.root, on_reactivated)
            self.start_btn.config(state='normal')
            
        def _proceed():
            import sys
            self.log_message("🚀 ĐANG KHỞI ĐỘNG AUTOMATION...")
            self.status_label.config(text="📢 Trạng thái: ▶️ ĐANG CHẠY", foreground="green")
            self.step_label.config(text="🔄 Bước hiện tại: Khởi động")
            self.progress['value'] = 10
            self.progress_label.config(text="10%")
            self.pause_btn.config(state='normal')
            self.resume_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            if getattr(sys, 'frozen', False):
                self.log_message("🎯 Chạy từ file .exe")
                self.run_automation_direct()
            else:
                self.log_message("🐍 Chạy từ Python source")
                self.run_automation_subprocess()

        # ── Kickoff the background thread ──
        threading.Thread(target=_run_env_checks_thread, daemon=True).start()

    def run_automation_direct(self):
        """Chạy automation trực tiếp (khi build .exe)"""
        try:
            # Redirect stdout để capture log
            import queue
            self.log_queue = queue.Queue()
            
            # Import automation module
            if getattr(sys, 'frozen', False):
                # Thêm automation path vào sys.path
                base_path = sys._MEIPASS
                automation_path = os.path.join(base_path, 'automation')
                if automation_path not in sys.path:
                    sys.path.insert(0, automation_path)
            
            from automation import auto_login_with_title_check
            
            self.log_message("✅ Đã load automation module")
            
            # Tạo class để redirect stdout
            class LogCapture:
                def __init__(self, log_queue):
                    self.log_queue = log_queue
                    self.original_stdout = sys.stdout
                    self.original_stderr = sys.stderr
                
                def write(self, text):
                    if text.strip():
                        self.log_queue.put(text.rstrip())
                    # Chỉ write ra console nếu original_stdout không phải None
                    # (khi chạy .exe với console=False thì stdout là None)
                    if self.original_stdout is not None:
                        try:
                            self.original_stdout.write(text)
                        except:
                            pass
                
                def flush(self):
                    if self.original_stdout is not None:
                        try:
                            self.original_stdout.flush()
                        except:
                            pass
            
            # Redirect stdout/stderr
            log_capture = LogCapture(self.log_queue)
            sys.stdout = log_capture
            sys.stderr = log_capture
            
            # Chạy automation trong thread
            def run_with_redirect():
                try:
                    auto_login_with_title_check.main(gui_mode=True)  # Pass gui_mode=True để không gọi input()
                except Exception as e:
                    self.log_queue.put(f"❌ Lỗi: {e}")
                finally:
                    # Restore stdout/stderr
                    sys.stdout = log_capture.original_stdout
                    sys.stderr = log_capture.original_stderr
            
            threading.Thread(target=run_with_redirect, daemon=True).start()
            
            # Tạo thread đọc log từ queue
            threading.Thread(target=self.read_queue_output, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"❌ Lỗi khi khởi động automation: {e}")
            import traceback
            self.log_message(traceback.format_exc())
    
    def run_automation_subprocess(self):
        """Chạy automation qua subprocess (khi dev từ source)"""
        # Đảm bảo PYTHONIOENCODING và PYTHONUNBUFFERED để log không lỗi Unicode và cập nhật realtime
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"

        # Đường dẫn tuyệt đối tới python.exe và script automation dựa trên vị trí file GUI
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "automation", "auto_login_with_title_check.py")
        
        # Tìm Python - thử nhiều vị trí
        python_exe = None
        python_candidates = [
            os.path.join(script_dir, ".venv", "Scripts", "python.exe"),  # Trong .venv local
            "python",  # Python trong PATH
            "py"       # Python launcher
        ]
        
        for candidate in python_candidates:
            if candidate in ["python", "py"]:
                # Thử chạy để kiểm tra
                try:
                    result = subprocess.run([candidate, "--version"], capture_output=True, timeout=2)
                    if result.returncode == 0:
                        python_exe = candidate
                        break
                except:
                    continue
            else:
                # Kiểm tra file tồn tại
                if os.path.exists(candidate):
                    python_exe = candidate
                    break
        
        if not python_exe:
            self.log_message("❌ KHÔNG TÌM THẤY PYTHON!")
            self.log_message("💡 Vui lòng chạy SETUP_FIRST_TIME.bat trước!")
            messagebox.showerror("Lỗi", "Không tìm thấy Python!\n\nVui lòng:\n1. Chạy SETUP_FIRST_TIME.bat\n2. Hoặc cài Python vào hệ thống")
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            return
        
        print(f"🐍 Python: {python_exe}")
        print(f"📜 Script: {script_path}")

        try:
            self.process = subprocess.Popen([
                python_exe, script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, text=True, bufsize=1, encoding='utf-8', cwd=script_dir)
            self.log_message(f"▶️ Đã khởi động: {python_exe} {script_path}")
            # Tạo thread đọc log stdout/stderr
            threading.Thread(target=self.read_process_output, daemon=True).start()
        except Exception as e:
            self.log_message(f"❌ Lỗi khi khởi động automation: {e}")
    
    def read_queue_output(self):
        """Đọc log từ queue (khi chạy direct từ .exe)"""
        while True:
            try:
                if hasattr(self, 'log_queue'):
                    line = self.log_queue.get(timeout=0.1)
                    if line:
                        self.log_message(line)
                else:
                    break
            except:
                time.sleep(0.1)
                continue

    def read_process_output(self):
        """Đọc log stdout/stderr từ process và hiển thị lên GUI"""
        if not self.process:
            return
        try:
            for line in self.process.stdout:
                if line:
                    self.log_message(line.rstrip())
        except Exception as e:
            self.log_message(f"[LOG ERROR] {e}")
    
    def pause_automation(self):
        """Tạm dừng automation"""
        self.log_message("⏸️ ĐANG TẠM DỪNG AUTOMATION...")
        self.status_label.config(text="📢 Trạng thái: ⏸️ TẠM DỪNG", foreground="orange")
        self.step_label.config(text="🔄 Bước hiện tại: Đã tạm dừng")
        
        try:
            import json
            pause_data = {
                "state": "PAUSED",
                "current_step": "User paused from GUI",
                "progress": 50,
                "timestamp": datetime.now().isoformat()
            }
            
            with open("pause_signal.json", "w", encoding="utf-8") as f:
                json.dump(pause_data, f, ensure_ascii=False, indent=2)
            
            self.log_message("✅ ĐÃ GỬI TÍN HIỆU TẠM DỪNG!")
            
        except Exception as e:
            self.log_message(f"❌ LỖI TẠM DỪNG: {e}")
        
        self.pause_btn.config(state='disabled')
        self.resume_btn.config(state='normal')
    
    def resume_automation(self):
        """Tiếp tục automation"""
        self.log_message("▶️ ĐANG TIẾP TỤC AUTOMATION...")
        self.status_label.config(text="📢 Trạng thái: ▶️ ĐANG CHẠY", foreground="green")
        self.step_label.config(text="🔄 Bước hiện tại: Đã tiếp tục")
        
        try:
            if os.path.exists("pause_signal.json"):
                os.remove("pause_signal.json")
            self.log_message("✅ ĐÃ GỬI TÍN HIỆU TIẾP TỤC!")
            
        except Exception as e:
            self.log_message(f"❌ LỖI TIẾP TỤC: {e}")
        
        self.pause_btn.config(state='normal')
        self.resume_btn.config(state='disabled')
    
    def stop_automation(self):
        """Dừng automation"""
        self.log_message("🛑 ĐANG DỪNG AUTOMATION...")
        
        if self.process:
            try:
                self.process.terminate()
                self.log_message("✅ ĐÃ DỪNG AUTOMATION")
            except:
                self.log_message("⚠️ Process đã kết thúc")
        
        # Clear pause signal
        try:
            if os.path.exists("pause_signal.json"):
                os.remove("pause_signal.json")
        except:
            pass
        
        self.status_label.config(text="📢 Trạng thái: ⏹️ ĐÃ DỪNG", foreground="red")
        self.step_label.config(text="🔄 Bước hiện tại: Đã kết thúc")
        self.progress['value'] = 0
        self.progress_label.config(text="0%")
        
        self.reset_buttons()
    
    def reset_buttons(self):
        """Reset trạng thái nút"""
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self.resume_btn.config(state='disabled')
        self.stop_btn.config(state='disabled')
    
    def check_course_and_class(self):
        """Kiểm tra CẢ mã học phần (tên môn) VÀ tên lớp tín chỉ với file Excel"""
        try:
            # Kiểm tra file Excel có tồn tại không
            excel_file = self.excel_path_entry.get().strip()
            if not excel_file:
                excel_file = "lophoc.xlsx"
                
            if not os.path.exists(excel_file):
                messagebox.showerror("Lỗi", f"Không tìm thấy file {excel_file}!\nVui lòng chọn file lịch học!")
                return
            
            # Đọc danh sách từ Treeview
            saved_data = []
            for child in self.course_tree.get_children():
                values = self.course_tree.item(child)['values']
                if len(values) >= 3:
                    saved_data.append({
                        'index': values[0],
                        'subject': values[1],  # Tên môn (sẽ so sánh với Mã_học_phần)
                        'class': values[2]      # Tên lớp (sẽ so sánh với Tên_lớp_tín_chỉ)
                    })
            
            if not saved_data:
                messagebox.showwarning("Cảnh báo", "Chưa có lớp nào được lưu để kiểm tra!")
                return
            
            # Đọc file Excel
            self.log_message("📖 Đang đọc file lophoc.xlsx...")
            df = pd.read_excel(excel_file)
            
            # Lấy danh sách mã học phần và tên lớp từ Excel
            excel_courses = df['Mã học phần'].dropna().unique().tolist()
            excel_classes = df['Tên lớp tín chỉ'].dropna().unique().tolist()
            
            # Helper function: Trích xuất mã học phần từ tên lớp
            def extract_course_code(class_name):
                """Trích xuất mã học phần từ tên lớp (phần trước dấu _)"""
                if '_' in class_name:
                    return class_name.split('_')[0]
                return class_name
            
            # Kiểm tra từng môn - CHỈ BÁO ĐÚNG KHI EXACT MATCH 100%
            errors = []
            auto_fixed = False
            
            for idx, item in enumerate(saved_data):
                subject_input = item['subject'].strip()  # Mã môn user nhập
                class_input = item['class'].strip()      # Tên lớp user nhập
                
                # BƯỚC 1: Kiểm tra EXACT MATCH tên lớp trước
                class_exact_match = class_input in excel_classes
                
                # BƯỚC 2: Tìm mã môn đúng từ Excel (dựa vào tên lớp hoặc trích xuất)
                correct_course = None
                correct_class = None
                
                if class_exact_match:
                    # Lớp đúng -> lấy mã môn từ Excel
                    matching_rows = df[df['Tên lớp tín chỉ'] == class_input]
                    if not matching_rows.empty:
                        correct_course = matching_rows.iloc[0]['Mã học phần']
                        correct_class = class_input
                else:
                    # Lớp sai -> tìm lớp gần giống
                    best_class_match = process.extractOne(class_input, excel_classes, scorer=fuzz.ratio)
                    if best_class_match and best_class_match[1] >= 85:  # Tăng độ chính xác lên 85%
                        suggested_class_name = best_class_match[0]
                        # Lấy mã môn từ lớp gợi ý
                        matching_rows = df[df['Tên lớp tín chỉ'] == suggested_class_name]
                        if not matching_rows.empty:
                            correct_course = matching_rows.iloc[0]['Mã học phần']
                            correct_class = suggested_class_name
                    
                    # Nếu không tìm được, thử trích xuất mã từ tên lớp input
                    if not correct_course:
                        extracted = extract_course_code(class_input)
                        if extracted in excel_courses:
                            correct_course = extracted
                
                # BƯỚC 3: Kiểm tra mã môn user nhập
                course_exact_match = subject_input in excel_courses
                
                # BƯỚC 4: Xác định xem có đúng 100% không
                is_perfect = False
                if course_exact_match and class_exact_match:
                    # Kiểm tra combo có khớp trong Excel không
                    combo_rows = df[
                        (df['Mã học phần'] == subject_input) &
                        (df['Tên lớp tín chỉ'] == class_input)
                    ]
                    is_perfect = not combo_rows.empty
                
                # BƯỚC 5: Ghi nhận kết quả
                if is_perfect:
                    # ĐÚNG 100%
                    self.log_message(f"✅ ĐÚNG 100%: [{subject_input}] - [{class_input}]")
                else:
                    # SAI - Cần sửa
                    self.log_message(f"❌ SAI: [{subject_input}] - [{class_input}]")
                    
                    error_info = {
                        'index': idx,
                        'subject_input': subject_input,
                        'class_input': class_input,
                        'correct_course': correct_course,
                        'correct_class': correct_class,
                        'course_exact': course_exact_match,
                        'class_exact': class_exact_match
                    }
                    errors.append(error_info)
                    
                    # Tự động sửa nếu tìm được combo đúng
                    if correct_course and correct_class:
                        # Kiểm tra lại combo có hợp lệ không
                        verify_rows = df[
                            (df['Mã học phần'] == correct_course) &
                            (df['Tên lớp tín chỉ'] == correct_class)
                        ]
                        if not verify_rows.empty:
                            children = self.course_tree.get_children()
                            if idx < len(children):
                                child = children[idx]
                                values = list(self.course_tree.item(child)['values'])
                                values[1] = correct_course
                                values[2] = correct_class
                                self.course_tree.item(child, values=tuple(values))
                                auto_fixed = True
                                self.log_message(f"   🔧 Đã sửa thành: [{correct_course}] - [{correct_class}]")
            
            # Hiển thị kết quả
            if errors:
                message = "❌ PHÁT HIỆN LỖI - CHƯA ĐÚNG 100%:\n\n"
                
                for error in errors:
                    message += "="*50 + "\n"
                    message += f"📌 BẠN NHẬP:\n"
                    message += f"   Mã môn: {error['subject_input']}\n"
                    message += f"   Tên lớp: {error['class_input']}\n\n"
                    
                    # Phân tích lỗi
                    if not error['course_exact']:
                        message += f"❌ MÃ MÔN SAI (không tồn tại trong Excel)\n"
                    if not error['class_exact']:
                        message += f"❌ TÊN LỚP SAI (không tồn tại trong Excel)\n"
                    
                    # Gợi ý sửa
                    if error['correct_course'] and error['correct_class']:
                        message += f"\n✅ GỢI Ý SỬA THÀNH:\n"
                        message += f"   Mã môn: {error['correct_course']}\n"
                        message += f"   Tên lớp: {error['correct_class']}\n"
                    else:
                        message += f"\n⚠️ Không tìm thấy lớp tương tự trong Excel!\n"
                    
                    message += "\n"
                
                if auto_fixed:
                    message += "\n✅ Đã TỰ ĐỘNG SỬA các lỗi!\n"
                    message += "⚠️ Vui lòng kiểm tra và nhấn LƯU CẤU HÌNH!"
                else:
                    message += "\n⚠️ Không thể tự động sửa!\n"
                    message += "Vui lòng nhập lại cho chính xác theo Excel."
                    
                messagebox.showwarning("Kết quả kiểm tra", message)
            else:
                message = "✅ TẤT CẢ ĐỀU ĐÚNG!\n\n"
                message += f"🎯 Đã kiểm tra {len(saved_data)} lớp\n"
                message += "✅ Mã học phần: Đúng\n"
                message += "✅ Tên lớp tín chỉ: Đúng\n"
                message += "✅ Combo mã + lớp: Khớp"
                messagebox.showinfo("Kết quả kiểm tra", message)
                self.log_message("✅ Tất cả mã học phần và lớp đều hợp lệ!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi kiểm tra: {e}")
            self.log_message(f"❌ Lỗi kiểm tra: {e}")
    
    def check_schedule_only(self):
        """Chỉ kiểm tra trùng lịch học (không check mã học phần hay lớp)"""
        try:
            # Kiểm tra file Excel
            excel_file = self.excel_path_entry.get().strip()
            if not excel_file:
                excel_file = "lophoc.xlsx"
                
            if not os.path.exists(excel_file):
                messagebox.showerror("Lỗi", f"Không tìm thấy file {excel_file}!")
                return
            
            # Đọc danh sách lớp từ Treeview
            saved_classes = []
            for child in self.course_tree.get_children():
                values = self.course_tree.item(child)['values']
                if len(values) >= 3:
                    saved_classes.append(values[2].strip())  # Tên lớp
            
            if not saved_classes:
                messagebox.showwarning("Cảnh báo", "Chưa có lớp nào để kiểm tra!")
                return
            
            # Đọc Excel
            self.log_message("📅 Đang kiểm tra trùng lịch học...")
            df = pd.read_excel(excel_file)
            
            # Gọi hàm kiểm tra trùng lịch
            self.check_schedule_conflicts(df, saved_classes)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi kiểm tra lịch: {e}")
            self.log_message(f"❌ Lỗi: {e}")
    
    def check_schedule_conflicts(self, df, saved_classes):
        """Kiểm tra trùng lịch học giữa các lớp đã chọn"""
        try:
            self.log_message("\n🔍 Đang kiểm tra trùng lịch học...")
            self.log_message(f"📋 Số lớp cần kiểm tra: {len(saved_classes)}")
            
            # Lọc các lớp đã lưu từ DataFrame
            class_schedules = []
            for class_name in saved_classes:
                class_name_clean = class_name.strip()
                self.log_message(f"  🔎 Đang tìm: {class_name_clean}")
                matching_rows = df[df['Tên lớp tín chỉ'] == class_name_clean]
                
                if not matching_rows.empty:
                    row = matching_rows.iloc[0]
                    ca_hoc = str(row['Ca học']) if 'Ca học' in df.columns else ""
                    lich_hoc = str(row['Lịch học']) if 'Lịch học' in df.columns else ""
                    schedule = f"{ca_hoc}\n{lich_hoc}".strip()
                    
                    subject = row['Tên học phần']
                    self.log_message(f"  ✅ Tìm thấy: {subject} - {class_name_clean}")
                    if schedule and schedule != "\nnan":
                        class_schedules.append({
                            'subject': subject,
                            'class': class_name_clean,
                            'schedule': schedule
                        })
                        self.log_message(f"     📅 Lịch: {schedule}")
                    else:
                        self.log_message(f"  ⚠️ Lớp {class_name_clean} không có lịch học")
                else:
                    self.log_message(f"  ❌ Không tìm thấy: {class_name_clean}")
            
            # So sánh lịch học giữa các lớp
            self.log_message(f"\n🔄 So sánh {len(class_schedules)} lớp với nhau...")
            conflicts = []
            for i in range(len(class_schedules)):
                for j in range(i + 1, len(class_schedules)):
                    schedule1 = class_schedules[i]['schedule']
                    schedule2 = class_schedules[j]['schedule']
                    
                    self.log_message(f"  So sánh: {class_schedules[i]['class']} vs {class_schedules[j]['class']}")
                    
                    # So sánh lịch học (nếu giống nhau hoặc tương tự)
                    if schedule1 == schedule2:
                        self.log_message(f"    ⚠️ TRÙNG HOÀN TOÀN!")
                        conflicts.append({
                            'class1': class_schedules[i],
                            'class2': class_schedules[j],
                            'type': 'exact'
                        })
                    # Kiểm tra xem có overlap về thời gian không
                    elif self.check_time_overlap(schedule1, schedule2):
                        self.log_message(f"    ⚠️ TRÙNG THỜI GIAN!")
                        conflicts.append({
                            'class1': class_schedules[i],
                            'class2': class_schedules[j],
                            'type': 'overlap'
                        })
                    else:
                        self.log_message(f"    ✅ Không trùng")
            
            # Hiển thị kết quả
            self.log_message(f"\n📊 Kết quả: Tìm thấy {len(conflicts)} trường hợp trùng lịch")
            
            if conflicts:
                # Lưu conflicts để dùng cho suggest alternative
                self.last_conflicts = conflicts
                self.last_df = df
                
                message = "⚠️ PHÁT HIỆN TRÙNG LỊCH HỌC:\n\n"
                for idx, conflict in enumerate(conflicts, 1):
                    c1 = conflict['class1']
                    c2 = conflict['class2']
                    conflict_type = "TRÙNG HOÀN TOÀN" if conflict['type'] == 'exact' else "TRÙNG THỜI GIAN"
                    
                    message += f"#{idx} 🔴 {conflict_type}:\n"
                    message += f"   📚 Môn 1: {c1['subject']} - {c1['class']}\n"
                    message += f"   📅 Lịch: {c1['schedule']}\n\n"
                    message += f"   📚 Môn 2: {c2['subject']} - {c2['class']}\n"
                    message += f"   📅 Lịch: {c2['schedule']}\n"
                    message += "\n" + "="*50 + "\n\n"
                
                message += "💡 Nhấn nút 'Gợi ý lớp thay thế' để tìm lớp không trùng lịch!"
                
                self.log_message(f"⚠️ Hiển thị thông báo trùng lịch...")
                messagebox.showwarning("Trùng lịch học", message)
                self.log_message(f"⚠️ Phát hiện {len(conflicts)} trường hợp trùng lịch!")
            else:
                self.last_conflicts = None
                self.log_message("✅ Không có trùng lịch, hiển thị thông báo...")
                messagebox.showinfo("Kết quả", "✅ Không có lớp nào trùng lịch học!")
                self.log_message("✅ Không có trùng lịch học")
                
        except Exception as e:
            error_msg = f"❌ Lỗi kiểm tra lịch: {e}"
            self.log_message(error_msg)
            messagebox.showerror("Lỗi", error_msg)
            import traceback
            self.log_message(traceback.format_exc())
    
    def suggest_alternative_classes(self):
        """Gợi ý lớp thay thế cho các lớp bị trùng lịch"""
        try:
            # Kiểm tra có conflict nào không
            if not hasattr(self, 'last_conflicts') or not self.last_conflicts:
                messagebox.showinfo("Thông báo", "Vui lòng chạy 'Check trùng lịch' trước!")
                return
            
            df = self.last_df
            conflicts = self.last_conflicts
            
            self.log_message("\n💡 Đang tìm lớp thay thế...")
            
            # Lấy tất cả lớp hiện tại và lịch của chúng
            current_classes = []
            for child in self.course_tree.get_children():
                values = self.course_tree.item(child)['values']
                if len(values) >= 3:
                    class_name = values[2].strip()
                    current_classes.append(class_name)
            
            # Lấy tất cả lịch học hiện tại
            current_schedules = []
            for class_name in current_classes:
                matching_rows = df[df['Tên lớp tín chỉ'] == class_name]
                if not matching_rows.empty:
                    row = matching_rows.iloc[0]
                    ca_hoc = str(row['Ca học']) if 'Ca học' in df.columns else ""
                    lich_hoc = str(row['Lịch học']) if 'Lịch học' in df.columns else ""
                    schedule = f"{ca_hoc}\n{lich_hoc}".strip()
                    
                    if schedule and schedule != "\nnan":
                        current_schedules.append(schedule)
            
            # Tìm lớp thay thế cho từng conflict
            suggestions = []
            
            for conflict in conflicts:
                c1 = conflict['class1']
                c2 = conflict['class2']
                
                # Ưu tiên sửa lớp thứ 2
                class_to_replace = c2['class']
                
                # Trích xuất mã môn học từ tên lớp
                course_code = class_to_replace.split('_')[0] if '_' in class_to_replace else class_to_replace
                
                self.log_message(f"\n🔍 Tìm lớp thay thế cho: {class_to_replace}")
                self.log_message(f"   Mã môn: {course_code}")
                
                # Tìm tất cả lớp cùng môn học
                same_course_classes = df[df['Mã học phần'] == course_code]
                
                if same_course_classes.empty:
                    self.log_message(f"   ❌ Không tìm thấy lớp nào cùng môn {course_code}")
                    continue
                
                # Tìm lớp không trùng lịch với tất cả lớp hiện tại
                alternatives = []
                for idx, row in same_course_classes.iterrows():
                    alt_class = row['Tên lớp tín chỉ']
                    ca_hoc = str(row['Ca học']) if 'Ca học' in df.columns else ""
                    lich_hoc = str(row['Lịch học']) if 'Lịch học' in df.columns else ""
                    alt_schedule = f"{ca_hoc}\n{lich_hoc}".strip()
                    
                    if not alt_schedule or alt_schedule == "\nnan":
                        alt_schedule = None
                    
                    if alt_class == class_to_replace:
                        continue  # Bỏ qua lớp hiện tại
                    
                    if not alt_schedule:
                        continue
                    
                    # Kiểm tra xem lớp này có trùng với lớp nào đang có không
                    has_conflict = False
                    for existing_schedule in current_schedules:
                        if existing_schedule != c2['schedule']:  # Không so sánh với chính nó
                            if alt_schedule == existing_schedule or self.check_time_overlap(alt_schedule, existing_schedule):
                                has_conflict = True
                                break
                    
                    if not has_conflict:
                        alternatives.append({
                            'class': alt_class,
                            'schedule': alt_schedule,
                            'slots': row.get('Còn_trống', '?')
                        })
                        self.log_message(f"   ✅ Tìm thấy: {alt_class} - Lịch: {alt_schedule}")
                
                if alternatives:
                    suggestions.append({
                        'original': class_to_replace,
                        'original_schedule': c2['schedule'],
                        'alternatives': alternatives,
                        'conflict_with': c1['class']
                    })
                else:
                    self.log_message(f"   ⚠️ Không tìm thấy lớp thay thế phù hợp")
            
            # Hiển thị gợi ý
            if not suggestions:
                messagebox.showinfo("Kết quả", "❌ Không tìm thấy lớp thay thế phù hợp nào!")
                return
            
            # Tạo dialog để user chọn
            self.show_suggestion_dialog(suggestions)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tìm lớp thay thế: {e}")
            self.log_message(f"❌ Lỗi: {e}")
            import traceback
            self.log_message(traceback.format_exc())
    
    def show_suggestion_dialog(self, suggestions):
        """Hiển thị dialog cho user chọn lớp thay thế"""
        # Tạo window mới
        dialog = tk.Toplevel(self.root)
        dialog.title("💡 Gợi ý lớp thay thế")
        dialog.geometry("800x600")
        
        # Frame chính
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label title
        title_label = ttk.Label(main_frame, text="💡 GỢI Ý LỚP THAY THẾ", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Scrolled frame
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Dictionary để lưu user selections
        selections = {}
        
        # Hiển thị từng suggestion
        for idx, suggestion in enumerate(suggestions):
            # Frame cho mỗi suggestion
            sug_frame = ttk.LabelFrame(scrollable_frame, text=f"Trùng #{idx+1}", padding="10")
            sug_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Thông tin lớp hiện tại
            info_text = f"❌ Lớp bị trùng: {suggestion['original']}\n"
            info_text += f"📅 Lịch: {suggestion['original_schedule']}\n"
            info_text += f"🔴 Trùng với: {suggestion['conflict_with']}\n\n"
            info_text += f"✅ Có {len(suggestion['alternatives'])} lớp thay thế:\n"
            
            info_label = ttk.Label(sug_frame, text=info_text, font=('Arial', 9))
            info_label.pack(anchor=tk.W)
            
            # Radio buttons cho alternatives
            var = tk.StringVar(value="KEEP")  # Mặc định giữ nguyên
            selections[suggestion['original']] = var
            
            # Option: Giữ nguyên
            keep_radio = ttk.Radiobutton(sug_frame, text="🔒 Giữ nguyên (không thay đổi)", 
                                        variable=var, value="KEEP")
            keep_radio.pack(anchor=tk.W, padx=20)
            
            # Options: Các lớp thay thế
            for alt_idx, alt in enumerate(suggestion['alternatives'][:5]):  # Giới hạn 5 lớp
                text = f"✅ {alt['class']}\n"
                text += f"    📅 Lịch: {alt['schedule']}\n"
                text += f"    💺 Còn trống: {alt['slots']}"
                
                alt_radio = ttk.Radiobutton(sug_frame, text=text, 
                                           variable=var, value=alt['class'])
                alt_radio.pack(anchor=tk.W, padx=20, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def apply_changes():
            """Áp dụng thay đổi"""
            changes_made = False
            
            for original_class, var in selections.items():
                new_class = var.get()
                
                if new_class != "KEEP" and new_class != original_class:
                    # Tìm và thay thế trong Treeview
                    for child in self.course_tree.get_children():
                        values = list(self.course_tree.item(child)['values'])
                        if len(values) >= 3 and values[2].strip() == original_class:
                            # Cập nhật tên lớp
                            values[2] = new_class
                            
                            # Cập nhật mã môn nếu cần
                            new_course_code = new_class.split('_')[0] if '_' in new_class else new_class
                            values[1] = new_course_code
                            
                            self.course_tree.item(child, values=tuple(values))
                            self.log_message(f"✅ Đã thay: {original_class} → {new_class}")
                            changes_made = True
                            break
            
            if changes_made:
                messagebox.showinfo("Thành công", "✅ Đã cập nhật lớp thay thế!\n\n⚠️ Vui lòng LƯU CẤU HÌNH!")
                dialog.destroy()
            else:
                messagebox.showinfo("Thông báo", "Không có thay đổi nào được áp dụng.")
                dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        ok_btn = ttk.Button(btn_frame, text="✅ Áp dụng", command=apply_changes)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="❌ Hủy", command=cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    # ─────────────────── Phân tích Lịch học (Phiên bản mới - hỗ trợ đa khoảng ngày) ───────────────────

    def parse_schedule_v2(self, ca_hoc_raw: str, lich_hoc_raw: str) -> list:
        """
        Phân tích lịch học đa khoảng ngày.
        Định dạng Ca học: "Sáng | Chiều | Tối"
        Định dạng Lịch học: "02/03/26-05/04/26 | Thứ 3(T1-3) | Thứ 5(T1-3)"
        """
        from datetime import date as _date
        slots = []

        def parse_date(s: str):
            s = s.strip()
            for fmt in ('%d/%m/%y', '%d/%m/%Y'):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    pass
            return None

        def parse_day(token: str):
            m = re.search(r'Th\S*\s*(\d)', token.strip(), re.IGNORECASE)
            if m:
                return int(m.group(1))
            return None

        def parse_periods(token: str):
            m = re.search(r'T(\d+)\s*-\s*(\d+)', token)
            if m:
                return int(m.group(1)), int(m.group(2))
            m2 = re.search(r'T([\d,]+)', token)
            if m2:
                nums = [int(x) for x in re.findall(r'\d+', m2.group(1))]
                if nums:
                    return min(nums), max(nums)
            if 'Sáng' in token or 'sang' in token.lower():
                return 1, 5
            if 'Chiều' in token or 'chieu' in token.lower():
                return 6, 10
            if 'Tối' in token or 'toi' in token.lower():
                return 11, 13
            return None, None

        ca_hoc_raw = ca_hoc_raw.replace('\n', '|')
        lich_hoc_raw = lich_hoc_raw.replace('\n', '|')
        
        sessions_raw = [s.strip() for s in ca_hoc_raw.split('|') if s.strip()]
        tokens = [t.strip() for t in lich_hoc_raw.split('|') if t.strip()]

        current_date_from = None
        current_date_to   = None
        session_idx = 0

        for i, token in enumerate(tokens):
            if not token:
                continue
                
            # Nếu token là 1 khoảng ngày -> Cập nhật mốc thời gian đang xét
            date_range_match = re.match(r'(\d{2}/\d{2}/\d{2,4})\s*-\s*(\d{2}/\d{2}/\d{2,4})', token)
            if date_range_match:
                df = parse_date(date_range_match.group(1))
                dt = parse_date(date_range_match.group(2))
                
                # NẾU CÓ NEXT RANGE (khoảng ngày tiếp theo), cắt EndDate sớm lại nếu nó đè lên
                # Nhìn về phía trước trong tokens xem có khoảng ngày nào nhỏ hơn hoặc bằng dt không?
                next_dt_start = None
                for j in range(i + 1, len(tokens)):
                    m_next = re.match(r'(\d{2}/\d{2}/\d{2,4})\s*-\s*(\d{2}/\d{2}/\d{2,4})', tokens[j])
                    if m_next:
                        next_dt_start = parse_date(m_next.group(1))
                        break
                
                from datetime import timedelta
                # Nếu khoảng tiếp theo bắt đầu SỚM HƠN HOẶC BẰNG dt của mình => cắt dt của mình lại ngay trước nó
                if next_dt_start and dt and next_dt_start <= dt:
                    dt = next_dt_start - timedelta(days=1)
                
                current_date_from = df
                current_date_to   = dt
                continue

            # Nếu token là Thứ (Thứ 3, Thứ 4...) -> Tạo slot với mốc thời gian gần nhất
            day_num = parse_day(token)
            if day_num is not None:
                start_p, end_p = parse_periods(token)
                
                # Ánh xạ ca học (ví dụ "Sáng")
                session_label = ""
                if sessions_raw:
                    # Nếu mảng session ngắn hơn số lượng slot thực tế, ta lấy cái cuối cùng
                    idx = min(session_idx, len(sessions_raw) - 1)
                    session_label = sessions_raw[idx]
                
                if start_p is None and session_label:
                    start_p, end_p = parse_periods(session_label)
                
                if start_p is not None:
                    slots.append({
                        'date_from': current_date_from,
                        'date_to':   current_date_to,
                        'day':       day_num,
                        'start':     start_p,
                        'end':       end_p,
                        'session':   session_label
                    })
                
                session_idx += 1

        return slots

    def parse_schedule(self, schedule):
        """Wrapper tương thích ngược với code cũ (chỉ trả về slot đầu tiên)."""
        try:
            text = str(schedule).strip()
            if not text or text == 'nan':
                return None
            parts = text.split('\n')
            ca_hoc  = parts[0].strip() if len(parts) > 0 else ''
            lich_hoc = parts[1].strip() if len(parts) > 1 else ''
            if not ca_hoc:
                ca_hoc = ''
            if not lich_hoc:
                lich_hoc = ca_hoc
                ca_hoc = ''
            slots = self.parse_schedule_v2(ca_hoc, lich_hoc)
            if slots:
                s = slots[0]
                return {'day': s['day'], 'start': s['start'], 'end': s['end']}
        except Exception:
            pass
        return None

    def check_time_overlap(self, schedule1, schedule2):
        """Kiểm tra trùng lịch giữa 2 môn, xét cả khoảng ngày học."""
        try:
            def get_slots(sched):
                text = str(sched).strip()
                if not text or text == 'nan':
                    return []
                parts = text.split('\n')
                ca   = parts[0].strip() if len(parts) > 0 else ''
                lich = parts[1].strip() if len(parts) > 1 else ''
                if not lich:
                    lich, ca = ca, ''
                return self.parse_schedule_v2(ca, lich)

            slots1 = get_slots(schedule1)
            slots2 = get_slots(schedule2)

            for s1 in slots1:
                for s2 in slots2:
                    # Cùng thứ trong tuần
                    if s1['day'] != s2['day']:
                        continue
                    # Trùng tiết
                    if not (s1['start'] <= s2['end'] and s1['end'] >= s2['start']):
                        continue
                    # Kiểm tra khoảng ngày có giao nhau không
                    d1_from = s1.get('date_from')
                    d1_to   = s1.get('date_to')
                    d2_from = s2.get('date_from')
                    d2_to   = s2.get('date_to')
                    # Nếu một trong hai không có ngày → coi là trùng
                    if None in (d1_from, d1_to, d2_from, d2_to):
                        return True
                    # Khoảng [d1_from, d1_to] giao với [d2_from, d2_to]
                    if d1_from <= d2_to and d1_to >= d2_from:
                        return True
            return False
        except Exception:
            return False

    
    def show_timetable(self):
        """Hiển thị thời khóa biểu dạng bảng"""
        try:
            excel_file = self.excel_path_entry.get().strip()
            if not excel_file:
                excel_file = "lophoc.xlsx"
            if not os.path.exists(excel_file):
                messagebox.showerror("Lỗi", f"Không tìm thấy file {excel_file}!")
                return

            saved_classes = []
            for child in self.course_tree.get_children():
                values = self.course_tree.item(child)['values']
                if len(values) >= 3:
                    saved_classes.append({'subject': values[1].strip(), 'class': values[2].strip()})

            if not saved_classes:
                messagebox.showwarning("Cảnh báo", "Chưa có lớp nào để xem thời khóa biểu!")
                return

            df = pd.read_excel(excel_file)

            # ── Thu thập tất cả slots từ mỗi môn ──
            # slots_by_subject: [{subject, class, slots: [slot_dict, ...]}]
            subjects_slots = []
            for class_info in saved_classes:
                class_name = class_info['class']
                subject_name = class_info['subject']
                matching = df[df['Tên lớp tín chỉ'] == class_name]
                if matching.empty:
                    continue
                row = matching.iloc[0]
                ca_hoc  = str(row.get('Ca học', '')) if 'Ca học' in df.columns else ''
                lich_hoc = str(row.get('Lịch học', '')) if 'Lịch học' in df.columns else ''
                if ca_hoc == 'nan': ca_hoc = ''
                if lich_hoc == 'nan': lich_hoc = ''
                slots = self.parse_schedule_v2(ca_hoc, lich_hoc)
                if slots:
                    subjects_slots.append({'subject': subject_name, 'class': class_name, 'slots': slots})

            self.display_timetable_window(subjects_slots)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tạo thời khóa biểu: {e}")
            self.log_message(f"❌ Lỗi: {e}")
    
    def display_timetable_window(self, subjects_slots: list):
        """Hiển thị thời khóa biểu với điều hướng theo tuần."""
        from datetime import date, timedelta
        from collections import defaultdict

        dialog = tk.Toplevel(self.root)
        dialog.title("📅 THỜI KHÓA BIỂU")
        dialog.geometry("1350x860")
        dialog.resizable(True, True)

        DAY_NAMES = {2:'Thứ 2', 3:'Thứ 3', 4:'Thứ 4', 5:'Thứ 5', 6:'Thứ 6', 7:'Thứ 7'}
        DAYS      = [2, 3, 4, 5, 6, 7]
        COLORS    = ['#d0f0c0','#c0e0ff','#ffe4b5','#ffd7e0','#e0d4f7','#d4f7f7','#fff4cc']

        # ── Tính màu cho từng môn (1 lần) ──
        subject_color = {}
        ci = 0
        for entry in subjects_slots:
            s = entry['subject']
            if s not in subject_color:
                subject_color[s] = COLORS[ci % len(COLORS)]
                ci += 1

        # ── Tính tuần hiện tại (Thứ 2 → Thứ 7) ──
        today = date.today()
        week_start_var = [today - timedelta(days=today.weekday())]  # Thứ 2 của tuần hiện tại

        # ── UI: thanh điều hướng (top) ──
        top = ttk.Frame(dialog, padding=(8, 6))
        top.pack(fill=tk.X)

        ttk.Label(top, text="📅 THỜI KHÓA BIỂU", font=('Segoe UI', 13, 'bold'),
                  foreground='#0078D4').pack(side=tk.LEFT, padx=(0, 20))

        nav = ttk.Frame(top)
        nav.pack(side=tk.LEFT)

        prev_btn = ttk.Button(nav, text="◀ Tuần trước", width=14)
        prev_btn.pack(side=tk.LEFT, padx=3)

        week_label = ttk.Label(nav, text="", font=('Segoe UI', 10, 'bold'), width=30, anchor='center')
        week_label.pack(side=tk.LEFT, padx=6)

        next_btn = ttk.Button(nav, text="Tuần sau ▶", width=14)
        next_btn.pack(side=tk.LEFT, padx=3)

        # ── Bộ chọn ngày tự do ──
        ttk.Separator(top, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Label(top, text="Từ ngày:").pack(side=tk.LEFT)
        from_var = tk.StringVar()
        from_entry = ttk.Entry(top, textvariable=from_var, width=11)
        from_entry.pack(side=tk.LEFT, padx=(2, 6))

        ttk.Label(top, text="Đến:").pack(side=tk.LEFT)
        to_var = tk.StringVar()
        to_entry = ttk.Entry(top, textvariable=to_var, width=11)
        to_entry.pack(side=tk.LEFT, padx=(2, 6))

        go_btn = ttk.Button(top, text="🔍 Xem", width=8)
        go_btn.pack(side=tk.LEFT, padx=3)

        ttk.Label(top, text="(dd/mm/yy)", foreground='gray',
                  font=('Segoe UI', 8)).pack(side=tk.LEFT)

        # ── Scrollable canvas (content) ──
        content = ttk.Frame(dialog)
        content.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        canvas = tk.Canvas(content, bg='#f7f8fa')
        vsb = ttk.Scrollbar(content, orient='vertical',   command=canvas.yview)
        hsb = ttk.Scrollbar(content, orient='horizontal', command=canvas.xview)
        scrollable = tk.Frame(canvas, bg='#f7f8fa')
        scrollable.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        canvas.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

        # ── Hàm dựng bảng TKB cho 1 tuần (week_mon → week_sat) ──
        def build_table(week_mon: date):
            week_sat = week_mon + timedelta(days=5)  # Thứ 7

            # Cập nhật nhãn tuần
            week_label.config(
                text=f"{week_mon.strftime('%d/%m/%Y')}  ─  {week_sat.strftime('%d/%m/%Y')}"
            )

            # Xoá nội dung cũ
            for w in scrollable.winfo_children():
                w.destroy()

            # Lọc slots: lấy slot nào có khoảng ngày giao với tuần đang xem
            # (date_from ≤ week_sat) AND (date_to ≥ week_mon)
            # Nếu slot không có ngày → hiển thị luôn
            tbl_data = defaultdict(lambda: defaultdict(list))
            # tbl_data[day][period] = [(text, color), ...]

            for entry in subjects_slots:
                subj = entry['subject']
                col  = subject_color[subj]
                for slot in entry['slots']:
                    df = slot.get('date_from')
                    dt = slot.get('date_to')
                    # Kiểm tra giao nhau
                    if df and dt:
                        if df > week_sat or dt < week_mon:
                            continue  # không học tuần này
                    label = f"{subj}\n({slot['session']})" if slot.get('session') else subj
                    day = slot['day']
                    for p in range(slot['start'], slot['end'] + 1):
                        tbl_data[day][p].append((label, col))

            # ── Vẽ header ──
            def lbl(parent, text, bg, fg='#1a1a1a', bold=False, w=6, h=1):
                font = ('Segoe UI', 8, 'bold') if bold else ('Segoe UI', 8)
                return tk.Label(parent, text=text, font=font, bg=bg, fg=fg,
                                relief='ridge', bd=1, width=w, height=h,
                                anchor='center', wraplength=140, justify='center')

            lbl(scrollable, 'Tiết', '#2c3e50', fg='white', bold=True, w=5
                ).grid(row=0, column=0, sticky='nsew', padx=1, pady=1)

            # Đánh dấu ngày thực tế trong tuần lên header
            for ci2, day in enumerate(DAYS, 1):
                actual_date = week_mon + timedelta(days=day - 2)
                hdr_text = f"{DAY_NAMES[day]}\n{actual_date.strftime('%d/%m')}"
                bg_hdr = '#0078D4' if actual_date != today else '#e67e22'
                lbl(scrollable, hdr_text, bg_hdr, fg='white', bold=True, w=20, h=2
                    ).grid(row=0, column=ci2, sticky='nsew', padx=1, pady=1)

            # ── Vẽ các tiết ──
            for p in range(1, 16):
                lbl(scrollable, f'T{p}', '#ecf0f1', bold=False, w=5
                    ).grid(row=p, column=0, sticky='nsew', padx=1, pady=1)
                for ci2, day in enumerate(DAYS, 1):
                    entries = tbl_data.get(day, {}).get(p, [])
                    if entries:
                        unique_texts = list(dict.fromkeys(e[0] for e in entries))
                        text = '\n'.join(unique_texts)
                        bg   = entries[0][1]
                        if len(unique_texts) > 1:
                            bg, text = '#ff6b6b', '⚠️ TRÙNG!\n' + text
                    else:
                        text, bg = '', '#fafafa'
                    lbl(scrollable, text, bg, w=20, h=3
                        ).grid(row=p, column=ci2, sticky='nsew', padx=1, pady=1)

        # ── Các hàm điều hướng ──
        def go_prev():
            week_start_var[0] -= timedelta(weeks=1)
            build_table(week_start_var[0])

        def go_next():
            week_start_var[0] += timedelta(weeks=1)
            build_table(week_start_var[0])

        def go_custom():
            try:
                from datetime import datetime as _dt
                d_from = _dt.strptime(from_var.get().strip(), '%d/%m/%y').date()
                # Lấy thứ 2 của tuần chứa d_from
                week_start_var[0] = d_from - timedelta(days=d_from.weekday())
                build_table(week_start_var[0])
            except ValueError:
                messagebox.showerror("Lỗi", "Định dạng ngày sai!\nVui lòng nhập: dd/mm/yy (ví dụ: 02/03/26)", parent=dialog)

        prev_btn.config(command=go_prev)
        next_btn.config(command=go_next)
        go_btn.config(command=go_custom)

        # ── Phím tắt: mũi tên trái/phải ──
        dialog.bind('<Left>',  lambda e: go_prev())
        dialog.bind('<Right>', lambda e: go_next())

        # ── Build lần đầu (tuần hiện tại) ──
        build_table(week_start_var[0])

        # ── Nút đóng ──
        ttk.Button(dialog, text="❌ Đóng", command=dialog.destroy).pack(pady=5)



def main():
    """Chạy Complete GUI – kiểm tra bản quyền trước khi mở."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        root = tk.Tk()
        root.withdraw()  # Ẩn cửa sổ chính lúc đầu

        # ── Kiểm tra bản quyền ──
        result = license_manager.check_license()

        if result["valid"]:
            # Bản quyền hợp lệ → mở thẳng tool
            licensed_masv = result["masv"]
            days_left     = result["days_left"]
            expire_date   = result["expire_date"]
            
            root.deiconify()
            app = CompleteGUI(root, licensed_masv=licensed_masv, expire_date=expire_date, days_left=days_left)
            app.log_message(f"✅ Bản quyền hợp lệ | Mã SV: {licensed_masv} | Hết hạn: {expire_date}")

            def on_closing():
                if app.process and app.process.poll() is None:
                    if messagebox.askokcancel("Thoát", "Automation đang chạy. Dừng và thoát?"):
                        app.stop_automation()
                        root.destroy()
                else:
                    root.destroy()

            root.protocol("WM_DELETE_WINDOW", on_closing)
            root.mainloop()

        else:
            # Chưa có hoặc hết hạn → hiện màn hình kích hoạt
            reason = result["reason"]
            print(f"[License] {reason}")

            # Nếu là hết hạn (có masv cũ) → thông báo rõ cho user
            is_expired = result.get("masv") and "hết hạn" in reason.lower()
            if is_expired:
                old_masv = result.get("masv", "")
                old_exp  = result.get("expire_date", "N/A")
                messagebox.showwarning(
                    "⚠️ Bản quyền đã hết hạn",
                    f"Tài khoản {old_masv} đã hết hạn lúc {old_exp}.\n\n"
                    "Vui lòng gia hạn để tiếp tục sử dụng!\n"
                    "→ Quét mã QR hoặc nhập Key gia hạn bên dưới."
                )

            def on_activated(masv: str):
                """Callback sau khi kích hoạt xong."""
                # Lấy lại thông tin bản quyền vừa lưu
                res = license_manager.check_license()
                exp = res.get("expire_date", "N/A")
                days = res.get("days_left", 0)
                
                root.deiconify()
                app = CompleteGUI(root, licensed_masv=masv, expire_date=exp, days_left=days)
                app.log_message(f"✅ Kích hoạt thành công | Mã SV: {masv} | Hết hạn: {exp}")

                def on_closing():
                    if app.process and app.process.poll() is None:
                        if messagebox.askokcancel("Thoát", "Automation đang chạy. Dừng và thoát?"):
                            app.stop_automation()
                            root.destroy()
                    else:
                        root.destroy()

                root.protocol("WM_DELETE_WINDOW", on_closing)

            LicenseWindow(root, on_activated)
            root.mainloop()

    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
