from app.schemas.workflows import WorkflowType
from app.workflows.registry import get_workflow_strategy

# Optional Just For Testing
def build_workflow_prompt(workflow: WorkflowType, question: str, chunks: list[dict]) -> str:
    strategy = get_workflow_strategy(workflow)
    return strategy.build_prompt(question=question, chunks=chunks)