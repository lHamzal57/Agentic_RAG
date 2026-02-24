from typing import List, Dict


def build_rag_prompt(question: str, chunks: List[Dict]) -> str:
    context_blocks = []
    for c in chunks:
        context_blocks.append(
            f"[Chunk ID: {c['id']}]\n{c['text']}"
        )

    context = "\n\n".join(context_blocks) if context_blocks else "(No relevant context found)"

    return f"""You are a BRD-aware assistant.

Use ONLY the provided context to answer the question.
If the answer is not in the context, say so clearly.

Context:
{context}

Question:
{question}

Answer clearly and concisely.
Include referenced chunk IDs when possible.
"""