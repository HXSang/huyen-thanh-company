import io
from datetime import datetime

import xlsxwriter

from config import supabase
from schemas.don_hang import Item, SORequest


# ── Tính toán ─────────────────────────────────────────────────

def tinh_toan(items: list[Item]) -> tuple[list[dict], dict]:
    rows = []
    tong_thanh_tien = tong_gia_goc = tong_phi_vc = 0.0
    tong_vat_8 = tong_vat_10 = 0.0

    for item in items:
        thanh_tien = item.don_gia * item.so_luong
        chi_phi    = (item.gia_goc * item.so_luong) + item.phi_van_chuyen
        loi_nhuan  = thanh_tien - chi_phi

        if item.vat >= 0.10:
            tong_vat_10 += thanh_tien * item.vat
        else:
            tong_vat_8  += thanh_tien * item.vat

        rows.append({**item.model_dump(),
                     "thanh_tien": thanh_tien,
                     "loi_nhuan":  loi_nhuan})

        tong_thanh_tien += thanh_tien
        tong_gia_goc    += item.gia_goc * item.so_luong
        tong_phi_vc     += item.phi_van_chuyen

    tong_vat = tong_vat_8 + tong_vat_10
    totals = {
        "tong_thanh_tien": tong_thanh_tien,
        "vat_10":          tong_vat_10,
        "vat_8":           tong_vat_8,
        "tong_loi_nhuan":  tong_thanh_tien - (tong_gia_goc + tong_phi_vc),
        "tong_thanh_toan": tong_thanh_tien + tong_vat,
    }
    return rows, totals


# ── Build Excel ────────────────────────────────────────────────
#
# Cột (0-based):
#   0=STT | 1=Tên hàng | 2=DVT | 3=Số lượng | 4=Đơn giá
#   5=Thành tiền | 6=VAT | 7=Giá gốc | 8=NCC | 9=Phí vận chuyển
#
# Layout rows (0-based):
#   0   : "SO NỘI BỘ"  (merge A:J)
#   1   : "SO: HT-..." (merge D:F, đỏ, border)
#   2   : blank
#   3   : Kính gửi
#   4   : Điện thoại
#   5   : Địa chỉ
#   6   : Header bảng (xanh)
#   7…  : Data rows
#   7+n : TỔNG CỘNG
#   7+n+1: VAT 10%
#   7+n+2: VAT 8%
#   7+n+3: TỔNG THANH TOÁN (xanh)
#   7+n+4: blank
#   7+n+5: blank
#   7+n+6: "Người lập báo giá" (cột G:J)
#   7+n+7: tên người lập (đỏ)
#   7+n+8: ô ký tên (border)

BLUE = "#1F6FBF"
WHITE = "#FFFFFF"
FONT = "Times New Roman"

COL_WIDTHS = [5, 40, 8, 9, 14, 16, 7, 14, 22, 14]  # 10 cột A-J


