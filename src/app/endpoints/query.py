"""Query endpoint for agent interactions with streaming support."""

import json
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic_ai.messages import (
    BuiltinToolCallPart,
    BuiltinToolReturnPart,
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    PartEndEvent,
    PartStartEvent,
    TextPart,
    TextPartDelta,
    ThinkingPart,
    ThinkingPartDelta,
    ToolCallPart,
    ToolCallPartDelta,
    ToolReturnPart,
)

from src.agents import get_registry
from src.models import QueryRequest, QueryResponse
from src.log import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["query"])


def _serialize_event(event: Any) -> dict | None:
    """Serialize a stream event to a dictionary."""
    if isinstance(event, PartStartEvent):
        part = event.part
        if isinstance(part, TextPart):
            return {"type": "text_start", "content": part.content}
        elif isinstance(part, ToolCallPart):
            return {
                "type": "tool_call",
                "tool_name": part.tool_name,
                "tool_call_id": part.tool_call_id,
                "args": part.args,
            }
        elif isinstance(part, ThinkingPart):
            return {"type": "thinking_start", "content": part.content}
        elif isinstance(part, BuiltinToolCallPart):
            return {
                "type": "builtin_tool_call",
                "tool_name": part.tool_name,
                "tool_call_id": part.tool_call_id,
                "args": part.args,
            }
        elif isinstance(part, BuiltinToolReturnPart):
            return {
                "type": "builtin_tool_result",
                "tool_call_id": part.tool_call_id,
                "content": part.content,
            }
        elif isinstance(part, ToolReturnPart):
            return {
                "type": "tool_result",
                "tool_call_id": part.tool_call_id,
                "content": part.content,
            }
    elif isinstance(event, PartDeltaEvent):
        delta = event.delta
        if isinstance(delta, TextPartDelta):
            return {"type": "text_delta", "content": delta.content_delta}
        elif isinstance(delta, ThinkingPartDelta):
            return {"type": "thinking_delta", "content": delta.content_delta}
        elif isinstance(delta, ToolCallPartDelta):
            return {"type": "tool_call_delta", "args_delta": delta.args_delta}
    elif isinstance(event, PartEndEvent):
        return {"type": "part_end", "part_index": event.index}
    elif isinstance(event, FinalResultEvent):
        return {"type": "final_result"}
    elif isinstance(event, FunctionToolCallEvent):
        return {
            "type": "tool_call",
            "tool_name": event.part.tool_name,
            "tool_call_id": event.tool_call_id,
            "args": event.part.args,
        }
    elif isinstance(event, FunctionToolResultEvent):
        result = event.result
        content = result.content if hasattr(result, "content") else str(result)
        return {
            "type": "tool_result",
            "tool_call_id": event.tool_call_id,
            "content": content,
        }
    return None


async def _stream_response(agent, message: str) -> AsyncIterator[str]:
    """Stream agent response as Server-Sent Events."""
    async for event in agent.run_stream_events(message):
        data = _serialize_event(event)
        if data:
            yield f"data: {json.dumps(data)}\n\n"
        else:
            logger.warning("Unhandled event type: %s", type(event).__name__)


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
            _stream_response(agent, request.message),
            media_type="text/event-stream",
        )

    result = await agent.run(request.message)

    return QueryResponse(
        response=result.output,
        agent_name=request.agent_name,
    )