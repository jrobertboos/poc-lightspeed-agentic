"""Pydantic models for API response payloads."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response for health check endpoints."""
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")


class QueryResponse(BaseModel):
    """Response from an agent query."""

    response: str = Field(..., description="Agent response text")
    agent_name: str = Field(..., description="Agent that handled the query")


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