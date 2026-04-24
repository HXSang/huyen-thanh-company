/**
 * frontend/src/components/ItemsTable.tsx
 * ─────────────────────────────────────────────────────────────
 * Bảng nhập liệu sản phẩm.
 *
 * Cột hiển thị:
 *   STT | Tên hàng | ĐVT | Số lượng | Đơn giá | Thành tiền | VAT | Ghi chú
 *   ── nội bộ (màu nền khác) ──
 *   Giá gốc | NCC | Phí VC | (xóa)
 */

import { useRef, useState } from "react";
import { Item } from "../api/client";
import { NumericInput } from "./NumericInput";

// ── Danh sách ĐVT gợi ý ─────────────────────────────────────
const UNIT_LIST = [
  "Cái","Bộ","Chiếc","Cặp","Cuộn","Mét","MD","Kg","Lít",
  "Hộp","Thùng","Bao","Tấm","Thanh","Ống","Lô","Đôi",
];

// ── Định dạng số có dấu phân cách hàng nghìn ────────────────
const fmt = (n: number) =>
  n === 0 ? "0" : n.toLocaleString("vi-VN");

// ════════════════════════════════════════════════════════════

interface Props {
  items:    Item[];
  onChange: (items: Item[]) => void;
}

export default function ItemsTable({ items, onChange }: Props) {
  // index của dropdown ĐVT đang mở (-1 = không mở)
  const [openUnit, setOpenUnit] = useState<number>(-1);
  const unitRefs  = useRef<(HTMLDivElement | null)[]>([]);

  // ── Helpers cập nhật field ─────────────────────────────────
  const update = <K extends keyof Item>(
    idx: number,
    field: K,
    value: Item[K]
  ) => {
    const next = items.map((it, i) => (i === idx ? { ...it, [field]: value } : it));
    onChange(next);
  };

  const addRow = () =>
    onChange([
      ...items,
      {
        stt:            items.length + 1,
        ten_hang:       "",
        dvt:            "Cái",
        so_luong:       1,
        don_gia:        0,
        vat:            0.08,
        ghi_chu:        "",
        gia_goc:        0,
        ncc:            "",
        phi_van_chuyen: 0,
      },
    ]);

  const removeRow = (idx: number) =>
    onChange(items.filter((_, i) => i !== idx).map((it, i) => ({ ...it, stt: i + 1 })));

  // ── Auto-resize textarea ───────────────────────────────────
  const autoResize = (el: HTMLTextAreaElement) => {
    el.style.height = "auto";
    el.style.height = el.scrollHeight + "px";
  };

  return (
    <section>
      <h2>Danh mục hàng hóa</h2>
      <div className="table-wrapper">
        <table className="items-table">
          <thead>
            <tr>
              {/* ── Cột thông thường ── */}
              <th className="col-stt">STT</th>
              <th className="col-name">Tên hàng / Quy cách</th>
              <th className="col-unit">ĐVT</th>
              <th className="col-qty">Số lượng</th>
              <th className="col-price">Đơn giá (đ)</th>
              <th className="col-amount">Thành tiền (đ)</th>
              <th className="col-vat">VAT</th>
              <th className="col-note">Ghi chú</th>
              {/* ── Cột nội bộ (nền khác) ── */}
              <th className="col-gia-goc">Giá gốc (đ)</th>
              <th className="col-ncc   ">NCC</th>
              <th className="col-phi-vc">Phí VC (đ)</th>
              <th className="col-del"></th>
            </tr>
          </thead>

          <tbody>
            {items.map((item, idx) => {
              const thanhTien = item.so_luong * item.don_gia;
              const vatPct    = item.vat === 0.10 ? "10%" : "8%";

              return (
                <tr key={idx}>
                  {/* STT */}
                  <td className="readonly center">{item.stt}</td>

                  {/* Tên hàng */}
                  <td className="col-name">
                    <textarea
                      className="name-textarea"
                      value={item.ten_hang}
                      placeholder="Gõ tên sản phẩm..."
                      rows={1}
                      onChange={(e) => {
                        update(idx, "ten_hang", e.target.value);
                        autoResize(e.target);
                      }}
                      onFocus={(e) => autoResize(e.target)}
                    />
                  </td>

                  {/* ĐVT – combobox */}
                  <td className="col-unit">
                    <div
                      className="unit-wrapper"
                      ref={(el) => { unitRefs.current[idx] = el; }}
                    >
                      <input
                        className="unit-input"
                        value={item.dvt}
                        onChange={(e) => update(idx, "dvt", e.target.value)}
                        onFocus={() => setOpenUnit(idx)}
                        onBlur={() => setTimeout(() => setOpenUnit(-1), 150)}
                      />
                      {openUnit === idx && (
                        <ul className="unit-dropdown">
                          {UNIT_LIST.filter((u) =>
                            u.toLowerCase().startsWith(item.dvt.toLowerCase())
                          ).map((u) => (
                            <li
                              key={u}
                              className={`unit-option ${u === item.dvt ? "active" : ""}`}
                              onMouseDown={() => {
                                update(idx, "dvt", u);
                                setOpenUnit(-1);
                              }}
                            >
                              {u}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </td>

                  {/* Số lượng */}
                  <td>
                    <NumericInput
                      value={item.so_luong}
                      onChange={(val) => update(idx, "so_luong", val)}
                    />
                  </td>

                  {/* Đơn giá */}
                  <td>
                    <NumericInput
                      value={item.don_gia}
                      onChange={(val) => update(idx, "don_gia", val)}
                      placeholder="0"
                    />
                  </td>

                  {/* Thành tiền – readonly */}
                  <td className="readonly">{fmt(thanhTien)}</td>

                  {/* VAT */}
                  <td className="center">
                    <select
                      value={vatPct}
                      onChange={(e) =>
                        update(idx, "vat", e.target.value === "10%" ? 0.10 : 0.08)
                      }
                    >
                      <option value="8%">8%</option>
                      <option value="10%">10%</option>
                    </select>
                  </td>

                  {/* Ghi chú */}
                  <td>
                    <input
                      type="text"
                      value={item.ghi_chu}
                      onChange={(e) => update(idx, "ghi_chu", e.target.value)}
                    />
                  </td>

                  {/* ── Cột nội bộ ─────────────────────────── */}

                  {/* Giá gốc */}
                  <td>
                    <NumericInput
                      value={item.gia_goc}
                      onChange={(val) => update(idx, "gia_goc", val)}
                      placeholder="0"
                    />
                  </td>

                  {/* NCC */}
                  <td>
                    <input
                      type="text"
                      value={item.ncc}
                      placeholder="Nhà cung cấp..."
                      onChange={(e) => update(idx, "ncc", e.target.value)}
                    />
                  </td>

                  {/* Phí vận chuyển */}
                  <td>
                    <NumericInput
                      value={item.phi_van_chuyen}
                      onChange={(val) => update(idx, "phi_van_chuyen", val)}
                      placeholder="0"
                    />
                  </td>

                  {/* Xóa dòng */}
                  <td className="center">
                    <button
                      className="btn-del"
                      onClick={() => removeRow(idx)}
                      title="Xóa dòng"
                    >
                      ×
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <button className="btn-add-row" onClick={addRow}>
        + Thêm dòng
      </button>
    </section>
  );
}