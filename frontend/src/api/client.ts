import axios from "axios";

// 1. Khai báo và EXPORT biến BASE ra để dập lỗi 
export const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// 2. Gắn thẳng biến BASE vào cái axios config. Tiện tay export luôn cái API phòng hờ.
export const API = axios.create({
  baseURL: BASE,
  headers: { "Content-Type": "application/json" },
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export interface KhachHang {
  ten:     string;
  sdt:     string;
  dia_chi: string;
}

export interface Item {
  stt:             number;
  ten_hang:        string;
  dvt:             string;
  so_luong:        number;
  don_gia:         number;
  vat:             number;          
  ghi_chu:         string;

  gia_goc:         number;          
  ncc:             string;          
  phi_van_chuyen:  number;          
}

export interface QuoteData {
  khach_hang: KhachHang;
  items:      Item[];
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a   = document.createElement("a");
  a.href    = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export async function extractFile(file: File): Promise<QuoteData> {
  const form = new FormData();
  form.append("file", file);
  const res = await API.post<QuoteData>("/api/extract", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function saveQuoteData(data: QuoteData): Promise<void> {
  await API.post("/api/don-hang/luu-bao-gia", data);
}

export async function generatePdf(data: QuoteData): Promise<Blob> {
  const res = await API.post("/api/generate-pdf", data, {
    responseType: "blob",
  });
  return res.data;
}

export async function exportSoNoiBo(data: QuoteData): Promise<Blob> {
  const res = await API.post("/api/so-noi-bo/export-va-luu", data, {
    responseType: "blob",
  });
  return res.data;
}
