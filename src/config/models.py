"""Pydantic configuration models for application settings."""

from pydantic import BaseModel, Field, model_validator


class ServiceConfig(BaseModel):
    """HTTP server configuration."""
    host: str = "0.0.0.0"
    port: int = 8080


class OutputFieldConfig(BaseModel):
    """Configuration for a field in an output type."""

    name: str = Field(..., description="Field name")
    type: str = Field(default="str", description="Field type (str, int, float, bool, list[T], etc.)")
    description: str | None = Field(None, description="Field description for the LLM")
    required: bool = Field(default=True, description="Whether the field is required")


class OutputTypeConfig(BaseModel):
    """Configuration for a structured output type."""

    name: str = Field(..., description="Name of the generated Pydantic model")
    description: str | None = Field(None, description="Description of the output type")
    fields: list[OutputFieldConfig] = Field(..., description="Fields in the output type")


class AgentConfig(BaseModel):
    """Configuration for a single AI agent."""

    name: str
    description: str = ""
    model: str = Field(default="openai:gpt-4o-mini")
    instructions: str | None = None
    subagents: list[str] = Field(default_factory=list)
    output_type: OutputTypeConfig | None = Field(None, description="Structured output type")


class WorkflowNodeConfig(BaseModel):
    """Configuration for a node in a workflow graph."""

    agent: str = Field(..., description="Name of the agent to use for this node")
    description: str | None = Field(None, description="Description of what this node does")


class WorkflowEdgeConfig(BaseModel):
    """Configuration for an edge between workflow nodes."""

    from_node: str = Field(..., alias="from", description="Source node (agent name)")
    to_node: str = Field(..., alias="to", description="Target node (agent name or '__end__')")
    label: str | None = Field(None, description="Optional label describing the transition")
    condition: str | None = Field(None, description="Optional condition expression for this edge")

    model_config = {"populate_by_name": True}


class WorkflowConfig(BaseModel):
    """Configuration for a workflow graph using agents as nodes."""

    name: str = Field(..., description="Unique workflow identifier")
    description: str | None = Field(None, description="Workflow description")
    start_node: str = Field(..., description="Initial node to start execution")
    nodes: list[WorkflowNodeConfig] = Field(..., description="Nodes in the workflow")
    edges: list[WorkflowEdgeConfig] = Field(..., description="Edges defining transitions")

    @model_validator(mode="after")
    def validate_workflow(self) -> "WorkflowConfig":
        """Validate workflow structure."""
        node_names = {n.agent for n in self.nodes}

        if self.start_node not in node_names:
            raise ValueError(f"start_node '{self.start_node}' is not defined in nodes")

        for edge in self.edges:
            if edge.from_node not in node_names:
                raise ValueError(f"Edge 'from' node '{edge.from_node}' is not defined in nodes")
            if edge.to_node != "__end__" and edge.to_node not in node_names:
                raise ValueError(f"Edge 'to' node '{edge.to_node}' is not defined in nodes")

        return self


class AppConfig(BaseModel):
    """Root application configuration."""

    name: str = "Lightspeed Agentic"
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    agents: list[AgentConfig] = Field(default_factory=list)
    workflows: list[WorkflowConfig] = Field(default_factory=list, description="Workflow configurations")
