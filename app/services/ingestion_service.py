from app.loaders.factory import get_loader
from app.processors.chunker import chunk_text

class IngestionService:

    def __init__(self, collection):
        self.collection = collection

    def ingest(self, file_path: str):

        loader = get_loader(file_path)
        text = loader.load(file_path)

        chunks = chunk_text(text)

        self.collection.add(
            documents=chunks,
            ids=[f"chunk_{i}" for i in range(len(chunks))]
        )

        return len(chunks)
