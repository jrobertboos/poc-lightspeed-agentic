# Source Code

Core application code for Lightspeed Agentic, a no-code platform for building AI agents and workflows from YAML configuration.

## Structure

| Directory | Purpose |
|-----------|---------|
| `agents/` | Agent creation, registry, and structured output types |
| `app/` | FastAPI application, routing, and API endpoints |
| `capabilities/` | Reserved for agent capability extensions (currently empty) |
| `config/` | YAML configuration loading and Pydantic config models |
| `models/` | Pydantic request/response schemas for API payloads |
| `providers/` | Custom LLM model providers (LlamaStack integration) |
| `runners/` | Server execution utilities (uvicorn) |
| `utils/` | Shared utility functions (currently empty) |
| `workflows/` | Graph-based workflow orchestration using pydantic-graph |

## Key Files

- `main.py` - FastAPI application instance with lifespan management; initializes agent registry, workflow registry, and configuration on startup
- `log.py` - Logging utilities with Rich console formatting and TTY detection
- `constants.py` - Application constants (log format, log level)

## Module Details

### agents/

- `factory.py` - Creates Pydantic AI agents from configuration; supports standard models and LlamaStack models (prefixed with `llama-stack:`); handles subagent delegation as tools
- `registry.py` - Global agent registry for storing and retrieving agents by name; handles initialization order for agents with subagent dependencies
- `output_types.py` - Dynamic Pydantic model generation from YAML config for structured agent outputs

### app/

- `routers.py` - Registers all API routers with the FastAPI application
- `endpoints/` - API endpoint modules:
  - `health.py` - Health and readiness check endpoints (`/health`, `/ready`)
  - `query.py` - Not implemented
  - `agents.py` - Agent listing, retrieval, and execution (`GET /agents`, `GET /agents/{name}`, `POST /agents/run`)
  - `workflows.py` - Workflow listing and execution (`GET /workflows`, `GET /workflows/{name}`, `POST /workflows/run`)

### config/

- `loader.py` - Loads and validates YAML configuration files into Pydantic models
- `models.py` - Pydantic configuration models: `AppConfig`, `AgentConfig`, `WorkflowConfig`, `OutputTypeConfig`, etc.

### models/

- `requests.py` - API request payload schemas (`AgentRunRequest`, `WorkflowRunRequest`)
- `responses.py` - API response schemas (`HealthResponse`, `AgentResponse`, `AgentListResponse`, `AgentRunResponse`, `WorkflowResponse`, `WorkflowListResponse`, `WorkflowRunResponse`, `ErrorResponse`)

### providers/

- `llama_stack.py` - Custom Pydantic AI model provider for LlamaStack; runs LlamaStack as an in-process library via `AsyncLlamaStackAsLibraryClient`; handles message mapping, tool definitions, and structured output

### workflows/

- `registry.py` - Global workflow registry for storing and retrieving workflows by name
- `factory.py` - Creates workflows from YAML configuration; creates node classes and wires conditional edges
- `workflow.py` - `Workflow` class that orchestrates agents through a graph; returns `WorkflowRunResult` with output and state
- `nodes.py` - `WorkflowNode` base class and `AgentNode` subclass that wrap agents as pydantic-graph nodes; handles prompt building with workflow context and conditional edge routing
- `state.py` - `WorkflowState` dataclass for tracking workflow execution (input, output, history, current node)

### runners/

- `uvicorn.py` - Development/production server runner using uvicorn
