"""Workflow node definitions for pydantic-graph."""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_graph import BaseNode, End, GraphRunContext

from src.log import get_logger
from src.workflows.state import WorkflowState


logger = get_logger(__name__)

def serialize_output(output: Any) -> str:
    """Serialize agent output to string for downstream nodes."""
    if isinstance(output, str):
        return output
    if isinstance(output, BaseModel):
        return output.model_dump_json(indent=2)
    return str(output)


def evaluate_condition(condition: str, context: dict[str, Any]) -> bool:
    """Evaluate a condition expression against context.

    Available in expressions: output, state, history, input, len, any, all
    """
    safe_builtins = {"len": len, "any": any, "all": all, "True": True, "False": False}
    try:
        return bool(eval(condition, {"__builtins__": safe_builtins}, context))
    except Exception as e:
        logger.warning(f"Condition '{condition}' failed: {e}")
        return False


@dataclass
class WorkflowNode(BaseNode[WorkflowState]):
    """Base class for all workflow nodes."""

    _name: ClassVar[str]
    _node_id: ClassVar[str]
    _description: ClassVar[str | None]
    _conditional_edges: ClassVar[list[tuple[str, type[BaseNode[WorkflowState]] | type[End]]]]
    _default_next: ClassVar[type[BaseNode[WorkflowState]] | type[End] | None]

    @abstractmethod
    async def run(
        self, ctx: GraphRunContext[WorkflowState]
    ) -> BaseNode[WorkflowState] | End[Any]:
        """Execute the node and determine the next node."""
        ...

    def _resolve_next_node(
        self, output: Any, state: WorkflowState
    ) -> type[BaseNode[WorkflowState]] | type[End] | None:
        """Evaluate conditional edges and return the first matching target."""
        context = {
            "output": output,
            "state": state,
            "history": state.history,
            "input": state.input,
        }

        for condition, target in self._conditional_edges:
            if evaluate_condition(condition, context):
                logger.debug(f"Condition '{condition}' matched, routing to {target}")
                return target

        return self._default_next

    def _record_output(self, state: WorkflowState, output: Any, output_text: str, **extra: Any) -> None:
        """Record node execution to workflow history."""
        entry = {
            "node": self._node_id,
            "output": output,
            "output_text": output_text,
            **extra,
        }
        state.history.append(entry)
        state.output = output
        state.current_node = self._node_id


@dataclass
class AgentNode(WorkflowNode):
    """A workflow node that executes an agent."""

    _agent: ClassVar[Agent[None, Any]]

    async def run(
        self, ctx: GraphRunContext[WorkflowState]
    ) -> BaseNode[WorkflowState] | End[Any]:
        """Execute the agent and determine the next node."""
        state = ctx.state
        prompt = self._build_prompt(state)

        logger.info(f"Executing node '{self._node_id}' with agent '{self._agent.name}'")
        result = await self._agent.run(prompt)
        output = result.output
        output_text = serialize_output(output)

        self._record_output(state, output, output_text, agent=self._agent.name)

        logger.debug(f"Node '{self._node_id}' completed, output length: {len(output_text)}")

        next_node = self._resolve_next_node(output, state)

        if next_node is None or next_node is End:
            return End(output)

        return next_node()

    def _build_prompt(self, state: WorkflowState) -> str:
        """Build prompt with full workflow context."""
        if not state.history:
            return state.input

        parts = [f"## Original Input\n{state.input}"]

        parts.append("\n## Workflow History")
        for i, entry in enumerate(state.history, 1):
            node = entry.get("node", "unknown")
            output_text = entry.get("output_text", "")
            parts.append(f"\n### Step {i}: {node}\n{output_text}")

        parts.append("\n## Your Task")
        parts.append(f"You are the '{self._node_id}' agent. Process the above and produce your output.")

        return "\n".join(parts)


def create_agent_node_class(
    agent: Agent[None, Any],
    node_id: str,
    name: str,
    description: str | None = None,
) -> type[AgentNode]:
    """Create a node class for a specific agent."""
    class_name = node_id.title().replace('_', '')

    node_class = type(
        class_name,
        (AgentNode,),
        {
            "__module__": __name__,
            "__doc__": f"Node executing agent: {agent.name}",
            "_name": name,
            "_agent": agent,
            "_node_id": node_id,
            "_description": description or agent.description,
            "_conditional_edges": [],
            "_default_next": None,
        },
    )

    return node_class
