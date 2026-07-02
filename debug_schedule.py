import re
from datetime import datetime, timedelta, date

def parse_schedule_v2(ca_hoc_raw, lich_hoc_raw):
    slots = []
    DAY_MAP = {'Hai': 2, 'Ba': 3, 'Tuu': 4, 'Năm': 5, 'Sáu': 6, 'Bảy': 7,
               'T\u01b0': 4,
               '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7}

    def parse_date(s):
        s = s.strip()
        for fmt in ('%d/%m/%y', '%d/%m/%Y'):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                pass
        return None

    def parse_day(token):
        for k, v in DAY_MAP.items():
            if k in token:
                return v
        return None

    def parse_periods(token):
        m = re.search(r'T(\d+)-(\d+)', token)
        if m:
            return int(m.group(1)), int(m.group(2))
        m2 = re.search(r'T([\d,]+)', token)
        if m2:
            nums = [int(x) for x in re.findall(r'\d+', m2.group(1))]
            if nums:
                return min(nums), max(nums)
        if 'Sáng' in token: return 1, 5
        if 'Chi\u1ec1u' in token: return 6, 10
        if 'T\u1ed1i' in token: return 11, 13
        return None, None

    sessions_raw = [s.strip() for s in ca_hoc_raw.split('|')] if ca_hoc_raw else []
    tokens = [t.strip() for t in lich_hoc_raw.split('|')] if lich_hoc_raw else []

    current_date_from = None
    current_date_to   = None
    session_idx = 0

    print(f"  Ca hoc tokens: {sessions_raw}")
    print(f"  Lich hoc tokens: {tokens}")

    for token in tokens:
        date_range_match = re.match(r'(\d{2}/\d{2}/\d{2,4})\s*-\s*(\d{2}/\d{2}/\d{2,4})', token)
        if date_range_match:
            current_date_from = parse_date(date_range_match.group(1))
            current_date_to   = parse_date(date_range_match.group(2))
            print(f"  >> Range: {current_date_from} => {current_date_to}")
            continue

        day_num = parse_day(token)
        if day_num is not None:
            start_p, end_p = parse_periods(token)
            if start_p is None:
                session_idx += 1
                continue
            session_label = sessions_raw[session_idx] if session_idx < len(sessions_raw) else ''
            slots.append({
                'date_from': current_date_from,
                'date_to':   current_date_to,
                'day':       day_num,
                'start':     start_p,
                'end':       end_p,
                'session':   session_label
            })
            print(f"  >> Slot: Thu {day_num}, T{start_p}-{end_p}, sess='{session_label}', range=({current_date_from} => {current_date_to})")
            session_idx += 1
        else:
            print(f"  ?? Khong nhan biet token: '{token}'")

    return slots


print("=" * 60)
print("TEST 1: 1 khoang ngay, 3 thu")
print("=" * 60)
s1 = parse_schedule_v2(
    "Sáng | Sáng | Sáng",
    "02/03/26-05/04/26 | Thứ 3(T1-3) | Thứ 5(T1-3) | Thứ 7(T1-3)"
)
print(f"=> {len(s1)} slots\n")

print("=" * 60)
print("TEST 2: Nhieu khoang ngay luân phien")
print("=" * 60)
s2 = parse_schedule_v2(
    "Sáng | Sáng | Sáng",
    "09/03/26-19/04/26 | Thứ 4(T1-5) | 13/04/26-19/04/26 | Thứ 7(T1-5) | 20/04/26-03/05/26 | Thứ 4(T1-5)"
)
print(f"=> {len(s2)} slots\n")

# Check week 09/03/2026 for both
def sim_week(slots, week_mon, label):
    week_sat = week_mon + timedelta(days=5)
    print(f"Tuan {label}: {week_mon} => {week_sat}")
    shown = False
    for slot in slots:
        df, dt = slot['date_from'], slot['date_to']
        if df and dt:
            if df > week_sat or dt < week_mon:
                continue
        day_names = {2:'T2', 3:'T3', 4:'T4', 5:'T5', 6:'T6', 7:'T7'}
        print(f"  HIEN: {day_names.get(slot['day'],'?')}, T{slot['start']}-{slot['end']}, sess='{slot['session']}'")
        shown = True
    if not shown:
        print("  (Khong co mon nao hoc tuan nay)")

print("=" * 60)
print("SIMULATE TEST 1")
sim_week(s1, date(2026, 3, 9), "09/03/2026")
sim_week(s1, date(2026, 3, 23), "23/03/2026")

print("=" * 60)
print("SIMULATE TEST 2")
sim_week(s2, date(2026, 3, 9), "09/03/2026")
sim_week(s2, date(2026, 4, 13), "13/04/2026")
sim_week(s2, date(2026, 4, 20), "20/04/2026")
