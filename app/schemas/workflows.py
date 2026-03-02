from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional


class WorkflowType(str, Enum):
    GeneralQuestionWorkflow = "GeneralQuestionWorkflow"
    SystemArchitectureWorkflow = "SystemArchitectureWorkflow"
    TestCasesWorkflow = "TestCasesWorkflow"
    TestPlanWorkflow = "TestPlanWorkflow"
    TestReviewWorkflow = "TestReviewWorkflow"


class WorkflowQueryRequest(BaseModel):
    doc_id: str
    workflow: WorkflowType
    question: Optional[str] = Field(default=None)  # optional
    top_k: int | None = Field(default=None, ge=1, le=50)

    # NEW: optional user-provided artifact input (e.g. existing test cases)
    inputs: Optional[str] = Field(default=None)

    # NEW: optional explicit use-cases (if user already generated them)
    use_cases: Optional[str] = Field(default=None)


class WorkflowQueryResponse(BaseModel):
    doc_id: str
    workflow: WorkflowType
    answer: str
    chunks_used: list[dict[str, Any]]