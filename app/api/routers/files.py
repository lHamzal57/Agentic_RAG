from fastapi import APIRouter, Depends, UploadFile
from app.dependencies.chroma import get_collection
from app.services.ingestion_service import IngestionService
import shutil

router = APIRouter()

@router.post("/files/index")
async def index_file(
    file: UploadFile,
    collection=Depends(get_collection)
):

    path = f"storage/uploads/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    service = IngestionService(collection)
    count = service.ingest(path)

    return {"chunks_indexed": count}
