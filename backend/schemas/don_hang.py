from pydantic import BaseModel
from typing import List, Optional

class KhachHang(BaseModel):
    ten: str = ""
    sdt: str = ""
    dia_chi: str = ""
    ngay_bao_gia: str = ""  

class Item(BaseModel):
    stt: int = 1
    ten_hang: str = ""
    dvt: str = "Cái"
    so_luong: float = 1
    don_gia: float = 0
    vat: float = 0.08
    ghi_chu: str = ""

class QuoteRequest(BaseModel):
    khach_hang: KhachHang
    items: List[Item]