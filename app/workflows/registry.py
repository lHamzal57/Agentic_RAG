from app.schemas.workflows import WorkflowType
from app.workflows.general import GeneralQuestionWorkflow
from app.workflows.system_architecture import SystemArchitectureWorkflow
from app.workflows.test_cases import TestCasesWorkflow
from app.workflows.test_plan import TestPlanWorkflow
from app.workflows.test_review import TestReviewWorkflow
from app.workflows.base import BaseWorkflow


_WORKFLOW_REGISTRY: dict[WorkflowType, type[BaseWorkflow]] = {
    WorkflowType.GeneralQuestionWorkflow: GeneralQuestionWorkflow,
    WorkflowType.SystemArchitectureWorkflow: SystemArchitectureWorkflow,
    WorkflowType.TestCasesWorkflow: TestCasesWorkflow,
    WorkflowType.TestPlanWorkflow: TestPlanWorkflow,
    WorkflowType.TestReviewWorkflow: TestReviewWorkflow,
}


def get_workflow_strategy(workflow: WorkflowType) -> BaseWorkflow:
    cls = _WORKFLOW_REGISTRY.get(workflow)
    if cls is None:
        raise ValueError(f"Unsupported workflow: {workflow}")
    return cls()