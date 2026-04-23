"""Workflow state for tracking execution."""

from dataclasses import dataclass, field
from typing import Any

from src.config.models import WorkflowConfig


@dataclass
class WorkflowState:
    """State passed between workflow nodes."""

    input: str = ""
    output: Any = ""
    current_node: str = ""
    history: list[dict[str, Any]] = field(default_factory=list)


def create_initial_state(config: WorkflowConfig, user_input: str) -> WorkflowState:
    """Create initial workflow state."""
    return WorkflowState(
        input=user_input,
        current_node=config.start_node,
    )
