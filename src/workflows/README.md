# Workflows

Graph-based workflow orchestration using pydantic-graph. Workflows define directed graphs where nodes execute agents and edges determine routing based on conditions.

## Modules

- `factory.py` - Creates workflows from YAML configuration
- `workflow.py` - `Workflow` class that executes graphs and returns results
- `nodes.py` - `WorkflowNode` base class and `AgentNode` subclass for pydantic-graph nodes
- `state.py` - `WorkflowState` dataclass for tracking execution
- `registry.py` - Global registry for workflows

## How It Works

1. `initialize_registry(config, agent_registry)` is called at app startup
2. Each workflow config is passed to `create_workflow()` which:
   - Creates `AgentNode` subclasses for each node referencing agents from the registry
   - Wires conditional edges between nodes based on YAML config
   - Returns a `Workflow` with the compiled graph
3. `Workflow.run(input)` executes the graph:
   - Creates initial `WorkflowState` with user input
   - Starts at the `start_node` and executes agents
   - Evaluates edge conditions to determine routing
   - Returns `WorkflowRunResult` with final output and state

## Key Classes

### Workflow

A workflow that orchestrates agents through a graph. Contains the compiled graph, start node class, and configuration. Call `run(input)` to execute and get a `WorkflowRunResult`.

### WorkflowRunResult

Result of a workflow execution containing `output` (string) and `state` (WorkflowState).

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
  - from: reviewer_node
    to: publisher_node
    condition: "output.approved and output.score >= 8"
  - from: reviewer_node
    to: improver_node
    condition: "not output.approved"
  - from: reviewer_node
    to: __end__  # Default fallback (no condition)
```

Available in condition expressions: `output`, `state`, `history`, `input`, `len`, `any`, `all`

## Usage

```python
from src.workflows import get_registry

registry = get_registry()
workflow = registry.get("my-workflow")
result = await workflow.run("Process this input")

print(result.output)
print(result.state.history)
```
