"""Workflow registry for managing and accessing configured workflows."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.agents.registry import AgentRegistry
from src.config.models import AppConfig
from src.log import get_logger
from src.workflows.builder import WorkflowDefinition, build_workflow
from src.workflows.runner import WorkflowRunner

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)

_registry: "WorkflowRegistry | None" = None


class WorkflowRegistry:
    """Registry for storing and retrieving workflows by name."""

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowDefinition] = {}
        self._runners: dict[str, WorkflowRunner] = {}

    def register(self, workflow: WorkflowDefinition) -> None:
        """Register a workflow definition."""
        self._workflows[workflow.name] = workflow
        self._runners[workflow.name] = WorkflowRunner(workflow)
        logger.info(f"Registered workflow: {workflow.name}")

    def get(self, name: str) -> WorkflowDefinition | None:
        """Retrieve a workflow definition by name."""
        return self._workflows.get(name)

    def get_runner(self, name: str) -> WorkflowRunner | None:
        """Retrieve a workflow runner by name."""
        return self._runners.get(name)

    def list_workflows(self) -> list[str]:
        """Return a list of all registered workflow names."""
        return list(self._workflows.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._workflows


def initialize_workflow_registry(
    config: AppConfig,
    agent_registry: AgentRegistry,
) -> WorkflowRegistry | None:
    """Initialize the global workflow registry from configuration."""
    global _registry

    if not config.workflows:
        logger.info("No workflow configurations found")
        return None

    registry = WorkflowRegistry()

    for workflow_config in config.workflows:
        workflow_def = build_workflow(workflow_config, agent_registry)
        registry.register(workflow_def)

    _registry = registry
    return registry


def get_workflow_registry() -> WorkflowRegistry | None:
    """Get the global workflow registry, or None if not initialized."""
    return _registry
