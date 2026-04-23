"""Pydantic configuration models for application settings."""

from pydantic import BaseModel, Field


class ServiceConfig(BaseModel):
    """HTTP server configuration."""
    host: str = "0.0.0.0"
    port: int = 8080

class AgentConfig(BaseModel):
    """Configuration for a single AI agent."""

    name: str
    description: str = ""
    model: str = Field(default="openai:gpt-4o-mini")
    instructions: str | None = None
    subagents: list[str] = Field(default_factory=list)

class AppConfig(BaseModel):
    """Root application configuration."""

    name: str = "Lightspeed Agentic"
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    agents: list[AgentConfig] = Field(default_factory=list)