def build_excel(payload: SORequest, nguoi_lap: str = "") -> bytes:
    rows, totals = tinh_toan(payload.items)
    n   = len(rows)
    now = datetime.now()

    buf = io.BytesIO()
    wb  = xlsxwriter.Workbook(buf, {"in_memory": True})
    ws  = wb.add_worksheet()

    def fmt(**kw):
        return wb.add_format({"font_name": FONT, "font_size": 11, **kw})

    f_title    = fmt(bold=True, font_size=16, align="center", valign="vcenter")
    f_so       = fmt(bold=True, align="center", valign="vcenter",
                     font_color="red", border=1)
    f_label    = fmt(valign="vcenter")
    f_bold_lbl = fmt(bold=True, valign="vcenter")
    f_hdr      = fmt(bold=True, align="center", valign="vcenter",
                     bg_color=BLUE, font_color=WHITE, border=1, text_wrap=True)
    f_data     = fmt(border=1, valign="vcenter")
    f_data_c   = fmt(border=1, align="center", valign="vcenter")
    f_money    = fmt(border=1, align="right", valign="vcenter", num_format="#,##0")
    f_ft_lbl   = fmt(bold=True, align="center", valign="vcenter", border=1)
    f_ft_val   = fmt(bold=True, align="right",  valign="vcenter", border=1,
                     num_format="#,##0")
    f_ft_empty = fmt(border=1)
    f_tt_lbl   = fmt(bold=True, align="center", valign="vcenter", border=1,
                     bg_color=BLUE, font_color=WHITE)
    f_tt_val   = fmt(bold=True, align="right",  valign="vcenter", border=1,
                     bg_color=BLUE, font_color=WHITE, num_format="#,##0")
    f_tt_empty = fmt(border=1, bg_color=BLUE)
    f_sign_lbl  = fmt(align="center", valign="vcenter")
    f_sign_name = fmt(bold=True, align="center", valign="vcenter", font_color="red")
    f_sign_box  = fmt(border=1)

    for i, w in enumerate(COL_WIDTHS):
        ws.set_column(i, i, w)

    # Row 0: SO NỘI BỘ
    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, 9, "SO NỘI BỘ", f_title)

    # Row 1: Số phiếu — merge D:F (cột 3-5)
    ws.set_row(1, 20)
    ws.merge_range(1, 3, 1, 5, f"SO: {payload.so_phieu}", f_so)

    # Row 2: blank
    ws.set_row(2, 8)

    # Row 3-5: Khách hàng
    ws.set_row(3, 18); ws.set_row(4, 18); ws.set_row(5, 18)
    ws.merge_range(3, 0, 3, 9, f"Kính gửi: {payload.khach_hang.ten}", f_bold_lbl)
    ws.merge_range(4, 0, 4, 9, f"Điện thoại: {payload.khach_hang.sdt}", f_label)
    ws.merge_range(5, 0, 5, 9, f"Địa chỉ: {payload.khach_hang.dia_chi}", f_label)

    # Row 6: Header
    ws.set_row(6, 34)
    for c, h in enumerate([
        "STT", "Tên hàng", "DVT", "Số lượng",
        "Đơn giá", "Thành tiền", "VAT", "Giá gốc", "NCC", "Phí vận\nchuyển",
    ]):
        ws.write(6, c, h, f_hdr)

    # Row 7+: Data
    for idx, row in enumerate(rows):
        r = 7 + idx
        ws.set_row(r, 22)
        ws.write(r, 0, row["stt"],                      f_data_c)
        ws.write(r, 1, row["ten_hang"],                 f_data)
        ws.write(r, 2, row["dvt"],                      f_data_c)
        ws.write(r, 3, row["so_luong"],                 f_data_c)
        ws.write(r, 4, row["don_gia"],                  f_money)
        ws.write(r, 5, row["thanh_tien"],               f_money)
        ws.write(r, 6, f'{int(row["vat"] * 100)}%',    f_data_c)
        ws.write(r, 7, row["gia_goc"],                  f_money)
        ws.write(r, 8, row["ncc"],                      f_data)
        ws.write(r, 9, row["phi_van_chuyen"],           f_money)

    # Footer
    rf = 7 + n

    def write_footer(r, label, value, lf, vf, ef):
        ws.set_row(r, 22)
        ws.merge_range(r, 0, r, 4, label, lf)
        ws.write(r, 5, value, vf)
        for c in range(6, 10):
            ws.write_blank(r, c, None, ef)

    write_footer(rf,     "TỔNG CỘNG",      totals["tong_thanh_tien"], f_ft_lbl, f_ft_val, f_ft_empty)
    write_footer(rf + 1, "VAT 10%",         totals["vat_10"],          f_ft_lbl, f_ft_val, f_ft_empty)
    write_footer(rf + 2, "VAT 8%",          totals["vat_8"],           f_ft_lbl, f_ft_val, f_ft_empty)
    write_footer(rf + 3, "TỔNG THANH TOÁN", totals["tong_thanh_toan"], f_tt_lbl, f_tt_val, f_tt_empty)

    # Blank
    ws.set_row(rf + 4, 14)
    ws.set_row(rf + 5, 14)

    # Ngày + Ký tên
    r_date = rf + 6
    r_sign = rf + 7
    ws.set_row(r_date,     18)
    ws.set_row(r_sign,     18)
    ws.set_row(r_sign + 1, 18)
    ws.set_row(r_sign + 2, 30)

    f_date = fmt(italic=True, align="center", valign="vcenter")

    ws.merge_range(r_date, 6, r_date, 9,
                   f"TP.HCM, Ngày {now.day} Tháng {now.month} Năm {now.year}",
                   f_date)

    ws.merge_range(r_sign,     6, r_sign,     9, "Người lập báo giá", f_sign_lbl)
    ws.merge_range(r_sign + 1, 6, r_sign + 1, 9, nguoi_lap,           f_sign_name)
    ws.merge_range(r_sign + 2, 6, r_sign + 2, 9, "",                  f_sign_box)

    wb.close()
    return buf.getvalue()


# ── Lưu Supabase ──────────────────────────────────────────────

def luu_supabase(payload: SORequest, current_user: dict) -> str:
    kh_ten = payload.khach_hang.ten.strip()

    kh = supabase.table("khach_hang").select("id").eq("ten_cong_ty", kh_ten).execute()
    if kh.data:
        kh_id = kh.data[0]["id"]
    else:
        kh_id = supabase.table("khach_hang").insert({
            "ten_cong_ty": kh_ten,
            "sdt":         payload.khach_hang.sdt,
            "dia_chi":     payload.khach_hang.dia_chi,
            "created_by":  current_user["nhan_vien_id"],
        }).execute().data[0]["id"]

    ma_dh = f"SO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    dh_id = supabase.table("don_hang").insert({
        "ma_don_hang":   ma_dh,
        "khach_hang_id": kh_id,
        "nhan_vien_id":  current_user["nhan_vien_id"],
        "trang_thai":    "Báo giá",
    }).execute().data[0]["id"]

    chi_tiet = [
        {
            "don_hang_id":          dh_id,
            "ten_san_pham_luc_ban": it.ten_hang,
            "don_vi_tinh":          it.dvt,
            "so_luong":             int(it.so_luong),
            "don_gia_luc_ban":      int(it.don_gia),
            "vat":                  it.vat,
            "gia_goc":              int(it.gia_goc),
            "nha_cung_cap":         it.ncc,
            "phi_van_chuyen":       int(it.phi_van_chuyen),
            "ghi_chu":              it.ghi_chu or "",
        }
        for it in payload.items if it.ten_hang.strip()
    ]
    if chi_tiet:
        supabase.table("chi_tiet_don_hang").insert(chi_tiet).execute()

    return ma_dh