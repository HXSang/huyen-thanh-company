import { Item } from "../api/client";
import { NumericInput } from "./NumericInput";
import { UnitInput } from "./UnitInput";
import { ProductAutocomplete } from "./ProductAutocomplete";

interface Props {
  items: Item[];
  onChange: (items: Item[]) => void;
}

const EMPTY_ITEM = (): Item => ({
  stt: 0, ten_hang: "", dvt: "Cái",
  so_luong: 1, don_gia: 0, vat: 0.08, ghi_chu: "",
});

export default function ItemsTable({ items, onChange }: Props) {
  const update = (idx: number, field: keyof Item, val: string | number) => {
    onChange(items.map((item, i) => i !== idx ? item : { ...item, [field]: val }));
  };

  const addRow = () => onChange([...items, EMPTY_ITEM()]);
  const removeRow = (idx: number) => onChange(items.filter((_, i) => i !== idx));

  return (
    <section className="items-section">
      <h2>Danh mục hàng hóa</h2>
      <div className="table-wrapper">
        <table className="items-table">
          <thead>
            <tr>
              <th className="col-stt">STT</th>
              <th className="col-name">Tên hàng / Quy cách</th>
              <th className="col-unit">ĐVT</th>
              <th className="col-qty">Số lượng</th>
              <th className="col-price">Đơn giá (₫)</th>
              <th className="col-amount">Thành tiền (₫)</th>
              <th className="col-vat">VAT</th>
              <th className="col-note">Ghi chú</th>
              <th className="col-del"></th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => {
              const thanh_tien = item.so_luong * item.don_gia;
              return (
                <tr key={idx}>
                  <td className="col-stt center">{idx + 1}</td>

                  <td className="col-name">
                  <ProductAutocomplete
                    value={item.ten_hang}
                    onChange={(val) => update(idx, "ten_hang", val)}
                    onSelect={(prodData) => {
                      const newItemList = [...items];
                      newItemList[idx] = { 
                        ...newItemList[idx], 
                        ten_hang: prodData.ten_hang!,
                        dvt: prodData.dvt!,
                        don_gia: prodData.don_gia!
                      };
                      onChange(newItemList);
                    }}
                  />
                </td>
                  <td className="col-unit">
                    <UnitInput
                      value={item.dvt}
                      onChange={val => update(idx, "dvt", val)}
                    />
                  </td>

                  <td className="col-qty">
                    <NumericInput
                      value={item.so_luong}
                      onChange={val => update(idx, "so_luong", val)}
                      min={0}
                    />
                  </td>

                  <td className="col-price">
                    <NumericInput
                      value={item.don_gia}
                      onChange={val => update(idx, "don_gia", val)}
                      min={0}
                      placeholder="0"
                    />
                  </td>

                  <td className="col-amount readonly">
                    {thanh_tien.toLocaleString("vi-VN")}
                  </td>

                  <td className="col-vat">
                    <select
                      value={item.vat}
                      onChange={e => update(idx, "vat", +e.target.value)}
                    >
                      <option value={0.08}>8%</option>
                      <option value={0.10}>10%</option>
                    </select>
                  </td>

                  <td className="col-note">
                    <input
                      value={item.ghi_chu}
                      onChange={e => update(idx, "ghi_chu", e.target.value)}
                    />
                  </td>

                  <td className="col-del">
                    <button
                      className="btn-del"
                      onClick={() => removeRow(idx)}
                      title="Xóa dòng"
                    >×</button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <button className="btn-add-row" onClick={addRow}>+ Thêm dòng</button>
    </section>
  );
}