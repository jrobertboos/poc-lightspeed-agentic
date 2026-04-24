# Models

Pydantic schemas for API request and response bodies.

## Modules

- `requests.py` - Inbound request schemas
- `responses.py` - Outbound response schemas

## Request Models

| Model | Endpoint | Purpose |
|-------|----------|---------|
| `AgentRunRequest` | `POST /agents/run` | Message and optional agent name |
| `WorkflowRunRequest` | `POST /workflows/run` | Message and optional workflow name |

## Response Models

| Model | Endpoint | Purpose |
|-------|----------|---------|
| `AgentListResponse` | `GET /agents` | List of all available agents |
| `AgentResponse` | `GET /agents/{agent_name}` | Single agent name and description |
| `AgentRunResponse` | `POST /agents/run` | Agent output, tool calls, and tool results |
| `ToolCall` | `POST /agents/run` | Tool invocation with name, ID, and arguments |
| `ToolResult` | `POST /agents/run` | Tool execution result with content and outcome |
| `WorkflowListResponse` | `GET /workflows` | List of all available workflows |
| `WorkflowResponse` | `GET /workflows/{workflow_name}` | Workflow details (name, description, nodes) |
| `WorkflowRunResponse` | `POST /workflows/run` | Workflow output and execution history |
| `HealthResponse` | `GET /health`, `GET /ready` | Service status and version |
| `ErrorResponse` | Error conditions | Error detail message |
