"""Agent listing and retrieval endpoints."""

from fastapi import APIRouter, HTTPException

from src.log import get_logger
from src.models import (
    AgentListResponse,
    AgentResponse,
    AgentRunRequest,
    AgentRunResponse,
    ToolCall,
    ToolResult,
)
from src.agents import get_registry

from pydantic_ai.messages import ToolCallPart, ToolReturnPart

logger = get_logger(__name__)

router = APIRouter(tags=["agents"])


@router.get("/agents", response_model=AgentListResponse)
async def list_agents() -> AgentListResponse:
    """List all available agents."""
    registry = get_registry()

    agents = []
    for name in registry.list_agents():
        agent = registry.get(name)
        if agent:
            agents.append(
                AgentResponse(
                    name=agent.name,
                    description=agent.description,
                )
            )

    return AgentListResponse(agents=agents)


@router.get("/agents/{agent_name}", response_model=AgentResponse)
async def get_agent(agent_name: str) -> AgentResponse:
    """Get details for a specific agent by name."""
    registry = get_registry()
    agent = registry.get(agent_name)
    
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    return AgentResponse(name=agent.name, description=agent.description)


@router.post("/agents/run", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest) -> AgentRunResponse:
    """Run an agent with the given input."""
    registry = get_registry()

    agent_names = registry.list_agents()
    if not agent_names:
        raise HTTPException(status_code=404, detail="No agents available")

    agent_name = request.agent_name or agent_names[0]
    agent = registry.get(agent_name)

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found. Available: {agent_names}",
        )

    try:
        result = await agent.run(request.message)
    except Exception as e:
        logger.error(f"Agent '{agent_name}' failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {e}",
        )

    output = result.output
    if hasattr(output, "model_dump"):
        output = output.model_dump()

    tool_calls: list[ToolCall] = []
    tool_results: list[ToolResult] = []

    for msg in result.all_messages():
        for part in msg.parts:
            if isinstance(part, ToolCallPart):
                tool_calls.append(ToolCall(
                    tool_name=part.tool_name,
                    tool_call_id=part.tool_call_id,
                    args=part.args,
                ))
            elif isinstance(part, ToolReturnPart):
                tool_results.append(ToolResult(
                    tool_name=part.tool_name,
                    tool_call_id=part.tool_call_id,
                    content=part.content,
                    outcome=part.outcome,
                ))

    return AgentRunResponse(
        output=output,
        tool_calls=tool_calls,
        tool_results=tool_results,
    )
