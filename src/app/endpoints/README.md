# Endpoints

FastAPI route handlers organized by domain.

## Modules

| Module | Routes | Purpose |
|--------|--------|---------|
| `health.py` | `GET /health`, `GET /ready` | Liveness and readiness probes |
| `query.py` | `POST /query` | Send messages to agents (supports streaming) |
| `agents.py` | `GET /agents`, `GET /agents/{name}` | List and inspect registered agents |

## Adding a New Endpoint

1. Create a new module with `router = APIRouter(tags=["your-tag"])`
2. Define route handlers using `@router.get()`, `@router.post()`, etc.
3. Register the router in `../routers.py`
