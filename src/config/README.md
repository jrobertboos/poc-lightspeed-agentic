# Config

YAML-based application configuration.

## Modules

- `loader.py` - Loads and validates `config.yaml` into Pydantic models
- `models.py` - Pydantic schemas for configuration structure

## Configuration Classes

| Class | Purpose |
|-------|---------|
| `AppConfig` | Root configuration container |
| `ServiceConfig` | Server host and port settings |
| `AgentConfig` | Agent definition with model, instructions, subagents |
| `OutputTypeConfig` | Structured output type definition |
| `OutputFieldConfig` | Field definition within output types |
| `WorkflowConfig` | Workflow graph configuration |
| `WorkflowNodeConfig` | Workflow node configuration |
| `WorkflowEdgeConfig` | Workflow edge configuration with optional conditions |

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
    output_type:               # Optional: structured output
      name: ResponseType
      fields:
        - name: answer
          type: str
          description: The response

workflows:
  - name: my-workflow
    start_node: step1_node
    nodes:
      - name: step1_node
        type: agent
        agent: agent-name
        description: First step in workflow
    edges:
      - from: step1_node
        to: __end__
        condition: "output.answer"  # Optional
```

## Usage

```python
from src.config import load_config

config = load_config()  # Loads config.yaml from project root
```
