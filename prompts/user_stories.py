from typing import Optional


JSON_ERROR_STRUCTURE = """
{
  "error": true,
  "reason": "..."
}
""".strip()


def render_prompt(
    *,
    context: str,
    conversation_title: Optional[str] = None,
    json_error_structure: str = JSON_ERROR_STRUCTURE
) -> str:
    """
    Extract business use cases / user flows from BRD context.
    Returns STRICT JSON ONLY, no markdown, no prose.

    Output schema:
    {
      "conversation_title": "...",
      "user_stories": [
        {
          "id": "UC-1",
          "title": "...",
          "actors": ["..."],
          "description": "... [Sources: ...]",
          "preconditions": ["..."],
          "main_flow": ["..."],
          "alternate_flows": ["..."],
          "business_rules": ["..."],
          "data_entities": ["..."],
          "integrations": ["..."],
          "notes": "..."
        }
      ]
    }
    """
    title_instruction = (
        f'Use this conversation_title exactly: "{conversation_title}".'
        if conversation_title
        else "Generate conversation_title (5–10 words, professional, BRD use-case extraction)."
    )

    return f"""
You are a senior QA/business analyst extracting BUSINESS USE CASES and USER FLOWS from a BRD.

STRICT OUTPUT RULES:
- Output MUST be valid JSON ONLY (no markdown, no code fences, no extra text).
- Output MUST be a single JSON object with EXACTLY these top-level keys:
  - "conversation_title" (string)
  - "user_stories" (array)
- Do NOT include any other root keys.

ERROR RULES:
- If context is empty OR clearly not BRD/User-Story-like, return ONLY:
{json_error_structure}

INPUT CONTEXT (RAG chunks with IDs; may be partial):
{context}

TITLE:
{title_instruction}

TRACEABILITY (MANDATORY):
- Every use case "description" MUST end with:
  "[Sources: <chunk_id_1>, <chunk_id_2>]"
- If you cannot identify relevant chunk IDs, use:
  "[Sources: none]"

USE CASE RULES:
- Use ONLY information supported by the context.
- Do NOT invent features.
- Prefer fewer, higher quality use cases over many speculative ones.
- Each use case should represent a business goal / user goal that can be tested.
- If the document is incomplete, include fewer use cases and note "Insufficient context" in "notes".

USE CASE ITEM SCHEMA (MANDATORY):
Each item in "user_stories" MUST contain EXACTLY these keys:
- "id": "UC-1", "UC-2", ...
- "title": concise name
- "actors": list of roles (strings). If unknown, use [].
- "description": short paragraph + sources tag
- "preconditions": list of strings (may be [])
- "main_flow": list of steps (may be [])
- "alternate_flows": list of strings (may be [])
- "business_rules": list of strings (may be [])
- "data_entities": list of strings (may be [])
- "integrations": list of strings (may be [])
- "notes": string (may be "")

QUALITY CHECK BEFORE RETURNING:
- Validate JSON syntax.
- Ensure IDs are unique and sequential UC-1, UC-2, ...
- Ensure all required keys exist in every use case item.
- No null values: use "" or [] instead.

NOW RETURN THE JSON OBJECT ONLY.
""".strip()


def render_prompt_text(
    *,
    context: str,
    json_error_structure: str = JSON_ERROR_STRUCTURE
) -> str:
    """
    Alternative: Extract use cases as a compact text list (not JSON).
    Useful if you only want a plain string to inject into TestCasesWorkflow.
    """
    return f"""
You are extracting BUSINESS USE CASES and USER FLOWS from BRD context.

OUTPUT RULES:
- Output MUST be plain text only (no JSON, no markdown).
- Each use case MUST be 1-3 lines maximum.
- Include chunk IDs at the end of each use case line in:
  [Sources: <chunk_id_1>, <chunk_id_2>]
- If context is empty or irrelevant, output exactly:
{json_error_structure}

CONTEXT:
{context}

Return format:
UC-1: <Title> — <1 sentence description>. [Sources: ...]
UC-2: ...

Generate only the list.
""".strip()