# Config

YAML-based application configuration.

## Modules

- `loader.py` - Loads and validates `config.yaml` into Pydantic models
- `models.py` - Pydantic schemas for configuration structure

## Configuration Schema

```yaml
name: Lightspeed Agentic       # Application name
service:
  host: 0.0.0.0                # Server bind address
  port: 8080                   # Server port

agents:
  - name: agent-name           # Unique identifier
    description: ...           # Used in tool descriptions for delegation
    model: openai:gpt-4o-mini  # Pydantic AI model string
    instructions: |            # System prompt
      ...
    subagents: [other-agent]   # Optional: agents this one can delegate to
```

## Usage

```python
from src.config import load_config

config = load_config()  # Loads config.yaml from project root
```
