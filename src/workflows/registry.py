"""Workflow registry for managing and accessing configured workflows."""

from __future__ import annotations

from src.agents.registry import AgentRegistry
from src.config.models import AppConfig, WorkflowConfig
from src.log import get_logger
from src.workflows.factory import create_workflow
from src.workflows.workflow import Workflow

logger = get_logger(__name__)

_registry: "WorkflowRegistry | None" = None


class WorkflowRegistry:
    """Registry for storing and retrieving workflows by name."""

    def __init__(self, agent_registry: AgentRegistry) -> None:
        self._workflows: dict[str, Workflow] = {}
        self._agent_registry = agent_registry

    def register(self, config: WorkflowConfig) -> Workflow:
        """Create and register a workflow from configuration."""
        workflow = create_workflow(config, self._agent_registry)
        self._workflows[workflow.name] = workflow
        logger.debug(f"Created workflow '{workflow.name}'")
        return workflow

    def get(self, name: str) -> Workflow | None:
        """Retrieve a workflow by name, or None if not found."""
        return self._workflows.get(name)

    def list_workflows(self) -> list[str]:
        """Return a list of all registered workflow names."""
        return list(self._workflows.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._workflows


def initialize_registry(
    config: AppConfig,
    agent_registry: AgentRegistry,
) -> WorkflowRegistry:
    """Initialize the global workflow registry from configuration."""
    global _registry
    registry = WorkflowRegistry(agent_registry)

    if not config.workflows:
        logger.info("No workflow configurations found")
    else:
        for workflow_config in config.workflows:
            registry.register(workflow_config)

        workflow_names = ", ".join(registry.list_workflows())
        logger.info(f"Registered {len(registry.list_workflows())} workflows: {workflow_names}")

    _registry = registry
    return registry


def get_registry() -> WorkflowRegistry:
    """Get the global workflow registry, raising if not initialized."""
    if _registry is None:
        raise RuntimeError("Workflow registry not initialized. Call initialize_registry() first.")
    return _registry
