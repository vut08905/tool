"""
Phương pháp 3: Sử dụng Google Sheets API (Nếu có quyền truy cập)
Yêu cầu: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import json

# Scopes cần thiết
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def authenticate_google_sheets():
    """
    Xác thực với Google Sheets API
    Cần file credentials.json từ Google Cloud Console
    """
    creds = None
    
    # Token được lưu sau lần đăng nhập đầu tiên
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Nếu không có credentials hợp lệ, yêu cầu đăng nhập
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Lưu credentials cho lần sau
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def read_google_sheet(spreadsheet_id, range_name='Sheet1'):
    """
    Đọc dữ liệu từ Google Sheet
    
    Args:
        spreadsheet_id: ID của spreadsheet (từ URL)
        range_name: Range cần đọc (vd: 'Sheet1', 'Sheet1!A1:Z1000')
    """
    try:
        creds = authenticate_google_sheets()
        service = build('sheets', 'v4', credentials=creds)
        
        # Gọi API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('Không tìm thấy dữ liệu.')
            return None
        
        print(f'✓ Đã đọc {len(values)} rows')
        
        # Lưu vào file
        output_file = f'{spreadsheet_id}_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(values, f, ensure_ascii=False, indent=2)
        
        print(f'✓ Đã lưu vào {output_file}')
        
        return values
        
    except Exception as e:
        print(f'Lỗi: {e}')
        return None

def get_all_sheets_data(spreadsheet_id):
    """
    Lấy dữ liệu từ tất cả sheets trong spreadsheet
    """
    try:
        creds = authenticate_google_sheets()
        service = build('sheets', 'v4', credentials=creds)
        
        # Lấy metadata để biết có bao nhiêu sheets
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        sheets = spreadsheet.get('sheets', [])
        all_data = {}
        
        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            print(f'Đang đọc sheet: {sheet_name}')
            
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=sheet_name
            ).execute()
            
            values = result.get('values', [])
            all_data[sheet_name] = values
            print(f'  ✓ {len(values)} rows')
        
        # Lưu tất cả
        output_file = f'{spreadsheet_id}_all_sheets.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f'\n✓ Đã lưu tất cả sheets vào {output_file}')
        return all_data
        
    except Exception as e:
        print(f'Lỗi: {e}')
        return None


# Sử dụng
if __name__ == '__main__':
    # Lấy SPREADSHEET_ID từ URL
    # URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
    SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE'
    
    # Đọc một sheet cụ thể
    data = read_google_sheet(SPREADSHEET_ID, 'Sheet1')
    
    # Hoặc đọc tất cả sheets
    # all_data = get_all_sheets_data(SPREADSHEET_ID)
    
    # In ra một vài rows
    if data:
        print('\nDữ liệu mẫu:')
        for i, row in enumerate(data[:5]):
            print(f'Row {i+1}: {row}')
