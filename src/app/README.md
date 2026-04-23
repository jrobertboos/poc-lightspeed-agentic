# App

FastAPI application setup and HTTP routing.

## Modules

- `routers.py` - Registers all endpoint routers with the FastAPI app
- `endpoints/` - Individual API endpoint modules

## Router Registration

All routers are registered in `routers.py`:

```python
def register_routers(app: FastAPI) -> None:
    app.include_router(health.router)
    app.include_router(query.router)
    app.include_router(agents.router)
    app.include_router(workflows.router)
```

## Endpoints

| Module | Routes | Purpose |
|--------|--------|---------|
| `health.py` | `GET /health`, `GET /ready` | Liveness and readiness probes |
| `query.py` | `POST /query` | Not implemented |
| `agents.py` | `GET /agents`, `GET /agents/{agent_name}` | List and inspect registered agents |
| `workflows.py` | `GET /workflows`, `POST /workflows/run` | List and execute workflows |
