import os
from fastapi import UploadFile
from app.core.config import settings


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower().lstrip(".")


def validate_upload_file(upload: UploadFile) -> None:
    ext = get_file_extension(upload.filename or "")
    if ext not in settings.allowed_extensions_list:
        raise ValueError(f"Unsupported file type: .{ext}")