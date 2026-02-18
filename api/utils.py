# utils.py
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/csv"
}

def validate_mime_type(content_type: str):
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Unsupported file type: {content_type}")

# utils.py
import uuid
from pathlib import Path

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_file(file_bytes: bytes, original_name: str) -> str:
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{original_name}"
    file_path.write_bytes(file_bytes)
    return file_id
