# Models

Pydantic schemas for API request and response bodies.

## Modules

- `requests.py` - Inbound request schemas
- `responses.py` - Outbound response schemas

## Request Models

| Model | Endpoint | Purpose |
|-------|----------|---------|
| `QueryRequest` | `POST /query` | Message, agent name, streaming flag |

## Response Models

| Model | Purpose |
|-------|---------|
| `QueryResponse` | Agent response text and agent name |
| `AgentResponse` | Agent name and description |
| `HealthResponse` | Service status and version |
