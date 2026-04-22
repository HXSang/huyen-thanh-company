export const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
import axios from "axios";

export interface KhachHang {
  ten: string;
  sdt: string;
  dia_chi: string;
}

export interface Item {
  stt: number;
  ten_hang: string;
  dvt: string;
  so_luong: number;
  don_gia: number;
  vat: number;         // 0.08 | 0.10
  ghi_chu: string;
}

export interface QuoteData {
  khach_hang: KhachHang;
  items: Item[];
}

// ─── Extract từ file ───────────────────────────────────────
export async function extractFile(file: File): Promise<QuoteData> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${BASE}/api/extract`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "Không đọc được file");
  }
  return res.json();
}

// ─── Xuất PDF ──────────────────────────────────────────────
export async function generatePdf(data: QuoteData): Promise<Blob> {
  const token = localStorage.getItem("token");
  if (!token) throw new Error("Chưa đăng nhập hoặc mất token!");

  const res = await fetch(`${BASE}/api/generate-pdf`, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(data),
  });
  return res.blob();
}

// ─── Helper: download blob ──────────────────────────────────
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
export const saveQuoteData = async (data: QuoteData) => {
  const token = localStorage.getItem("token");
  if (!token) throw new Error("Chưa đăng nhập! Thẻ ra vào không hợp lệ.");
  const res = await axios.post(`${BASE}/api/don-hang/luu-bao-gia`, data, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data;
};

