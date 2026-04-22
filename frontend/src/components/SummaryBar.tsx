import { Item } from "../api/client";

interface Props {
  items: Item[];
}

export default function SummaryBar({ items }: Props) {
  const tienHang = items.reduce((s, i) => s + i.so_luong * i.don_gia, 0);
  const tienVat  = items.reduce((s, i) => s + i.so_luong * i.don_gia * i.vat, 0);
  const total    = tienHang + tienVat;

  const fmt = (n: number) => n.toLocaleString("vi-VN") + " ₫";

  return (
    <div className="summary-bar">
      <div className="summary-item">
        <span className="label">Tổng tiền hàng</span>
        <span className="value">{fmt(tienHang)}</span>
      </div>
      <div className="summary-item">
        <span className="label">Tiền thuế VAT</span>
        <span className="value">{fmt(tienVat)}</span>
      </div>
      <div className="summary-item highlight">
        <span className="label">TỔNG THANH TOÁN</span>
        <span className="value">{fmt(total)}</span>
      </div>
    </div>
  );
}
