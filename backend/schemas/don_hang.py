from pydantic import BaseModel
from typing import List, Optional


class KhachHang(BaseModel):
    ten:          str = ""
    sdt:          str = ""
    dia_chi:      str = ""
    ngay_bao_gia: str = ""


class Item(BaseModel):
    stt:      int   = 1
    ten_hang: str   = ""
    dvt:      str   = "Cái"
    so_luong: float = 1
    don_gia:  float = 0
    vat:      float = 0.08
    ghi_chu:  str   = ""
    gia_goc:        float = 0
    ncc:            str   = ""
    phi_van_chuyen: float = 0


class QuoteRequest(BaseModel):
    khach_hang: KhachHang
    items:      List[Item]


class SORequest(BaseModel):
    so_phieu:   str       = "SO-...."
    khach_hang: KhachHang
    items:      List[Item]