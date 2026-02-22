# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from api.utils import validate_mime_type, save_file
from services.document_loader import extract_text
import ollama
import chromadb

app = FastAPI()
chroma = chromadb.PersistentClient(path="./db")
collection = chroma.get_or_create_collection("docs")


@app.post("/query")
def query(q: str):
    results = collection.query(query_texts=[q], n_results=1)
    context = results["documents"][0][0] if results["documents"] else ""

    answer = ollama.generate(
        model="tinyllama",
        prompt=f"Context:\n{context}\n\nQuestion: {q}\n\n Answer Clearly and Concisely:"
    )

    return {"answer":answer["response"]}

@app.post("/add")
def add_Knowledge(text: str):
    """Add New Docs to the embded vector db"""
    try:
        import uuid
        doc_id = str(uuid.uuid4())
        # Add text to chroma collection
        collection.add(documents=[text], ids=[doc_id])

        return {
            "status": "success",
            "message": "Content Added",
            "id":doc_id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/files/validate")
async def validate_file(file: UploadFile = File(...)):
    try:
        validate_mime_type(file.content_type)

        file_bytes = await file.read()
        text = extract_text(file_bytes, file.content_type)

        if not text.strip():
            raise HTTPException(status_code=400, detail="File contains no readable text")

        # ai_result_raw = check_file_content(text)
        # ai_result = json.loads(ai_result_raw)

        # if not ai_result.get("valid"):
        #     raise HTTPException(
        #         status_code=400,
        #         detail=f"AI validation failed: {ai_result.get('reason')}"
        #     )

        file_id = save_file(file_bytes, file.filename)

        return {
            "file_id": file_id,
            "filename": file.filename,
            "status": "validated"
        }

    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
