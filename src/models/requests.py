"""Pydantic models for API request payloads."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request payload for querying an agent."""
    message: str = Field(..., description="User message to send to the agent")
    agent_name: str = Field("root", description="Agent to route the query to")
