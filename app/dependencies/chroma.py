import chromadb
from app.core.config import settings


def get_chroma_client():
    return chromadb.PersistentClient(path=settings.CHROMA_PATH)


def get_chroma_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=settings.CHROMA_COLLECTION)