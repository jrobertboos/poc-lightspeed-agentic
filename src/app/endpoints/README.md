# Endpoints

FastAPI route handlers organized by domain.

## Modules

| Module | Routes | Purpose |
|--------|--------|---------|
| `health.py` | `GET /health`, `GET /ready` | Liveness and readiness probes |
| `query.py` | `POST /query` | Not implemented |
| `agents.py` | `GET /agents`, `GET /agents/{agent_name}`, `POST /agents/run` | List, inspect, and run agents |
| `workflows.py` | `GET /workflows`, `GET /workflows/{workflow_name}`, `POST /workflows/run` | List, inspect, and execute workflows |

## Adding a New Endpoint

1. Create a new module with `router = APIRouter(tags=["your-tag"])`
2. Define route handlers using `@router.get()`, `@router.post()`, etc.
3. Register the router in `../routers.py`
