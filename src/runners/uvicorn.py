"""Uvicorn server runner for development and production."""

import uvicorn


def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Start the uvicorn server with the FastAPI application."""
    uvicorn.run("src.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run(reload=True)
