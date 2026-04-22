import { useRef, useState } from "react";
import { extractFile, QuoteData } from "../api/client";

interface Props {
  onResult: (data: QuoteData) => void;
}

export default function UploadPanel({ onResult }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [message, setMessage] = useState("");
  const [fileName, setFileName] = useState("");

  const handleFile = async (file: File) => {
    setFileName(file.name);
    setStatus("loading");
    setMessage("AI đang đọc file...");
    try {
      const data = await extractFile(file);
      onResult(data);
      setStatus("done");
      setMessage(`Trích xuất xong — ${data.items.length} sản phẩm`);
    } catch (e: any) {
      setStatus("error");
      setMessage(e.message ?? "Có lỗi xảy ra");
    }
  };

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <aside className="upload-panel">
      <h3>AI Trích Xuất</h3>

      <div
        className={`drop-zone ${status === "loading" ? "loading" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDrop={onDrop}
        onDragOver={e => e.preventDefault()}
      >
        <input
          ref={inputRef} type="file" hidden
          accept=".png,.jpg,.jpeg,.xlsx,.xls,.csv,.docx"
          onChange={onInputChange}
        />
        {status === "loading" ? (
          <div className="spinner" />
        ) : (
          <>
            <span className="upload-icon">📎</span>
            <p>{fileName || "Kéo thả hoặc click để chọn file"}</p>
            <small>PNG, JPG, Excel, CSV, Word</small>
          </>
        )}
      </div>

      {message && (
        <div className={`upload-msg ${status}`}>{message}</div>
      )}

      <p className="upload-tip">
        AI tự động đọc tên hàng, số lượng, đơn vị từ ảnh chụp hoặc file Excel.
      </p>
    </aside>
  );
}
