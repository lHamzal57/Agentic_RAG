from fastapi import Depends
import chromadb
from app.core.config import settings

def get_chroma_client():
    return chromadb.PersistentClient(path=settings.CHROMA_PATH)

def get_collection(client=Depends(get_chroma_client)):
    return client.get_or_create_collection(
        name="brd_docs"
    )
