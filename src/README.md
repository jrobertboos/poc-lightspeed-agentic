# Source Code

Core application code for Lightspeed Agentic.

## Structure

| Directory | Purpose |
|-----------|---------|
| `agents/` | Agent creation and registry |
| `app/` | FastAPI application and routing |
| `config/` | YAML configuration loading |
| `models/` | Pydantic request/response schemas |
| `runners/` | Server execution utilities |

## Entry Points

- `main.py` - FastAPI application instance with lifespan management
- `runners/uvicorn.py` - Development server runner
