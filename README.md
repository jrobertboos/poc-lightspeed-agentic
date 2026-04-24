# Lightspeed Agentic

A no-code AI agent platform built with FastAPI and Pydantic AI. Define agents and workflows in YAML, deploy as an API.

## Features

- **YAML-based agent configuration** - Define agents, models, instructions, and structured outputs without code
- **Multi-agent orchestration** - Agents can delegate to subagents automatically
- **Graph-based workflows** - Define conditional workflows with pydantic-graph that route between agents based on output conditions
- **Structured outputs** - Define typed output schemas in YAML for validated, structured responses
- **Multiple model providers** - Support for OpenAI models and LlamaStack (with auto-configuration for multiple API providers)
- **FastAPI backend** - OpenAPI docs, async support, production-ready

## Quick Start

```bash
# Install dependencies
uv sync

# Set your API key
export OPENAI_API_KEY=your-key-here

# Run the server
uv run uvicorn src.main:app --reload

# Open API docs
open http://localhost:8000/docs
```

## Configuration

Agents and workflows are defined in `config.yaml`:

```yaml
name: Lightspeed Agentic
service:
  host: 0.0.0.0
  port: 8000

agents:
  - name: content_reviewer
    description: Reviews content and decides if it needs revision
    model: openai:gpt-4o-mini
    output_type:
      name: ContentReview
      fields:
        - name: approved
          type: bool
          description: Whether the content is ready
        - name: quality_score
          type: int
          description: Quality score from 1-10
    instructions: |
      You are a content reviewer...

  - name: content_improver
    description: Improves content based on feedback
    model: openai:gpt-4o-mini
    instructions: |
      You are a content improvement specialist...

workflows:
  - name: content_pipeline
    description: Review, improve, and publish content
    start_node: content_reviewer_node

    nodes:
      - name: content_reviewer_node
        type: agent
        agent: content_reviewer
      - name: content_improver_node
        type: agent
        agent: content_improver
      - name: publisher_node
        type: agent
        agent: publisher

    edges:
      - from: content_reviewer_node
        to: publisher_node
        condition: "output.approved"
      - from: content_reviewer_node
        to: content_improver_node  # Default if not approved
      - from: content_improver_node
        to: content_reviewer_node
      - from: publisher_node
        to: __end__
```

## API Usage

### Run an agent

```bash
curl -X POST http://localhost:8000/agents/run \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "content_reviewer", "message": "Review this article..."}'
```

### Run a workflow

```bash
curl -X POST http://localhost:8000/workflows/run \
  -H "Content-Type: application/json" \
  -d '{"workflow_name": "content_pipeline", "message": "Please review and publish this content..."}'
```

### List available workflows

```bash
curl http://localhost:8000/workflows
```

### List available agents

```bash
curl http://localhost:8000/agents
```

## Project Structure

```
src/
├── agents/          # Agent factory, registry, and output type builder
├── app/             # FastAPI app and endpoints
│   └── endpoints/   # API route handlers (query, workflows, agents, health)
├── config/          # YAML config loader and models
├── models/          # Request/response schemas
├── providers/       # Model providers (LlamaStack integration)
├── workflows/       # Graph-based workflow builder and runner
└── main.py          # Application entry point
```

## Model Providers

### OpenAI (default)
Use standard Pydantic AI model strings:
```yaml
model: openai:gpt-4o-mini
```

### LlamaStack
Use the `llama-stack:` prefix for LlamaStack models:
```yaml
model: llama-stack:openai/gpt-4o-mini
```

LlamaStack runs as an in-process library and automatically picks up API keys from environment variables (OPENAI_API_KEY, ANTHROPIC_API_KEY, TOGETHER_API_KEY, etc.).

## Requirements

- Python 3.12+
- API key for your chosen model provider (e.g., `OPENAI_API_KEY` environment variable)
