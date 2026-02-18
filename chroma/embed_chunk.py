import chromadb
from services.document_loader import load_document_text
 
client = chromadb.PersistentClient(path="./db")
collection = client.get_or_create_collection("docs")


def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    return chunks

file = input("Enter File Name: ").strip()
embeded_text = load_document_text(f"api/storage/uploads/{file}")

chunks = chunk_text(embeded_text)

collection.add(
    documents=chunks,
    ids=[f"brd_{i}" for i in range(len(chunks))]
)

print(f"{len(chunks)} chunks embedded")
