import os
import io
import json
import logging
import traceback
from pathlib import Path
import google.generativeai as genai
import anthropic
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

def _load_secret(key: str) -> str | None:
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)


GEMINI_API_KEY  = _load_secret("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
GEMINI_MODEL    = _load_secret("GEMINI_MODEL") or os.getenv("GEMINI_MODEL")
ANTHROPIC_KEY   = _load_secret("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL    = "claude-sonnet-4-20250514"

_gemini_model   = None
_claude_client  = None

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    _gemini_model = genai.GenerativeModel(GEMINI_MODEL)
    log.info(f"Gemini ready ({GEMINI_MODEL})")
else:
    log.warning("GEMINI_API_KEY chưa được cấu hình")

if ANTHROPIC_KEY:
    _claude_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    log.info(f"Claude ready ({CLAUDE_MODEL})")
else:
    log.warning("ANTHROPIC_API_KEY chưa được cấu hình — fallback sẽ không hoạt động")

SYSTEM_PROMPT = """
Bạn là chuyên gia trích xuất dữ liệu hàng hóa từ tài liệu tiếng Việt.

THUẬT NGỮ KỸ THUẬT thường gặp — KHÔNG được sửa, KHÔNG được bỏ dấu:
  khổ (width), chu vi (circumference), răng (teeth), mặt (side),
  dây đai (belt), cái, bộ, cuộn, mét, chiếc, hộp

QUY TẮC BẮT BUỘC:
1. Giữ nguyên toàn bộ dấu tiếng Việt trong tên hàng.
2. don_gia: luôn gán 0 (khách hàng không ghi giá).
3. vat: chỉ chọn 0.08 hoặc 0.10. Không rõ → mặc định 0.08.
4. dvt: nếu không có → mặc định "Cái".
5. Không bỏ sót dòng sản phẩm nào trong tài liệu.
6. Chỉ trả về JSON object thuần túy — không markdown, không giải thích.

OUTPUT JSON:
{
  "khach_hang": {
    "ten":     "Tên công ty (chuỗi rỗng nếu không có)",
    "sdt":     "Số điện thoại (chuỗi rỗng nếu không có)",
    "dia_chi": "Địa chỉ (chuỗi rỗng nếu không có)"
  },
  "items": [
    {
      "stt":      1,
      "ten_hang": "Tên sản phẩm / Quy cách đầy đủ",
      "dvt":      "Đơn vị tính",
      "so_luong": 10,
      "don_gia":  0,
      "vat":      0.08,
      "ghi_chu":  ""
    }
  ]
}
"""

USER_PROMPT = "Trích xuất toàn bộ sản phẩm theo đúng cấu trúc JSON đã quy định."

def _mock_data() -> dict:
    return {
        "khach_hang": {"ten": "TEST (chưa có API key)", "sdt": "", "dia_chi": ""},
        "items": [
            {"stt": 1, "ten_hang": "Sản phẩm mẫu A", "dvt": "Cái", "so_luong": 5,  "don_gia": 0, "vat": 0.08, "ghi_chu": ""},
            {"stt": 2, "ten_hang": "Sản phẩm mẫu B", "dvt": "Bộ",  "so_luong": 2,  "don_gia": 0, "vat": 0.10, "ghi_chu": ""},
        ],
    }

def _read_image(file_bytes: bytes) -> bytes:
    return file_bytes

def _read_excel_or_csv(file_bytes: bytes, filename: str) -> str | bytes:
    ext = Path(filename).suffix.lower()
    if ext == ".csv":
        text = file_bytes.decode("utf-8", errors="replace")
        return f"Dữ liệu CSV:\n{text}"
    return file_bytes

def _read_word(file_bytes: bytes) -> str:
    import zipfile
    import xml.etree.ElementTree as ET
    NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        with z.open("word/document.xml") as f:
            tree = ET.parse(f)
    texts = [
        node.text
        for node in tree.iter(f"{{{NS}}}t")
        if node.text and node.text.strip()
    ]
    return "Nội dung tài liệu Word:\n" + " ".join(texts)

VIET_TERMS = [
    ("khổ",    "kho"),    
    ("răng",   "rang"),   
    ("mặt",    "mat"),    
    ("dây",    "day"),   
    ("đai",    "dai"),    
    ("cuộn",   "cuon"),
]

def confidence_check(result: dict) -> float:
    if not isinstance(result, dict):
        return 0.0

    items = result.get("items", [])
    if not items:
        log.warning("Không có items nào được trích xuất")
        return 0.0

    issues  = 0
    total   = len(items) * 3 

    for item in items:
        ten = (item.get("ten_hang") or "").lower()

        if not ten:
            issues += 3
            continue

        for correct, wrong in VIET_TERMS:
            if wrong in ten and correct not in ten:
                issues += 1
                log.debug(f"Mất dấu: '{wrong}' thay vì '{correct}' trong '{ten}'")

        qty = item.get("so_luong")
        if qty is None or qty == 0:
            issues += 1

        if not item.get("dvt"):
            issues += 1

    score = max(0.0, 1.0 - issues / total)
    log.info(f"Confidence score: {score:.2f} (issues={issues}/{total})")
    return score

def _parse_json(raw: str) -> dict | None:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("\n", 1)[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        log.error(f"JSON parse error: {e}\nRaw: {text[:300]}")
        return None


def _normalize(data: dict) -> dict:
    if not isinstance(data, dict):
        return {"khach_hang": {"ten": "", "sdt": "", "dia_chi": ""}, "items": []}
    kh = data.setdefault("khach_hang", {})
    kh.setdefault("ten",     "")
    kh.setdefault("sdt",     "")
    kh.setdefault("dia_chi", "")
    data.setdefault("items", [])
    return data

def _call_gemini(content_parts: list, mime_type: str | None = None) -> dict | None:
    if not _gemini_model:
        return None
    try:
        log.info(f"Gọi Gemini ({GEMINI_MODEL})...")
        parts = []
        for part in content_parts:
            if isinstance(part, bytes):
                parts.append({"mime_type": mime_type or "image/jpeg", "data": part})
            else:
                parts.append(part) 

        response = _gemini_model.generate_content(
            [SYSTEM_PROMPT, USER_PROMPT, *parts],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.0,
            ),
        )
        return _parse_json(response.text)
    except Exception as e:
        log.error(f"Gemini error: {e}\n{traceback.format_exc()}")
        return None

def _call_claude(content_parts: list, is_image: bool, image_bytes: bytes | None = None) -> dict | None:
    if not _claude_client:
        log.warning("Không có ANTHROPIC_API_KEY — bỏ qua fallback")
        return None
    try:
        log.info(f"Fallback Claude ({CLAUDE_MODEL})...")

        if is_image and image_bytes:
            import base64
            img_b64 = base64.standard_b64encode(image_bytes).decode()
            user_content = [
                {
                    "type": "image",
                    "source": {
                        "type":       "base64",
                        "media_type": "image/jpeg",
                        "data":       img_b64,
                    },
                },
                {"type": "text", "text": USER_PROMPT},
            ]
        else:
            text_part = content_parts[0] if content_parts else ""
            user_content = [{"type": "text", "text": f"{USER_PROMPT}\n\n{text_part}"}]

        response = _claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        raw = response.content[0].text
        return _parse_json(raw)
    except Exception as e:
        log.error(f"Claude error: {e}\n{traceback.format_exc()}")
        return None
    
def extract_with_progress(uploaded_file):
    if not _gemini_model and not _claude_client:
        yield ("done", _mock_data())
        return

    ext = Path(uploaded_file.name).suffix.lower()

    yield ("reading", None)
    is_image    = False
    image_bytes = None
    mime_type   = None
    gemini_parts: list = []

    try:
        if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
            is_image  = True
            mime_map  = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                         ".png": "image/png",  ".webp": "image/webp", ".bmp": "image/bmp"}
            mime_type   = mime_map.get(ext, "image/jpeg")
            image_bytes = _read_image(uploaded_file)
            gemini_parts.append(image_bytes)
        elif ext in {".xlsx", ".xls"}:
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            gemini_parts.append(_read_excel_or_csv(uploaded_file))
        elif ext == ".csv":
            gemini_parts.append(_read_excel_or_csv(uploaded_file))
        elif ext in {".docx", ".doc"}:
            gemini_parts.append(_read_word(uploaded_file))
        else:
            yield ("error", f"Định dạng chưa hỗ trợ: {ext}")
            return
    except Exception as e:
        yield ("error", str(e))
        return

    yield ("gemini", None)
    gemini_result = _call_gemini(gemini_parts, mime_type=mime_type)

    if gemini_result is not None:
        yield ("preview", _normalize(gemini_result))

        score = confidence_check(gemini_result)
        yield ("checking", score)

        if score >= 0.8:
            log.info("Gemini passed")
            yield ("done", _normalize(gemini_result))
            return

        log.warning(f"Score thấp ({score:.2f}) → fallback Claude")
    else:
        log.warning("Gemini trả về None → fallback Claude")

    yield ("fallback", None)
    claude_result = _call_claude(gemini_parts, is_image=is_image, image_bytes=image_bytes)

    if claude_result is not None:
        log.info("Claude fallback thành công")
        yield ("done", _normalize(claude_result))
        return

    log.error("Cả Gemini lẫn Claude đều thất bại")
    yield ("error", "Cả Gemini lẫn Claude đều không đọc được file này.")

def extract_data_from_file(file_bytes: bytes, filename: str) -> dict | None:
    if not _gemini_model and not _claude_client:
        log.warning("Không có API key nào — trả về Mock Data")
        return _mock_data()

    ext = Path(filename).suffix.lower()
    is_image    = False
    image_bytes = None
    mime_type   = None
    gemini_parts: list = []

    try:
        if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
            is_image    = True
            mime_map    = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                           ".png": "image/png",  ".webp": "image/webp", ".bmp": "image/bmp"}
            mime_type   = mime_map.get(ext, "image/jpeg")
            image_bytes = _read_image(file_bytes)
            gemini_parts.append(image_bytes)
        elif ext in {".xlsx", ".xls"}:
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            gemini_parts.append(_read_excel_or_csv(file_bytes, filename))
        elif ext == ".csv":
            gemini_parts.append(_read_excel_or_csv(file_bytes, filename))
        elif ext in {".docx", ".doc"}:
            gemini_parts.append(_read_word(file_bytes))
        else:
            log.error(f"Định dạng chưa hỗ trợ: {ext}")
            return None
    except Exception as e:
        log.error(f"Lỗi đọc file: {e}\n{traceback.format_exc()}")
        return None

    result = _call_gemini(gemini_parts, mime_type=mime_type)
    if result is not None:
        score = confidence_check(result)
        if score >= 0.8:
            return _normalize(result)
        log.warning(f"Gemini score thấp ({score:.2f}) — fallback Claude")
    else:
        log.warning("Gemini None — fallback Claude")

    fallback = _call_claude(gemini_parts, is_image=is_image, image_bytes=image_bytes)
    if fallback is not None:
        return _normalize(fallback)

    log.error("Cả Gemini lẫn Claude đều thất bại")
    return None