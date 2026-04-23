"""Router registration for FastAPI application."""

from fastapi import FastAPI

from src.app.endpoints import agents, health, query, workflows


def register_routers(app: FastAPI) -> None:
    """Register all API routers with the FastAPI application."""
    app.include_router(health.router)
    app.include_router(query.router)
    app.include_router(agents.router)
    app.include_router(workflows.router)
