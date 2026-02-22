from tiktoken import get_encoding

enc = get_encoding("cl100k_base")

def chunk_text(text, size=400, overlap=50):
    tokens = enc.encode(text)
    chunks = []

    start = 0
    while start < len(tokens):
        end = start + size
        chunk = enc.decode(tokens[start:end])
        chunks.append(chunk)
        start = end - overlap

    return chunks
