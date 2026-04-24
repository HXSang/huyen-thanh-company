import { useState } from "react";
import { useNavigate } from "react-router-dom"; 
import CustomerForm from "../components/CustomerForm";
import ItemsTable from "../components/ItemsTable";
import SummaryBar from "../components/SummaryBar";
import UploadPanel from "../components/UploadPanel";
import { KhachHang, Item, QuoteData, generatePdf, exportSoNoiBo, downloadBlob, saveQuoteData } from "../api/client";
import "../App.css"; 

const EMPTY_KH: KhachHang = { ten: "", sdt: "", dia_chi: "" };
const EMPTY_ITEM: Item = {
  stt: 1, ten_hang: "", dvt: "Cái",
  so_luong: 1, don_gia: 0, vat: 0.08, ghi_chu: "",
  // Trường nội bộ – mặc định rỗng
  gia_goc: 0, ncc: "", phi_van_chuyen: 0,
};

export default function DashboardPage() {
  const [khachHang, setKhachHang] = useState<KhachHang>(EMPTY_KH);
  const [items, setItems] = useState<Item[]>([EMPTY_ITEM]);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [soLoading, setSoLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleAiResult = (data: QuoteData) => {
    setKhachHang(data.khach_hang);
    setItems(data.items.length > 0 ? data.items : [EMPTY_ITEM]);
  };

  const handleExportPdf = async () => {
    if (!khachHang.ten.trim()) {
      alert("Tên khách hàng đang trống, điền vào đã ông ơi!");
      return;
    }

    setPdfLoading(true);
    try {
      const finalItems = items.map((it, i) => ({ ...it, stt: i + 1 }));
      const payload = { khach_hang: khachHang, items: finalItems };

      await saveQuoteData(payload);

      const blob = await generatePdf(payload);
      downloadBlob(blob, `BaoGia_${khachHang.ten}.pdf`);

    } catch (e: any) {
      const errorMsg = e.response?.data?.detail || e.message;
      alert("Lỗi hệ thống: " + errorMsg);
    } finally {
      setPdfLoading(false);
    }
    };

  const handleExportSO = async () => {
    if (!khachHang.ten.trim()) {
      alert("Tên khách hàng đang trống, điền vào đã ông ơi!");
      return;
    }
    setSoLoading(true);
    try {
      const finalItems = items.map((it, i) => ({ ...it, stt: i + 1 }));
      const payload: QuoteData = { khach_hang: khachHang, items: finalItems };
      const blob = await exportSoNoiBo(payload);
      downloadBlob(blob, `SO_NoiBo_${khachHang.ten}.xlsx`);
    } catch (e: any) {
      const errorMsg = e.response?.data?.detail || e.message;
      alert("Lỗi hệ thống: " + errorMsg);
    } finally {
      setSoLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token'); 
    navigate('/login'); 
  };

  return (
    <div className="layout">
      <UploadPanel onResult={handleAiResult} />

      <main className="main-content">
        <header className="app-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>Hệ Thống Báo Giá <span>Huyền Thanh</span></h1>

          <button 
            onClick={handleLogout}
            style={{
              padding: '6px 14px',
              background: 'transparent',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              color: '#4b5563',
              fontSize: '13px',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.color = '#ef4444';
              e.currentTarget.style.borderColor = '#fca5a5';
              e.currentTarget.style.background = '#fef2f2';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.color = '#4b5563';
              e.currentTarget.style.borderColor = '#d1d5db';
              e.currentTarget.style.background = 'transparent';
            }}
          >
            Đăng xuất
          </button>
        </header>

        <CustomerForm value={khachHang} onChange={setKhachHang} />
        <ItemsTable items={items} onChange={setItems} />

        <div className="sticky-action-bar">
          <div className="sticky-summary">
            <SummaryBar items={items} />
          </div>

          <div className="action-buttons">
            <button
              className="btn-export-so"
              onClick={handleExportSO}
              disabled={soLoading}
            >
              {soLoading ? "Đang xử lý..." : "📋 Xuất SO Nội Bộ"}
            </button>

            <button
              className="btn-export"
              onClick={handleExportPdf}
              disabled={pdfLoading}
            >
              {pdfLoading ? "Đang tạo PDF..." : "🖨️ Xuất báo giá PDF"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}