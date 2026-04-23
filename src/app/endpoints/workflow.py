"""Workflow endpoint for executing graph-based agent workflows."""

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.log import get_logger
from src.workflows.registry import get_workflow_registry

logger = get_logger(__name__)

router = APIRouter(prefix="/workflow", tags=["workflow"])


class WorkflowRequest(BaseModel):
    """Request payload for executing a workflow."""

    message: str = Field(..., description="User input to start the workflow")
    workflow_name: str | None = Field(None, description="Workflow name (uses default if not specified)")
    stream: bool = Field(False, description="Enable streaming response")


class WorkflowResponse(BaseModel):
    """Response from a workflow execution."""

    output: str = Field(..., description="Final workflow output")
    workflow_name: str = Field(..., description="Name of the executed workflow")
    history: list[dict] = Field(default_factory=list, description="Execution history")
    success: bool = Field(True, description="Whether workflow completed successfully")


class WorkflowListResponse(BaseModel):
    """Response containing available workflows."""

    workflows: list[dict] = Field(default_factory=list)


@router.get("", response_model=WorkflowListResponse)
async def list_workflows() -> WorkflowListResponse:
    """List all available workflows."""
    registry = get_workflow_registry()
    if registry is None:
        return WorkflowListResponse(workflows=[])

    workflows = []
    for name in registry.list_workflows():
        workflow = registry.get(name)
        if workflow:
            workflows.append({
                "name": workflow.name,
                "description": workflow.description,
                "start_node": workflow.config.start_node,
                "nodes": [n.agent for n in workflow.config.nodes],
            })

    return WorkflowListResponse(workflows=workflows)


async def _stream_workflow(runner, message: str) -> AsyncIterator[str]:
    """Stream workflow execution as Server-Sent Events."""
    async for event in runner.run_stream(message):
        yield f"data: {json.dumps(event)}\n\n"


@router.post("/run", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest) -> WorkflowResponse | StreamingResponse:
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

    if request.stream:
        return StreamingResponse(
            _stream_workflow(runner, request.message),
            media_type="text/event-stream",
        )

    result = await runner.run(request.message)

    if not result.success:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {result.error}",
        )

    return WorkflowResponse(
        output=result.output,
        workflow_name=workflow_name,
        history=result.state.history,
        success=result.success,
    )
