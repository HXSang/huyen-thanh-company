from fastapi import APIRouter, Depends, HTTPException
from config import supabase
from dependencies import get_current_user
from schemas.don_hang import QuoteRequest
from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException
import re

COMMON_BRANDS = [
    # --- 1. Truyền động (Dây curoa, Băng tải) ---
    "mitsuboshi", "bando", "optibelt", "gates", "megadyne", "habasit",
    
    # --- 2. Cơ khí & Vòng bi (Bạc đạn) ---
    "skf", "nsk", "ntn", "koyo", "fag", "timken", "thk", "ina", "hiwin",
    
    # --- 3. Điện dân dụng & Công nghiệp ---
    "panasonic", "sino", "cadivi", "daphaco", "schneider", "ls", 
    "mitsubishi", "abb", "omron", "autonics", "idec", "fuji", "yaskawa",
    
    # --- 4. Dụng cụ cầm tay & Thiết bị hàn ---
    "makita", "bosch", "dewalt", "milwaukee", "stanley", "total", "ingco", 
    "jasic", "weldcom", "hong ky",
    
    # --- 5. Khí nén & Thủy lực ---
    "smc", "festo", "airtac", "yuken", "rexroth", "parker",
    
    # --- 6. Bơm, Van & Ống nước ---
    "ebara", "pentax", "grundfos", "kitz", "minh hoa", 
    "binh minh", "tien phong", "hoa sen", "dec",
    
    # --- 7. Sắt thép & Kim khí tổng hợp ---
    "hoa phat", "nam kim", "dong a", "vinaone", "pomina"
]

def extract_brand(product_name: str) -> str | None:
    name_lower = product_name.lower()
    for brand in COMMON_BRANDS:
        if re.search(rf'\b{brand}\b', name_lower):
            return brand.capitalize()
    return None

router = APIRouter(prefix="/api/don-hang", tags=["Đơn Hàng & Báo Giá"])

@router.post("/luu-bao-gia")
async def luu_bao_gia(payload: QuoteRequest, current_user: dict = Depends(get_current_user)):
    kh_ten = payload.khach_hang.ten.strip()
    if not kh_ten:
        raise HTTPException(400, "Tên khách hàng không được để trống")

    kh_res = supabase.table("khach_hang").select("id").eq("ten_cong_ty", kh_ten).execute()
    
    if kh_res.data:
        khach_hang_id = kh_res.data[0]["id"]
    else:
        new_kh = supabase.table("khach_hang").insert({
            "ten_cong_ty": kh_ten,
            "sdt": payload.khach_hang.sdt,
            "dia_chi": payload.khach_hang.dia_chi,
            "created_by": current_user["nhan_vien_id"]
        }).execute()
        khach_hang_id = new_kh.data[0]["id"]

    ma_dh = f"BG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    new_dh = supabase.table("don_hang").insert({
        "ma_don_hang": ma_dh,
        "khach_hang_id": khach_hang_id,
        "nhan_vien_id": current_user["nhan_vien_id"],
        "trang_thai": "Báo giá"
    }).execute()
    
    don_hang_id = new_dh.data[0]["id"]

    chi_tiet_list = []
    for item in payload.items:
        if not item.ten_hang.strip():
            continue 

        sp_res = supabase.table("san_pham").select("id").eq("ten_san_pham", item.ten_hang.strip()).execute()
        
        if not sp_res.data:
            hang = extract_brand(item.ten_hang.strip())

            supabase.table("san_pham").insert({
                "ten_san_pham": item.ten_hang.strip(),
                "don_vi_tinh": item.dvt,
                "don_gia_mac_dinh": int(float(item.don_gia)),
                "ma_san_pham": f"SP-AUTO-{uuid.uuid4().hex[:6].upper()}",
                "hang_san_xuat": hang 
            }).execute()

        chi_tiet_list.append({
            "don_hang_id": don_hang_id,
            "ten_san_pham_luc_ban": item.ten_hang,
            "don_vi_tinh": item.dvt,
            "so_luong": int(float(item.so_luong)),
            "don_gia_luc_ban": int(float(item.don_gia)),
            "vat": float(item.vat),
            "ghi_chu": item.ghi_chu or ""
        })

    if chi_tiet_list:
        supabase.table("chi_tiet_don_hang").insert(chi_tiet_list).execute()

    return {
        "message": "Lưu báo giá thành công", 
        "ma_don_hang": ma_dh
    }