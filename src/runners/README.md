# Runners

Server execution utilities for running the FastAPI application.

## Available Runner Types

- `uvicorn.py` - Uvicorn server wrapper for development and production

## Usage

```bash
# Via module
python -m src.runners.uvicorn

# Or use uvicorn directly
uvicorn src.main:app --reload
```

## Programmatic Usage

```python
from src.runners import run

run(host="127.0.0.1", port=8000, reload=True)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | `str` | `"0.0.0.0"` | Host address to bind |
| `port` | `int` | `8000` | Port number |
| `reload` | `bool` | `False` | Enable auto-reload for development |
