"""Agent factory for creating Pydantic AI agents from configuration."""

from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model

from src.agents.output_types import build_output_type
from src.config.models import AgentConfig
from src.log import get_logger
from src.providers import LlamaStackModel

logger = get_logger(__name__)
output_logger = get_logger("agent.output")

LLAMA_STACK_PREFIX = "llama-stack:"


def _create_model(model_str: str) -> Model | str:
    """Create a model from a model string.

    Supports:
    - Standard Pydantic AI model strings (e.g., "openai:gpt-4o-mini")
    - LlamaStack models with prefix (e.g., "llama-stack:openai/gpt-4o-mini")
    """
    if model_str.startswith(LLAMA_STACK_PREFIX):
        model_id = model_str[len(LLAMA_STACK_PREFIX):]
        return LlamaStackModel(model_id=model_id, distro="starter")
    return model_str


def create_agent(
    config: AgentConfig,
    subagents: list[Agent[None, Any]] | None = None,
) -> Agent[None, Any]:
    """Create an agent from configuration with optional subagent delegation.

    Subagents are registered as tools following Pydantic AI's multi-agent pattern:
    https://pydantic.dev/docs/ai/guides/multi-agent-applications/
    """
    model = _create_model(config.model)

    output_type: type = str
    if config.output_type:
        output_type = build_output_type(config.output_type)

    agent: Agent[None, Any] = Agent(
        model=model,
        instructions=config.instructions or None,
        name=config.name,
        description=config.description or None,
        output_type=output_type,
    )

    _instrument_agent(agent)

    if subagents:
        for subagent in subagents:
            _register_delegate_tool(agent, subagent)

    return agent


def _instrument_agent(agent: Agent[None, Any]) -> None:
    """Add logging instrumentation to an agent."""

    @agent.output_validator
    def log_output(output: Any) -> Any:
        agent_name = agent.name or "unknown"

        if isinstance(output, BaseModel):
            output_str = output.model_dump_json(indent=2)
        else:
            output_str = str(output)

        output_logger.debug(f"[{agent_name}] output:\n{output_str}")
        return output


def _register_delegate_tool(
    parent: Agent[None, Any],
    delegate: Agent[None, Any],
) -> None:
    """Register a delegate agent as a tool on the parent agent.

    Follows Pydantic AI delegation pattern:
    - Passes ctx.usage to accumulate token counts across the delegation chain
    - Returns delegate output back to the parent for continued processing
    """

    async def delegate_to_agent(ctx: RunContext[None], query: str) -> str:
        logger.debug(f"Delegating: {parent.name} -> {delegate.name} | query: {query}")
        result = await delegate.run(query, usage=ctx.usage)
        logger.debug(f"Delegation complete: {delegate.name} -> {parent.name}")
        return result.output

    tool_name = delegate.name or "delegate"
    tool_description = delegate.description or f"Delegate task to {delegate.name}"

    parent.tool(name=tool_name, description=tool_description)(delegate_to_agent)
