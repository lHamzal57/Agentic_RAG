from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.dependencies.chroma import get_chroma_collection
from app.services.file_service import FileService
from app.services.ingestion_service import IngestionService
from app.services.file_inspection_service import FileInspectionService
from app.services.file_status_service import FileStatusService
from app.schemas.files import UploadFileResponse, FileStatusResponse, FileChunksResponse
router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=UploadFileResponse)
async def upload_and_index_file(
    file: UploadFile = File(...),
    collection = Depends(get_chroma_collection),
):
    try:
        file_service = FileService()
        doc_id, saved_path = file_service.save_upload(file)

        ingestion_service = IngestionService(collection)
        # re-index/update → replace_existing=True
        chunks_indexed = ingestion_service.ingest_file(doc_id=doc_id, file_path=saved_path)

        return UploadFileResponse(
            doc_id=doc_id,
            filename=file.filename or "",
            saved_path=saved_path,
            chunks_indexed=chunks_indexed,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload/index failed: {str(e)}")

@router.get("/{doc_id}/status", response_model=FileStatusResponse)
async def get_file_status(    
    doc_id: str,
    collection=Depends(get_chroma_collection),
):
    try:
        service = FileStatusService(collection)
        return FileStatusResponse(**service.get_status(doc_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
    
@router.get("/{doc_id}/chunks", response_model=FileChunksResponse)
async def get_file_chunks(
    doc_id: str,
    limit: int = 10,
    include_text: bool = False,  # <-- added
    collection=Depends(get_chroma_collection),
):
    try:
        service = FileInspectionService(collection)
        return FileChunksResponse(
            **service.list_chunks(doc_id=doc_id, limit=limit, include_text=include_text)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunk inspection failed: {str(e)}")