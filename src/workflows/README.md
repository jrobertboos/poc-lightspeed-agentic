# Workflows

Graph-based workflow orchestration using pydantic-graph. Workflows define directed graphs where nodes execute agents and edges determine routing based on conditions.

## Modules

- `builder.py` - Builds pydantic-graph workflows from YAML configuration
- `runner.py` - Executes workflow graphs and returns results
- `nodes.py` - `AgentNode` class that wraps agents as pydantic-graph nodes
- `state.py` - `WorkflowState` dataclass for tracking execution
- `registry.py` - Global registry for workflow definitions and runners

## How It Works

1. `initialize_workflow_registry(config, agent_registry)` is called at app startup
2. Each workflow config is passed to `build_workflow()` which:
   - Creates `AgentNode` subclasses for each node referencing agents from the registry
   - Wires conditional edges between nodes based on YAML config
   - Returns a `WorkflowDefinition` with the compiled graph
3. `WorkflowRunner.run(input)` executes the graph:
   - Creates initial `WorkflowState` with user input
   - Starts at the `start_node` and executes agents
   - Evaluates edge conditions to determine routing
   - Returns `WorkflowResult` with final output and execution history

## Key Classes

### WorkflowDefinition

A built workflow ready for execution. Contains the compiled graph, start node class, and configuration.

### WorkflowRunner

Executes a workflow with a given input string. Returns a `WorkflowResult` with output, state, and success status.

### WorkflowState

State passed between nodes during execution:

| Field | Type | Purpose |
|-------|------|---------|
| `input` | `str` | Original user input |
| `output` | `Any` | Current output (from last node) |
| `current_node` | `str` | Name of current node |
| `history` | `list[dict]` | Execution history with node outputs |

### AgentNode

Base class for workflow nodes. Each node:
- Builds a prompt with full workflow context (input + history)
- Executes its assigned agent
- Evaluates conditional edges to determine next node

## Conditional Routing

Edges can have conditions that reference the current output and state:

```yaml
edges:
  - from: reviewer
    to: publisher
    condition: "output.approved and output.score >= 8"
  - from: reviewer
    to: improver
    condition: "not output.approved"
  - from: reviewer
    to: __end__  # Default fallback (no condition)
```

Available in condition expressions: `output`, `state`, `history`, `input`, `len`, `any`, `all`

## Usage

```python
from src.workflows import get_workflow_registry

registry = get_workflow_registry()
runner = registry.get_runner("my-workflow")
result = await runner.run("Process this input")

print(result.output)
print(result.state.history)
```
