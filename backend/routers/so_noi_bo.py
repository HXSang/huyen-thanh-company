import io
import urllib.parse
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from config import supabase
from dependencies import get_current_user
from schemas.don_hang import SORequest
from engine.so_noi_bo_exporter import build_excel, luu_supabase

router = APIRouter(prefix="/api/so-noi-bo", tags=["SO Nội Bộ"])


@router.post("/export-va-luu", summary="Xuất Excel + Lưu DB")
async def export_va_luu(
    payload:      SORequest,
    current_user: dict = Depends(get_current_user),
):
    if not payload.khach_hang.ten.strip():
        raise HTTPException(400, "Tên khách hàng không được để trống")
    if not payload.items:
        raise HTTPException(400, "Danh sách sản phẩm đang trống")

    # Lấy tên nhân viên để điền vào Excel
    try:
        nv = supabase.table("nhan_vien") \
                     .select("ho_ten") \
                     .eq("id", current_user["nhan_vien_id"]) \
                     .single() \
                     .execute()
        nguoi_lap = (nv.data or {}).get("ho_ten", "")
    except Exception:
        nguoi_lap = ""

    try:
        ma_dh = luu_supabase(payload, current_user)
    except Exception as e:
        print(f"🔥 LỖI SUPABASE TRẢ VỀ: {repr(e)}")
        raise HTTPException(500, f"Lỗi lưu DB: {e}")

    if payload.so_phieu in ("SO-....", ""):
        payload.so_phieu = ma_dh

    try:
        excel_bytes = build_excel(payload, nguoi_lap)
    except FileNotFoundError as e:
        raise HTTPException(500, f"Không tìm thấy template Excel: {e}")
    except Exception as e:
        raise HTTPException(500, f"Lỗi tạo Excel (đã lưu DB – mã: {ma_dh}): {e}")

    filename = f"SO_NoiBo_{payload.khach_hang.ten}_{ma_dh}.xlsx"
    encoded  = urllib.parse.quote(filename)
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded}",
            "X-Ma-Don-Hang": ma_dh,
        },
    )