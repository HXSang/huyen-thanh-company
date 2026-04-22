import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Item, BASE } from "../api/client";

interface Props {
  value: string;
  onSelect: (itemData: Partial<Item>) => void;
  onChange: (val: string) => void;
}

export function ProductAutocomplete({ value, onSelect, onChange }: Props) {
  const [query, setQuery] = useState(value);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => { setQuery(value); }, [value]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (!wrapperRef.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const fetchProducts = async (searchTerm: string) => {
    if (!searchTerm.trim()) {
      setSuggestions([]);
      return;
    }
    
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const res = await axios.get(`${BASE}/api/san-pham/search?q=${searchTerm}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuggestions(res.data);
      setOpen(true);
    } catch (err) {
      console.error("Lỗi tìm sản phẩm:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (query !== value) {
        fetchProducts(query);
      }
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [query, value]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuery(e.target.value);
    onChange(e.target.value); 
  };

  const handleSelect = (prod: any) => {
    setQuery(prod.ten_san_pham);
    setOpen(false);
    onSelect({
      ten_hang: prod.ten_san_pham,
      dvt: prod.don_vi_tinh || "Cái",
      don_gia: prod.don_gia_ban || 0,
    });
  };

  return (
    <div className="unit-wrapper" ref={wrapperRef}>
      <textarea
        className="name-textarea"
        value={query}
        onChange={handleChange}
        onFocus={() => query.trim() && setOpen(true)}
        placeholder="Gõ tên sản phẩm..."
        rows={2}
      />
      
      {open && (suggestions.length > 0 || loading) && (
        <ul className="unit-dropdown" style={{ width: '300px', textAlign: 'left' }}>
          {loading ? (
            <li className="unit-option" style={{ color: '#888' }}>Đang tìm kiếm...</li>
          ) : (
            suggestions.map((prod) => (
              <li
                key={prod.id}
                className="unit-option"
                onMouseDown={() => handleSelect(prod)}
                style={{ borderBottom: '1px solid #eee' }}
              >
                <div style={{ fontWeight: 600, fontSize: '13px', color: '#111' }}>{prod.ten_san_pham}</div>
                <div style={{ fontSize: '11px', color: '#666', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Kho: {prod.ton_kho} {prod.don_vi_tinh}</span>
                  <span style={{ color: '#0055cc', fontWeight: 600 }}>{prod.don_gia_ban?.toLocaleString('vi-VN')} ₫</span>
                </div>
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
}