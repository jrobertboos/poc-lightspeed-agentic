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
```
