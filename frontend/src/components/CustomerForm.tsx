import { KhachHang } from "../api/client";

interface Props {
  value: KhachHang;
  onChange: (kh: KhachHang) => void;
}

export default function CustomerForm({ value, onChange }: Props) {
  const set = (field: keyof KhachHang) => (e: React.ChangeEvent<HTMLInputElement>) =>
    onChange({ ...value, [field]: e.target.value });

  return (
    <section className="customer-form">
      <h2>Thông tin khách hàng</h2>
      <div className="form-row">
        <label>
          <span>Tên khách hàng</span>
          <input value={value.ten} onChange={set("ten")} placeholder="Công ty TNHH..." />
        </label>
        <label>
          <span>Số điện thoại</span>
          <input value={value.sdt} onChange={set("sdt")} placeholder="0900 000 000" />
        </label>
        <label>
          <span>Địa chỉ</span>
          <input value={value.dia_chi} onChange={set("dia_chi")} placeholder="123 Nguyễn Văn A..." />
        </label>
      </div>
    </section>
  );
}
