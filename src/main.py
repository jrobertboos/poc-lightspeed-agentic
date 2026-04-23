"""FastAPI application entry point with lifespan management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.agents import initialize_registry
from src.app import register_routers
from src.config import load_config
from src.workflows.registry import initialize_workflow_registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize configuration, agent registry, and workflows on startup."""
    config = load_config()
    agent_registry = initialize_registry(config)
    workflow_registry = initialize_workflow_registry(config, agent_registry)
    app.state.agent_registry = agent_registry
    app.state.workflow_registry = workflow_registry
    app.state.config = config
    yield


app = FastAPI(
    title="Lightspeed Agentic",
    description="API for no code AI assistants with dynamic agents",
    version="0.1.0",
    lifespan=lifespan,
)

register_routers(app)


@app.get("/")
async def root():
    """Return API welcome message with docs link."""
    return {"message": "Lightspeed Agentic", "docs": "/docs"}
