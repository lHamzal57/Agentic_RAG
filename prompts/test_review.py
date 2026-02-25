"""
Prompts for TestReviewWorkflow
"""

JSON_STRUCTURE = """
{
    "status": "pass | needs_updates | insufficient_data",
    "summary": "...",
    "coverage": {
        "requirements_covered": [],
        "identified_gaps": []
    },
    "issues": [
        {
            "id": "ISS-001",
            "title": "...",
            "severity": "high | medium | low",
            "details": "...",
            "recommendation": "..."
        }
    ],
    "next_steps": []
}
""".strip()

def render_prompt(context: str, question: str) -> str:
    return f"""
You are a QA lead reviewing submitted test cases. Compare them against the
referenced BRD/User Story content. Highlight coverage, gaps, and actionable
feedback strictly in the JSON format below. If you lack enough context, set
status to "insufficient_data" and explain what is missing.

Specification (BRD/User Story):
{context}

Test cases submitted:
{question}

Response format:
{JSON_STRUCTURE}
""".strip()
