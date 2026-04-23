"""Agent registry for managing and accessing configured agents."""

from typing import Any

from pydantic_ai import Agent

from src.agents.factory import create_agent
from src.config.models import AgentConfig, AppConfig

_registry: "AgentRegistry | None" = None


class AgentRegistry:
    """Registry for storing and retrieving AI agents by name."""
    def __init__(self) -> None:
        self._agents: dict[str, Agent[None, Any]] = {}

    def register(
        self,
        agent_config: AgentConfig,
        subagents: list[Agent[None, Any]] | None = None,
    ) -> Agent[None, Any]:
        """Create and register an agent from configuration."""
        agent = create_agent(agent_config, subagents=subagents)
        self._agents[agent_config.name] = agent
        return agent

    def get(self, name: str) -> Agent[None, Any] | None:
        """Retrieve an agent by name, or None if not found."""
        return self._agents.get(name)

    def list_agents(self) -> list[str]:
        """Return a list of all registered agent names."""
        return list(self._agents.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._agents


def initialize_registry(config: AppConfig) -> AgentRegistry:
    """Initialize the global registry with agents from configuration."""
    global _registry
    registry = AgentRegistry()

    configs_with_subagents: list[AgentConfig] = []
    for agent_config in config.agents:
        if agent_config.subagents:
            configs_with_subagents.append(agent_config)
        else:
            registry.register(agent_config)

    for agent_config in configs_with_subagents:
        subagents: list[Agent[None, Any]] = []
        for subagent_name in agent_config.subagents:
            subagent = registry.get(subagent_name)
            if subagent is None:
                raise ValueError(
                    f"Agent '{agent_config.name}' references unknown subagent '{subagent_name}'"
                )
            subagents.append(subagent)
        registry.register(agent_config, subagents=subagents)

    _registry = registry
    return registry


def get_registry() -> AgentRegistry:
    """Get the global agent registry, raising if not initialized."""
    if _registry is None:
        raise RuntimeError("Agent registry not initialized. Call initialize_registry() first.")
    return _registry
