from app.schemas.workflows import WorkflowType


def _format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "(No relevant context found)"

    parts = []
    for c in chunks:
        parts.append(f"[Chunk ID: {c['id']}]\n{c['text']}")
    return "\n\n".join(parts)


def build_workflow_prompt(
    workflow: WorkflowType,
    question: str,
    chunks: list[dict]
) -> str:
    context = _format_context(chunks)

    if workflow == WorkflowType.GeneralQuestionWorkflow:
        return f"""You are a BRD-aware assistant.

Use ONLY the provided context to answer the user's question.
If the answer is not present in the context, say so clearly.

Context:
{context}

Question:
{question}

Answer clearly and concisely.
Include referenced chunk IDs when possible.
"""

    if workflow == WorkflowType.SystemArchitectureWorkflow:
        return f"""You are a system architecture analyst reviewing a BRD / technical document.

Task:
- Extract and explain the system architecture relevant to the question.
- Identify components, integrations, data flow, interfaces, dependencies, and constraints if present.
- Do not invent architecture details not found in the context.

Context:
{context}

Question:
{question}

Return in this structure:
1) Summary
2) Components
3) Interactions / Data Flow
4) Assumptions / Missing Details
5) Referenced Chunk IDs
"""

    if workflow == WorkflowType.TestCasesWorkflow:
        return f"""You are a QA analyst generating or evaluating system test cases from BRD context.

Task:
- Answer the question using only the provided context.
- Focus on testable requirements, acceptance criteria, validations, business rules, edge cases, and negative cases.
- If a requirement is ambiguous or missing, state it explicitly.

Context:
{context}

Question:
{question}

Return in this structure:
1) Relevant Requirements Summary
2) Suggested / Mapped Test Cases (if applicable)
3) Edge Cases / Negative Cases
4) Gaps / Ambiguities
5) Referenced Chunk IDs
"""

    if workflow == WorkflowType.TestPlanWorkflow:
        return f"""You are a QA lead building a test plan from BRD context.

Task:
- Answer the question with a test planning perspective.
- Focus on scope, objectives, test types, dependencies, environments, risks, assumptions, and coverage strategy.
- Use only the provided context.

Context:
{context}

Question:
{question}

Return in this structure:
1) Scope / Objective
2) Test Scope (In / Out)
3) Test Types / Strategy
4) Dependencies / Environment Needs
5) Risks / Assumptions
6) Referenced Chunk IDs
"""

    if workflow == WorkflowType.TestReviewWorkflow:
        return f"""You are a senior QA reviewer reviewing a test artifact against BRD context.

Task:
- Evaluate the question/request from a review perspective.
- Identify completeness issues, inconsistencies, missing coverage, unclear assumptions, and quality risks.
- Use only provided context.

Context:
{context}

Question:
{question}

Return in this structure:
1) Review Summary
2) Findings (Issues / Risks)
3) Missing Coverage / Missing Information
4) Recommendations
5) Referenced Chunk IDs
"""

    # defensive fallback
    return f"""Use ONLY the provided context to answer the question.

Context:
{context}

Question:
{question}

Answer clearly and include chunk IDs.
"""