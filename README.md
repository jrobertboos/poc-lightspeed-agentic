# Lightspeed Agentic

A no-code AI agent platform built with FastAPI and Pydantic AI. Define agents in YAML, deploy as an API.

## Features

- **YAML-based agent configuration** - Define agents, models, and instructions without code
- **Multi-agent orchestration** - Agents can delegate to subagents automatically
- **Streaming responses** - Server-sent events for real-time output
- **FastAPI backend** - OpenAPI docs, async support, production-ready

## Quick Start

```bash
# Install dependencies
uv sync

# Run the server
uv run uvicorn src.main:app --reload

# Open API docs
open http://localhost:8000/docs
```

## Configuration

Agents are defined in `config.yaml`:

```yaml
name: Lightspeed Agentic
service:
  host: 0.0.0.0
  port: 8080

agents:
  - name: researcher
    description: Researches topics and provides detailed information
    model: openai:gpt-4o-mini
    instructions: |
      You are a research specialist...

  - name: root
    description: Routes requests to specialized sub-agents
    model: openai:gpt-4o-mini
    subagents: [researcher]
    instructions: |
      You are the orchestration agent...
```

## API Usage

### Query an agent

```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "root", "message": "What is quantum computing?"}'
```

### Stream response

```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "root", "message": "Explain AI", "stream": true}'
```

## Project Structure

```
src/
├── agents/          # Agent factory and registry
├── app/             # FastAPI app and endpoints
├── config/          # YAML config loader and models
├── models/          # Request/response schemas
└── main.py          # Application entry point
```

## Requirements

- Python 3.12+
- OpenAI API key (set `OPENAI_API_KEY` environment variable)
