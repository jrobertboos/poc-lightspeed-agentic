"""Pydantic models for API request payloads."""

from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    """Request payload for running an agent."""

    message: str = Field(..., description="User message to send to the agent")
    agent_name: str | None = Field(None, description="Agent name (uses first available if not specified)")


class WorkflowRunRequest(BaseModel):
    """Request payload for executing a workflow."""

    message: str = Field(..., description="User input to start the workflow")
    workflow_name: str | None = Field(None, description="Workflow name (uses default if not specified)")
