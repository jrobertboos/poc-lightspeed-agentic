"""Query endpoint for agent interactions with streaming support."""

from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.agents import get_registry
from src.models import QueryRequest, QueryResponse, StreamChunkEvent, StreamDoneEvent
from src.log import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["query"])


async def _stream_response(agent, message: str, agent_name: str) -> AsyncIterator[str]:
    """Stream agent response as Server-Sent Events."""
    async with agent.run_stream(message) as stream:
        async for chunk in stream.stream_text(delta=True):
            event = StreamChunkEvent(chunk=chunk)
            yield f"data: {event.model_dump_json()}\n\n"

    done_event = StreamDoneEvent(agent_name=agent_name)
    yield f"data: {done_event.model_dump_json()}\n\n"


@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest) -> QueryResponse | StreamingResponse:
    """Send a message to an agent and receive a response."""
    registry = get_registry()

    agent = registry.get(request.agent_name)
    if agent is None:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{request.agent_name}' not found. Available: {registry.list_agents()}",
        )

    if request.stream:
        return StreamingResponse(
            _stream_response(agent, request.message, request.agent_name),
            media_type="text/event-stream",
        )

    result = await agent.run(request.message)

    return QueryResponse(
        response=result.output,
        agent_name=request.agent_name,
    )