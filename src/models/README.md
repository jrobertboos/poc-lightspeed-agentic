# Models

Pydantic schemas for API request and response bodies.

## Modules

- `requests.py` - Inbound request schemas
- `responses.py` - Outbound response schemas

## Request Models

| Model | Endpoint | Purpose |
|-------|----------|---------|
| `QueryRequest` | `POST /query` | User message and target agent name |

## Response Models

| Model | Endpoint | Purpose |
|-------|----------|---------|
| `QueryResponse` | `POST /query` | Agent response text and agent name |
| `AgentListResponse` | `GET /agents` | List of all available agents |
| `AgentResponse` | `GET /agents/{agent_name}` | Single agent name and description |
| `HealthResponse` | `GET /health`, `GET /ready` | Service status and version |
| `ErrorResponse` | Error conditions | Error detail message |
