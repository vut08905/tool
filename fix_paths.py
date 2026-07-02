import os

def fix_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # GUI text box path
    content = content.replace("self.excel_path_entry.insert(0, 'lophoc.xlsx')", "self.excel_path_entry.insert(0, os.path.join(application_path, 'lophoc.xlsx'))")
    
    # Static fallbacks
    content = content.replace("excel_file = \"lophoc.xlsx\"", "excel_file = os.path.join(application_path, \"lophoc.xlsx\")")
    
    # Dictionary fallback for Excel file
    content = content.replace("config_data.get('excel_file_path', 'lophoc.xlsx')", "config_data.get('excel_file_path', os.path.join(application_path, 'lophoc.xlsx'))")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

fix_file("d:/webtruong4.1/final/complete_gui.py")
fix_file("d:/webtruong4.1/complete_gui.py")
print("Fixed!")
