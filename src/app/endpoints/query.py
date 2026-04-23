"""Query endpoint for agent interactions."""

from fastapi import APIRouter, HTTPException

from src.agents import get_registry
from src.models import QueryRequest, QueryResponse
from src.log import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest) -> QueryResponse:
    """Send a message to an agent and receive a response."""
    registry = get_registry()

    agent = registry.get(request.agent_name)
    if agent is None:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{request.agent_name}' not found. Available: {registry.list_agents()}",
        )

    result = await agent.run(request.message)

    return QueryResponse(
        response=result.output,
        agent_name=request.agent_name,
    )