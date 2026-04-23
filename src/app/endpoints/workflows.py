"""Workflow endpoint for executing graph-based agent workflows."""

from fastapi import APIRouter, HTTPException

from src.log import get_logger
from src.models import (
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
)
from src.workflows.registry import get_workflow_registry

logger = get_logger(__name__)

router = APIRouter(tags=["workflows"])


@router.get("/workflows", response_model=WorkflowListResponse)
async def list_workflows() -> WorkflowListResponse:
    """List all available workflows."""
    registry = get_workflow_registry()
    if registry is None:
        return WorkflowListResponse(workflows=[])

    workflows = []
    for name in registry.list_workflows():
        workflow = registry.get(name)
        if workflow:
            workflows.append(
                WorkflowResponse(
                    name=workflow.name,
                    description=workflow.description,
                    start_node=workflow.config.start_node,
                    nodes=[n.agent for n in workflow.config.nodes],
                )
            )

    return WorkflowListResponse(workflows=workflows)


@router.get("/workflows/{workflow_name}", response_model=WorkflowResponse)
async def get_workflow(workflow_name: str) -> WorkflowResponse:
    """Get details for a specific workflow by name."""
    registry = get_workflow_registry()
    if registry is None:
        raise HTTPException(status_code=404, detail="No workflows configured")

    workflow = registry.get(workflow_name)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return WorkflowResponse(
        name=workflow.name,
        description=workflow.description,
        start_node=workflow.config.start_node,
        nodes=[n.agent for n in workflow.config.nodes],
    )


@router.post("/workflows/run", response_model=WorkflowRunResponse)
async def run_workflow(request: WorkflowRunRequest) -> WorkflowRunResponse:
    """Execute a workflow with the given input."""
    registry = get_workflow_registry()
    if registry is None:
        raise HTTPException(
            status_code=404,
            detail="No workflows configured",
        )

    workflow_names = registry.list_workflows()
    if not workflow_names:
        raise HTTPException(
            status_code=404,
            detail="No workflows available",
        )

    workflow_name = request.workflow_name or workflow_names[0]
    runner = registry.get_runner(workflow_name)

    if runner is None:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{workflow_name}' not found. Available: {workflow_names}",
        )

    result = await runner.run(request.message)

    if not result.success:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {result.error}",
        )

    return WorkflowRunResponse(
        output=result.output,
        workflow_name=workflow_name,
        history=result.state.history,
        success=result.success,
    )
