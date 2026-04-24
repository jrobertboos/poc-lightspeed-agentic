"""Workflow class for graph-based agent orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic_graph import Graph

from src.config.models import WorkflowConfig
from src.log import get_logger
from src.workflows.nodes import AgentNode, serialize_output
from src.workflows.state import WorkflowState, create_initial_state

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


@dataclass
class WorkflowRunResult:
    """Result of a workflow execution."""

    output: str
    state: WorkflowState
    success: bool = True
    error: str | None = None


class Workflow:
    """A workflow that orchestrates agents through a graph."""

    def __init__(
        self,
        config: WorkflowConfig,
        graph: Graph[WorkflowState, str, None],
        start_node_class: type[AgentNode],
        node_classes: dict[str, type[AgentNode]],
    ):
        self._config = config
        self._graph = graph
        self._start_node_class = start_node_class
        self._node_classes = node_classes

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def description(self) -> str | None:
        return self._config.description

    @property
    def start_node(self) -> str:
        return self._config.start_node

    @property
    def nodes(self) -> list[str]:
        return [n.agent for n in self._config.nodes]

    async def run(self, user_input: str) -> WorkflowRunResult:
        """Execute the workflow with the given input."""
        logger.info(f"Starting workflow '{self.name}' with input: {user_input[:100]}...")

        state = create_initial_state(self._config, user_input)

        try:
            start_node = self._start_node_class()
            result = await self._graph.run(start_node, state=state)

            logger.info(f"Workflow '{self.name}' completed successfully")

            return WorkflowRunResult(
                output=serialize_output(result.output),
                state=state,
                success=True,
            )

        except Exception as e:
            logger.error(f"Workflow '{self.name}' failed: {e}")
            return WorkflowRunResult(
                output="",
                state=state,
                success=False,
                error=str(e),
            )
