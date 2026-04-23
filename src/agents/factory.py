"""Agent factory for creating Pydantic AI agents from configuration."""

from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model

from src.config.models import AgentConfig
from src.log import get_logger
from src.providers import LlamaStackModel

logger = get_logger(__name__)

LLAMA_STACK_PREFIX = "llama-stack:"


def _create_model(model_str: str) -> Model | str:
    """Create a model from a model string.

    Supports:
    - Standard Pydantic AI model strings (e.g., "openai:gpt-4o-mini")
    - LlamaStack models with prefix (e.g., "llama-stack:openai/gpt-4o-mini")
    """
    if model_str.startswith(LLAMA_STACK_PREFIX):
        model_id = model_str[len(LLAMA_STACK_PREFIX):]
        logger.info(f"Creating LlamaStack model: {model_id}")
        return LlamaStackModel(model_id=model_id, distro="starter")
    return model_str


def create_agent(
    config: AgentConfig,
    subagents: list[Agent[None, str]] | None = None,
) -> Agent[None, str]:
    """Create an agent from configuration with optional subagent delegation.

    Subagents are registered as tools following Pydantic AI's multi-agent pattern:
    https://pydantic.dev/docs/ai/guides/multi-agent-applications/
    """
    model = _create_model(config.model)

    agent: Agent[None, str] = Agent(
        model=model,
        instructions=config.instructions or None,
        name=config.name,
        description=config.description or None,
    )

    if subagents:
        for subagent in subagents:
            _register_delegate_tool(agent, subagent)

    return agent


def _register_delegate_tool(
    parent: Agent[None, str],
    delegate: Agent[None, str],
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

    delegate_to_agent.__name__ = delegate.name or "delegate"
    delegate_to_agent.__doc__ = delegate.description or f"Delegate task to {delegate.name}"

    parent.tool()(delegate_to_agent)
