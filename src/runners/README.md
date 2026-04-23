# Runners

Server execution utilities.

## Modules

- `uvicorn.py` - Uvicorn server wrapper for development

## Usage

```bash
# Via module
python -m src.runners.uvicorn

# Or use uvicorn directly
uvicorn src.main:app --reload
```

## Configuration

The runner defaults can be overridden:

```python
from src.runners import run

run(host="127.0.0.1", port=8000, reload=True)
```
