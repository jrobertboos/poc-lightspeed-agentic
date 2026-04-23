# Agents

Agent creation, lifecycle management, and structured output support using Pydantic AI.

## Modules

- `factory.py` - Creates `Agent` instances from `AgentConfig`, wiring up subagent delegation and structured output types
- `registry.py` - Singleton registry that holds all agents and resolves subagent references
- `output_types.py` - Dynamic Pydantic model generation for structured agent outputs
- `__init__.py` - Public API exports: `AgentRegistry`, `create_agent`, `get_registry`, `initialize_registry`

## How It Works

1. `initialize_registry(config)` is called at app startup with an `AppConfig` instance
2. Agents without subagents are registered first
3. Agents with subagents are registered second, resolving references from the registry
4. Subagents are attached as tools using Pydantic AI's multi-agent pattern
5. Structured output types are built dynamically from configuration

## Key Functions

### create_agent

Factory function that creates a Pydantic AI `Agent` from configuration. Supports:
- Standard Pydantic AI models (e.g., `openai:gpt-4o-mini`)
- LlamaStack models with prefix (e.g., `llama-stack:openai/gpt-4o-mini`)

### build_output_type

Dynamically generates Pydantic models from `OutputTypeConfig` for structured outputs.
Supported field types: `str`, `int`, `float`, `bool`, `list[T]`, `optional[T]`

## Multi-Agent Delegation

When an agent has subagents, each subagent becomes a callable tool:

```python
async def delegate_to_agent(ctx: RunContext[None], query: str) -> str:
    result = await delegate.run(query, usage=ctx.usage)
    return result.output
```

Token usage is accumulated across the delegation chain via `ctx.usage`.
