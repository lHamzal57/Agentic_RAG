import os
import shutil
from fastapi import UploadFile
from app.core.config import settings
from app.utils.ids import new_doc_id
from app.utils.files import validate_upload_file


class FileService:
    def save_upload(self, upload: UploadFile) -> tuple[str, str]:
        validate_upload_file(upload)

        doc_id = new_doc_id()
        original_name = upload.filename or "unknown"
        ext = os.path.splitext(original_name)[1].lower()
        safe_filename = f"{doc_id}{ext}"

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        saved_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)

        return doc_id, saved_path