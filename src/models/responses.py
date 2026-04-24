"""Pydantic models for API response payloads."""

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response for health check endpoints."""

    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Response for error conditions."""

    detail: str = Field(..., description="Error message")


class AgentResponse(BaseModel):
    """Response containing agent details."""

    name: str = Field(..., description="Agent name")
    description: str | None = Field(None, description="Agent description")


class AgentListResponse(BaseModel):
    """Response containing a list of agents."""

    agents: list[AgentResponse] = Field(default_factory=list)


class ToolCall(BaseModel):
    """A tool call made by the agent."""

    tool_name: str = Field(..., description="Name of the tool called")
    tool_call_id: str = Field(..., description="Unique identifier for this tool call")
    args: dict[str, Any] | str | None = Field(None, description="Arguments passed to the tool")


class ToolResult(BaseModel):
    """Result from a tool execution."""

    tool_name: str = Field(..., description="Name of the tool")
    tool_call_id: str = Field(..., description="ID of the tool call this result corresponds to")
    content: Any = Field(..., description="Tool output content")
    outcome: str = Field("success", description="Outcome: success, failed, or denied")


class AgentRunResponse(BaseModel):
    """Response from running an agent."""

    output: Any = Field(..., description="Agent output")
    tool_calls: list[ToolCall] = Field(default_factory=list, description="Tool calls made during execution")
    tool_results: list[ToolResult] = Field(default_factory=list, description="Results from tool executions")


class WorkflowRunResponse(BaseModel):
    """Response from a workflow execution."""

    output: str = Field(..., description="Final workflow output")
    history: list[dict] = Field(default_factory=list, description="Execution history")


class WorkflowResponse(BaseModel):
    """Response containing workflow details."""

    name: str = Field(..., description="Workflow name")
    description: str | None = Field(None, description="Workflow description")
    start_node: str = Field(..., description="Starting node of the workflow")
    nodes: list[str] = Field(default_factory=list, description="List of agent nodes in the workflow")


class WorkflowListResponse(BaseModel):
    """Response containing available workflows."""

    workflows: list[WorkflowResponse] = Field(default_factory=list)