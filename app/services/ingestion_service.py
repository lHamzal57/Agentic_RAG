from app.loaders.factory import get_loader
from app.processors.normalizer import normalize_blocks
from app.processors.chunker import split_blocks_into_chunks
from app.vectorstore.chroma_repository import ChromaRepository


class IngestionService:
    def __init__(self, collection):
        self.repo = ChromaRepository(collection)

    def ingest_file(self, doc_id: str, file_path: str, replace_existing: bool = False) -> int:
        loader = get_loader(file_path)
        blocks = normalize_blocks(loader.load(file_path))
        chunks = split_blocks_into_chunks(doc_id=doc_id, blocks=blocks)

        if replace_existing:
            self.repo.delete_doc_chunks(doc_id)

        return self.repo.add_chunks(chunks, use_upsert=True)