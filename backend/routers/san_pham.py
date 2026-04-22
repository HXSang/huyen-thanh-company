from fastapi import APIRouter, Depends
from config import supabase
from dependencies import get_current_user

router = APIRouter(prefix="/api/san-pham", tags=["Sản Phẩm"])

@router.get("/search")
async def search_san_pham(q: str = "", limit: int = 10, current_user: dict = Depends(get_current_user)):
    if not q:
        return []
        
    res = supabase.table("san_pham").select("id, ma_san_pham, ten_san_pham, don_vi_tinh, don_gia_mac_dinh, hang_san_xuat") \
        .ilike("ten_san_pham", f"%{q}%") \
        .limit(limit) \
        .execute()
        
    return res.data