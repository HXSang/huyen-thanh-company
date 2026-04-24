import { useState, useEffect } from "react";

interface NumericInputProps {
  value: number;
  onChange: (val: number) => void;
  min?: number;
  className?: string;
  placeholder?: string;
}

export function NumericInput({
  value,
  onChange,
  min: _min = 0,
  className,
  placeholder,
}: NumericInputProps) {
  // Format số thành chuỗi có dấu "." mỗi 3 chữ số (kiểu Việt Nam)
  const format = (n: number) =>
    n === 0 ? "" : n.toLocaleString("vi-VN") ?? "0";

  const [display, setDisplay] = useState(format(value));

  useEffect(() => {
    // Chỉ đồng bộ lại khi giá trị từ bên ngoài thay đổi
    setDisplay(format(value));
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Bỏ tất cả ký tự không phải số (kể cả dấu chấm đã có)
    const raw = e.target.value.replace(/\D/g, "");
    const num = raw === "" ? 0 : Number(raw);

    // Hiển thị ngay với dấu chấm ngăn cách hàng nghìn
    setDisplay(raw === "" ? "" : num.toLocaleString("vi-VN"));
    onChange(num);
  };

  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    // Đặt con trỏ về cuối khi focus
    const el = e.target;
    setTimeout(() => {
      el.selectionStart = el.selectionEnd = el.value.length;
    }, 0);
  };

  return (
    <input
      type="text"
      inputMode="numeric"
      className={className}
      placeholder={placeholder ?? "0"}
      value={display}
      onFocus={handleFocus}
      onChange={handleChange}
      style={{ textAlign: "right" }}
    />
  );
}
