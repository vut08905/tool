function exportSheetToCSV() {
  // Lấy spreadsheet - phải mở từ bound script hoặc dùng openById
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  
  if (!spreadsheet) {
    // Nếu chạy standalone, cần ID của sheet
    Browser.msgBox('Lỗi: Vui lòng chạy script từ trong Google Sheet (Extensions → Apps Script)');
    return;
  }
  
  var sheet = spreadsheet.getActiveSheet();
  
  // Lấy tất cả dữ liệu
  var range = sheet.getDataRange();
  var values = range.getValues();
  
  // Chuyển thành CSV
  var csv = '';
  for (var i = 0; i < values.length; i++) {
    var row = values[i];
    for (var j = 0; j < row.length; j++) {
      if (j > 0) csv += ',';
      // Escape dấu ngoặc kép
      var cell = String(row[j]).replace(/"/g, '""');
      if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) {
        csv += '"' + cell + '"';
      } else {
        csv += cell;
      }
    }
    csv += '\n';
  }
  
  // Lưu vào Google Drive
  var fileName = sheet.getName() + '_export_' + new Date().getTime() + '.csv';
  var file = DriveApp.createFile(fileName, csv, MimeType.CSV);
  
  // Hiển thị link
  var url = file.getUrl();
  
  try {
    SpreadsheetApp.getUi().alert(
      'Export thành công!\n\n' +
      'File: ' + fileName + '\n' +
      'Rows: ' + values.length + '\n\n' +
      'Link: ' + url + '\n\n' +
      'Vào Google Drive để download!'
    );
  } catch(e) {
    // Nếu không có UI, chỉ log
    Logger.log('Export thành công!');
    Logger.log('File: ' + fileName);
    Logger.log('Rows: ' + values.length);
    Logger.log('Link: ' + url);
  }
  
  Logger.log('Export thành công: ' + url);
  
  return url;
}

function exportSheetToJSON() {
  // Lấy spreadsheet
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  
  if (!spreadsheet) {
    Browser.msgBox('Lỗi: Vui lòng chạy script từ trong Google Sheet (Extensions → Apps Script)');
    return;
  }
  
  var sheet = spreadsheet.getActiveSheet();
  var data = sheet.getDataRange().getValues();
  
  // Chuyển thành JSON
  var headers = data[0];
  var jsonArray = [];
  
  for (var i = 1; i < data.length; i++) {
    var row = {};
    for (var j = 0; j < headers.length; j++) {
      row[headers[j]] = data[i][j];
    }
    jsonArray.push(row);
  }
  
  var json = JSON.stringify(jsonArray, null, 2);
  
  // Lưu vào Google Drive
  var fileName = sheet.getName() + '_export_' + new Date().getTime() + '.json';
  var file = DriveApp.createFile(fileName, json, MimeType.PLAIN_TEXT);
  
  // Hiển thị link
  var url = file.getUrl();
  
  try {
    SpreadsheetApp.getUi().alert(
      'Export JSON thành công!\n\n' +
      'File: ' + fileName + '\n' +
      'Records: ' + jsonArray.length + '\n\n' +
      'Link: ' + url
    );
  } catch(e) {
    Logger.log('Export JSON thành công!');
    Logger.log('File: ' + fileName);
    Logger.log('Records: ' + jsonArray.length);
    Logger.log('Link: ' + url);
  }
  
  Logger.log('Export JSON: ' + url);
  
  return url;
}

function onOpen() {
  // Thêm menu vào Google Sheets
  SpreadsheetApp.getUi()
    .createMenu('📥 Export Data')
    .addItem('Export to CSV', 'exportSheetToCSV')
    .addItem('Export to JSON', 'exportSheetToJSON')
    .addToUi();
}
