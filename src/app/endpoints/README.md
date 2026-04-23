# Endpoints

FastAPI route handlers organized by domain.

## Modules

| Module | Routes | Purpose |
|--------|--------|---------|
| `health.py` | `GET /health`, `GET /ready` | Liveness and readiness probes |
| `query.py` | `POST /query` | Send messages to agents |
| `agents.py` | `GET /agents`, `GET /agents/{agent_name}` | List and inspect registered agents |
| `workflow.py` | `GET /workflow`, `POST /workflow/run` | List and execute workflows |

## Adding a New Endpoint

1. Create a new module with `router = APIRouter(tags=["your-tag"])`
2. Define route handlers using `@router.get()`, `@router.post()`, etc.
3. Register the router in `../routers.py`
