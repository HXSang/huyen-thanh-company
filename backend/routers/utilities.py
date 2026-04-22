from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
import io
import urllib.parse
from engine.ai_extractor import extract_data_from_file
from engine.pdf_generator import generate_pdf
from engine.excel_raw_exporter import export_raw_excel
from engine.drive_service import upload_excel_to_drive # <--- Kéo hàm đẩy Drive vào
from schemas.don_hang import QuoteRequest
from dependencies import get_current_user 

router = APIRouter(tags=["Tiện ích"])

@router.post("/api/extract")
async def extract(file: UploadFile = File(...)):
    allowed = {"png", "jpg", "jpeg", "xlsx", "xls", "csv", "docx"}
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"File type .{ext} không được hỗ trợ")

    file_bytes = await file.read()
    result = extract_data_from_file(file_bytes, file.filename)

    if not result:
        raise HTTPException(422, "AI không đọc được file này")

    # Chuẩn hóa an toàn
    if "khach_hang" not in result:
        result["khach_hang"] = {"ten": "", "sdt": "", "dia_chi": ""}
    result["khach_hang"].setdefault("ten", "")
    result["khach_hang"].setdefault("sdt", "")
    result["khach_hang"].setdefault("dia_chi", "")
    
    if "items" not in result:
        result["items"] = []

    for item in result["items"]:
        item.setdefault("don_gia", 0)
        item.setdefault("vat", 0.08)
        item.setdefault("ghi_chu", "")
        item.setdefault("dvt", "Cái")

    return result

@router.post("/api/generate-pdf")
async def gen_pdf(
    payload: QuoteRequest, 
    background_tasks: BackgroundTasks, 
    current_user: dict = Depends(get_current_user)
):
    data = payload.model_dump()
    kh_ten = payload.khach_hang.ten or "KhachHang"
    pdf_bytes = generate_pdf(
        data,
        nhan_vien={
            "ten": current_user.get("ten", "Admin"), 
            "sdt": current_user.get("sdt", "0399836279")
        }
    )
    if 'ngay_bao_gia' not in data['khach_hang']:
         data['khach_hang']['ngay_bao_gia'] = ""
    excel_bytes = export_raw_excel(data)
    
    excel_filename = f"Backup_BaoGia_{kh_ten}.xlsx"
    
    folder_id = "ĐIỀN_ID_THƯ_MỤC_DRIVE_VÀO_ĐÂY" 
    
    background_tasks.add_task(upload_excel_to_drive, excel_bytes, excel_filename, folder_id)
    
    filename = f"BaoGia_{kh_ten}.pdf"
    encoded_filename = urllib.parse.quote(filename)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        },
    )

@router.post("/api/generate-excel")
async def gen_excel(payload: QuoteRequest, current_user: dict = Depends(get_current_user)):
    data = payload.model_dump()
    if 'ngay_bao_gia' not in data['khach_hang']:
         data['khach_hang']['ngay_bao_gia'] = ""
            
    excel_bytes = export_raw_excel(data)
    
    kh_ten = payload.khach_hang.ten or "KhachHang"
    filename = f"BaoGia_{kh_ten}.xlsx"
    encoded_filename = urllib.parse.quote(filename) 
    
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        },
    )