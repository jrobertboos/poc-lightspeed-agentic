# Agents

Agent creation and lifecycle management using Pydantic AI.

## Modules

- `factory.py` - Creates `Agent` instances from `AgentConfig`, wiring up subagent delegation
- `registry.py` - Singleton registry that holds all agents and resolves subagent references

## How It Works

1. `initialize_registry()` is called at app startup
2. Agents without subagents are registered first
3. Agents with subagents are registered second, resolving references from the registry
4. Subagents are attached as tools using Pydantic AI's multi-agent pattern

## Multi-Agent Delegation

When an agent has subagents, each subagent becomes a callable tool:

```python
async def delegate_to_agent(ctx: RunContext[None], query: str) -> str:
    result = await delegate.run(query, usage=ctx.usage)
    return result.output
```

Token usage is accumulated across the delegation chain via `ctx.usage`.
