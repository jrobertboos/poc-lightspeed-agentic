"""FastAPI application entry point with lifespan management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.agents import initialize_registry
from src.app import register_routers
from src.config import load_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize configuration and agent registry on startup."""
    config = load_config()
    registry = initialize_registry(config)
    app.state.agent_registry = registry
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
