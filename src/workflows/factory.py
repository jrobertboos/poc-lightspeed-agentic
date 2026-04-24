"""Workflow factory for creating pydantic-graph workflows from configuration."""

from __future__ import annotations

from pydantic_graph import End, Graph

from src.agents.registry import AgentRegistry
from src.config.models import WorkflowConfig
from src.log import get_logger
from src.workflows.nodes import AgentNode, create_agent_node_class
from src.workflows.state import WorkflowState
from src.workflows.workflow import Workflow

logger = get_logger(__name__)


def create_workflow(
    config: WorkflowConfig,
    registry: AgentRegistry,
) -> Workflow:
    """Create a workflow from configuration.

    Args:
        config: Workflow configuration from YAML
        registry: Agent registry containing the agents to use

    Returns:
        Workflow ready for execution
    """
    logger.debug(f"Creating workflow '{config.name}'")

    node_classes: dict[str, type[AgentNode]] = {}

    for node_config in config.nodes:
        if node_config.type == "agent":
            if not node_config.agent:
                raise ValueError(
                    f"Workflow '{config.name}' node '{node_config.name}' requires 'agent' field"
                )
            agent = registry.get(node_config.agent)
            if agent is None:
                raise ValueError(
                    f"Workflow '{config.name}' node '{node_config.name}' references unknown agent '{node_config.agent}'"
                )

            node_class = create_agent_node_class(
                agent=agent,
                node_id=node_config.name,
                name=node_config.name,
                description=node_config.description,
            )
        else:
            raise ValueError(f"Unknown node type '{node_config.type}' for node '{node_config.name}'")

        node_classes[node_config.name] = node_class
        logger.debug(f"Created {node_config.type} node '{node_config.name}'")

    _wire_edges(config, node_classes)

    graph = Graph[WorkflowState, str, None](
        nodes=list(node_classes.values()),
        name=config.name,
    )

    start_node_class = node_classes[config.start_node]
    logger.debug(f"Workflow '{config.name}' created with {len(node_classes)} nodes")

    return Workflow(
        config=config,
        graph=graph,
        start_node_class=start_node_class,
        node_classes=node_classes,
    )


def _wire_edges(
    config: WorkflowConfig,
    node_classes: dict[str, type[AgentNode]],
) -> None:
    """Wire edges between node classes."""
    edges_by_source: dict[str, list[tuple[str, str | None]]] = {}

    for edge in config.edges:
        if edge.from_node not in edges_by_source:
            edges_by_source[edge.from_node] = []
        edges_by_source[edge.from_node].append((edge.to_node, edge.condition))

    for source_name, targets in edges_by_source.items():
        source_class = node_classes[source_name]
        conditional_edges: list[tuple[str, type]] = []
        default_target = None

        for target_name, condition in targets:
            target_class = End if target_name == "__end__" else node_classes[target_name]

            if condition:
                conditional_edges.append((condition, target_class))
            elif default_target is None:
                default_target = target_class

        source_class._conditional_edges = conditional_edges
        source_class._default_next = default_target if default_target else End

        logger.debug(
            f"Wired edges for '{source_name}': "
            f"{len(conditional_edges)} conditional, default={default_target}"
        )
