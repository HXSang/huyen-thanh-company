from fastapi import APIRouter, Depends
from config import supabase
from dependencies import get_current_user

router = APIRouter(prefix="/api/khach-hang", tags=["Khách Hàng"])

@router.get("/search")
async def search_khach_hang(q: str = "", limit: int = 5, current_user: dict = Depends(get_current_user)):
    if not q:
        return []
        
    res = supabase.table("khach_hang").select("id, ten_cong_ty, nguoi_dai_dien, sdt, dia_chi") \
        .ilike("ten_cong_ty", f"%{q}%") \
        .limit(limit) \
        .execute()
        
    return res.data