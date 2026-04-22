import { useState, useRef, useEffect } from "react";

// ── Danh sách đơn vị tính công nghiệp ──────────────────────────────
const UNIT_LIST: { label: string; keywords: string[] }[] = [
  // Số lượng / Rời
  { label: "Cái",    keywords: ["c", "cai"] },
  { label: "Chiếc",  keywords: ["c", "chiec"] },
  { label: "Bộ",     keywords: ["b", "bo"] },
  { label: "Đôi",    keywords: ["d", "doi"] },
  { label: "Viên",   keywords: ["v", "vien"] },
  // Chiều dài
  { label: "Mét",    keywords: ["m", "met"] },
  { label: "mm",     keywords: ["m", "mm"] },
  { label: "cm",     keywords: ["c", "cm"] },
  // Diện tích / Thể tích
  { label: "m²",     keywords: ["m", "m2"] },
  { label: "m³",     keywords: ["m", "m3"] },
  // Khối lượng
  { label: "Kg",     keywords: ["k", "kg"] },
  { label: "Gram",   keywords: ["g", "gr", "gram"] },
  { label: "Tấn",    keywords: ["t", "tan"] },
  // Thể tích lỏng
  { label: "Lít",    keywords: ["l", "lit"] },
  { label: "ml",     keywords: ["m", "ml"] },
  // Dạng cuộn / tấm / thanh / ống
  { label: "Cuộn",   keywords: ["c", "cuon"] },
  { label: "Tấm",    keywords: ["t", "tam"] },
  { label: "Thanh",  keywords: ["t", "thanh"] },
  { label: "Ống",    keywords: ["o", "ong"] },
  { label: "Sợi",    keywords: ["s", "soi"] },
  { label: "Tờ",     keywords: ["t", "to"] },
  // Đóng gói
  { label: "Thùng",  keywords: ["t", "thung"] },
  { label: "Hộp",    keywords: ["h", "hop"] },
  { label: "Bao",    keywords: ["b", "bao"] },
  { label: "Túi",    keywords: ["t", "tui"] },
  { label: "Gói",    keywords: ["g", "goi"] },
  { label: "Chai",   keywords: ["c", "chai"] },
  { label: "Can",    keywords: ["c", "can"] },
];

// Bỏ dấu tiếng Việt để so sánh linh hoạt
function removeDiacritics(str: string) {
  return str
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .toLowerCase();
}

function getSuggestions(query: string): string[] {
  if (!query.trim()) return UNIT_LIST.map(u => u.label);
  const q = removeDiacritics(query);
  return UNIT_LIST
    .filter(u =>
      removeDiacritics(u.label).startsWith(q) ||
      u.keywords.some(k => k.startsWith(q))
    )
    .map(u => u.label);
}

// ── Component ───────────────────────────────────────────────────────
interface UnitInputProps {
  value: string;
  onChange: (val: string) => void;
}

export function UnitInput({ value, onChange }: UnitInputProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState(value);
  const [highlighted, setHighlighted] = useState(0);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Đồng bộ khi value thay đổi từ bên ngoài (ví dụ AI điền vào)
  useEffect(() => { setQuery(value); }, [value]);

  const suggestions = getSuggestions(query);

  // Đóng dropdown khi click ra ngoài
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (!wrapperRef.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const select = (label: string) => {
    setQuery(label);
    onChange(label);
    setOpen(false);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    onChange(e.target.value);   // cho phép nhập tự do
    setHighlighted(0);
    setOpen(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!open) { if (e.key === "ArrowDown") setOpen(true); return; }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlighted(h => Math.min(h + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlighted(h => Math.max(h - 1, 0));
    } else if (e.key === "Enter" || e.key === "Tab") {
      if (suggestions[highlighted]) select(suggestions[highlighted]);
      setOpen(false);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  return (
    <div className="unit-wrapper" ref={wrapperRef}>
      <input
        ref={inputRef}
        className="unit-input"
        value={query}
        onChange={handleChange}
        onFocus={() => setOpen(true)}
        onKeyDown={handleKeyDown}
        placeholder="ĐVT"
        autoComplete="off"
      />
      {open && suggestions.length > 0 && (
        <ul className="unit-dropdown">
          {suggestions.map((s, i) => (
            <li
              key={s}
              className={i === highlighted ? "unit-option active" : "unit-option"}
              onMouseDown={() => select(s)}          // mouseDown trước blur
              onMouseEnter={() => setHighlighted(i)}
            >
              {s}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}