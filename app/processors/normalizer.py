from typing import List
from app.schemas.common import StructuredBlock


def normalize_blocks(blocks: List[StructuredBlock]) -> List[StructuredBlock]:
    normalized: List[StructuredBlock] = []
    for b in blocks:
        text = " ".join(b.content.split())  # collapse whitespace
        if not text:
            continue
        normalized.append(b.model_copy(update={"content": text}))
    return normalized