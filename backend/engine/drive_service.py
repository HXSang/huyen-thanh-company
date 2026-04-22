from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

def upload_excel_to_drive(file_bytes: bytes, filename: str, folder_id: str):
    """
    Hàm đẩy file Excel dạng bytes thẳng lên Google Drive
    """
    try:
        # Xác thực bằng Service Account
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        service = build('drive', 'v3', credentials=creds)

        # Cấu hình tên file và chỉ định thư mục đích
        file_metadata = {
            'name': filename,
            'parents': [folder_id] 
        }
        
        # Đóng gói file bytes thành định dạng mà Google Drive hiểu
        media = MediaIoBaseUpload(
            io.BytesIO(file_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=True
        )
        
        # Bấm nút phóng!
        file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id'
        ).execute()
        
        print(f"Đã backup thành công lên Drive: {filename} (ID: {file.get('id')})")
        return file.get('id')
        
    except Exception as e:
        print(f"Lỗi khi đẩy lên Drive: {e}")
        return None