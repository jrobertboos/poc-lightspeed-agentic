"""Build pydantic-graph workflows from YAML configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_graph import End, Graph

from src.agents.registry import AgentRegistry
from src.config.models import WorkflowConfig
from src.log import get_logger
from src.workflows.nodes import AgentNode, create_node_class
from src.workflows.state import WorkflowState

if TYPE_CHECKING:
    from pydantic_ai import Agent

logger = get_logger(__name__)


class WorkflowDefinition:
    """A built workflow ready for execution."""

    def __init__(
        self,
        config: WorkflowConfig,
        graph: Graph[WorkflowState, str, None],
        start_node_class: type[AgentNode],
        node_classes: dict[str, type[AgentNode]],
    ):
        self.config = config
        self.graph = graph
        self.start_node_class = start_node_class
        self.node_classes = node_classes

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def description(self) -> str | None:
        return self.config.description


def build_workflow(
    config: WorkflowConfig,
    registry: AgentRegistry,
) -> WorkflowDefinition:
    """Build a workflow graph from configuration.

    Args:
        config: Workflow configuration from YAML
        registry: Agent registry containing the agents to use

    Returns:
        WorkflowDefinition ready for execution
    """
    logger.info(f"Building workflow '{config.name}'")

    node_classes: dict[str, type[AgentNode]] = {}

    for node_config in config.nodes:
        agent = registry.get(node_config.agent)
        if agent is None:
            raise ValueError(
                f"Workflow '{config.name}' references unknown agent '{node_config.agent}'"
            )

        node_class = create_node_class(
            agent=agent,
            node_id=node_config.agent,
            description=node_config.description,
        )
        node_classes[node_config.agent] = node_class
        logger.debug(f"Created node class for agent '{node_config.agent}'")

    _wire_edges(config, node_classes)

    graph = Graph[WorkflowState, str, None](
        nodes=list(node_classes.values()),
        name=config.name,
    )

    start_node_class = node_classes[config.start_node]

    logger.info(f"Workflow '{config.name}' built with {len(node_classes)} nodes")

    return WorkflowDefinition(
        config=config,
        graph=graph,
        start_node_class=start_node_class,
        node_classes=node_classes,
    )


def _wire_edges(
    config: WorkflowConfig,
    node_classes: dict[str, type[AgentNode]],
) -> None:
    """Wire up edges between node classes."""
    edges_by_source: dict[str, list[tuple[str, str | None]]] = {}

    for edge in config.edges:
        if edge.from_node not in edges_by_source:
            edges_by_source[edge.from_node] = []
        edges_by_source[edge.from_node].append((edge.to_node, edge.condition))

    for source_name, targets in edges_by_source.items():
        source_class = node_classes[source_name]
        source_class._conditional_edges = []

        default_target = None

        for target_name, condition in targets:
            target_class = End if target_name == "__end__" else node_classes[target_name]

            if condition:
                source_class._conditional_edges.append((condition, target_class))
            elif default_target is None:
                default_target = target_class

        source_class._default_next = default_target if default_target else End

        logger.debug(
            f"Wired edges for '{source_name}': "
            f"{len(source_class._conditional_edges)} conditional, default={default_target}"
        )
