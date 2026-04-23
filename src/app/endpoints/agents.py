"""Agent listing and retrieval endpoints."""

from fastapi import APIRouter, HTTPException

from src.agents import get_registry
from src.models import AgentListResponse, AgentResponse

router = APIRouter(tags=["agents"])


@router.get("/agents", response_model=AgentListResponse)
async def list_agents() -> AgentListResponse:
    """List all available agents."""
    registry = get_registry()
    return AgentListResponse(
        agents=[
            AgentResponse(
                name=agent.name,
                description=agent.description,
            )
            for name in registry.list_agents()
            if (agent := registry.get(name))
        ]
    )


@router.get("/agents/{agent_name}", response_model=AgentResponse)
async def get_agent(agent_name: str) -> AgentResponse:
    """Get details for a specific agent by name."""
    registry = get_registry()
    agent = registry.get(agent_name)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    return AgentResponse(name=agent.name, description=agent.description)
