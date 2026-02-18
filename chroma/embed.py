import chromadb
from docx import Document

client = chromadb.PersistentClient(path="./db")
collection = client.get_or_create_collection("docs")

file = input("Enter File Name: ").strip()
print("File: ",file)
doc = Document(f"./api/storage/uploads/{file}")

text = "\n".join(
    paragraph.text
    for paragraph in doc.paragraphs
    if paragraph.text.strip()
)

collection.add(
    documents=[text],
    ids=["brd"]
)

print("Document Embedding stored")