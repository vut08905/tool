// Paste code này vào Google Apps Script Editor
// Tools > Script editor trong Google Sheets

function exportSheetData() {
  // Lấy spreadsheet hiện tại
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getActiveSheet();
  
  // Lấy tất cả dữ liệu
  var range = sheet.getDataRange();
  var values = range.getValues();
  
  // Chuyển sang JSON
  var jsonData = JSON.stringify(values);
  
  // Log ra để copy
  Logger.log(jsonData);
  
  // Hoặc gửi qua email
  // MailApp.sendEmail("your-email@gmail.com", "Sheet Data", jsonData);
  
  // Hoặc lưu vào Google Drive
  var fileName = sheet.getName() + '_data.json';
  DriveApp.createFile(fileName, jsonData);
  
  Logger.log('Data exported successfully!');
}

// Chạy function này
