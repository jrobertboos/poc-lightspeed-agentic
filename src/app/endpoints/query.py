"""Query endpoint for agent interactions."""

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["query"])


@router.post("/query")
async def query_agent():
    """Send a message to an agent and receive a response."""
    raise HTTPException(status_code=501, detail="Not implemented")