from enum import Enum
from pydantic import BaseModel
from typing import Any


class WorkflowType(str, Enum):
    GeneralQuestionWorkflow = "GeneralQuestionWorkflow"
    SystemArchitectureWorkflow = "SystemArchitectureWorkflow"
    TestCasesWorkflow = "TestCasesWorkflow"
    TestPlanWorkflow = "TestPlanWorkflow"
    TestReviewWorkflow = "TestReviewWorkflow"


class WorkflowQueryRequest(BaseModel):
    doc_id: str
    workflow: WorkflowType
    question: str
    top_k: int | None = None


class WorkflowQueryResponse(BaseModel):
    doc_id: str
    workflow: WorkflowType
    answer: str
    chunks_used: list[dict[str, Any]]