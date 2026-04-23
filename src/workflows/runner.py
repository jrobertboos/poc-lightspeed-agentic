"""Workflow execution runner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from src.log import get_logger
from src.workflows.state import WorkflowState, create_initial_state

if TYPE_CHECKING:
    from src.workflows.builder import WorkflowDefinition

logger = get_logger(__name__)


def _serialize_output(output: Any) -> str:
    """Convert workflow output to string representation."""
    if isinstance(output, str):
        return output
    if isinstance(output, BaseModel):
        return output.model_dump_json()
    return str(output)


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""

    output: str
    state: WorkflowState
    success: bool = True
    error: str | None = None


class WorkflowRunner:
    """Executes workflow graphs."""

    def __init__(self, workflow: WorkflowDefinition):
        self.workflow = workflow

    async def run(self, user_input: str) -> WorkflowResult:
        """Execute the workflow with the given input."""
        logger.info(f"Starting workflow '{self.workflow.name}' with input: {user_input[:100]}...")

        state = create_initial_state(self.workflow.config, user_input)

        try:
            start_node = self.workflow.start_node_class()
            result = await self.workflow.graph.run(start_node, state=state)

            logger.info(f"Workflow '{self.workflow.name}' completed successfully")

            return WorkflowResult(
                output=_serialize_output(result.output),
                state=state,
                success=True,
            )

        except Exception as e:
            logger.error(f"Workflow '{self.workflow.name}' failed: {e}")
            return WorkflowResult(
                output="",
                state=state,
                success=False,
                error=str(e),
            )
