# Lightspeed Agentic POC

## A No-Code AI Agent Platform

---

## What Is Lightspeed Agentic?

A **no-code AI agent platform** built with:

- **FastAPI** - Production-ready async API
- **Pydantic AI** - Type-safe agent framework

**Define agents and workflows in YAML, deploy as an API.**

### Key Features

| Feature | Description |
|---------|-------------|
| YAML-based configuration | Define agents and workflows without code |
| AI agents | Instructions, subagents, structured outputs |
| Graph-based workflows | Conditional routing between agents |
| Multiple model providers | OpenAI + LlamaStack (multi-provider support) |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STARTUP: config.yaml ──▶ AgentRegistry ──▶ WorkflowRegistry ──▶ FastAPI    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  RUNTIME                                                                    │
│                                                                             │
│  ┌─────────┐                                                                │
│  │ Client  │                                                                │
│  └────┬────┘                                                                │
│       │                                                                     │
│       ├──── /agents/run ────▶ AgentRegistry ──▶ Agent ───────────────┐      │
│       │                              │            │                  │      │
│       │                              │            │ delegates to     │      │
│       │                              │            ▼ subagents        │      │
│       │                              │         ┌───────────┐         │      │
│       │                              └────────▶│ Subagent  │─────────┤      │
│       │                            (as tools)  └───────────┘         │      │
│       │                                                              ▼      │
│       │                                                     ┌─────────────┐ │
│       │                                                     │   Model     │ │
│       └──── /workflows/run ──▶ Workflow                     │  Providers  │ │
│                                      │                      │             │ │
│             ┌────────────────────────┘                      │ Any Pydantic│ │
│             │                                               │ AI provider:│ │
│             ▼                                               │  - OpenAI   │ │
│  ┌─────────────────────────────────────────────────┐        │  - Anthropic│ │
│  │  Workflow Graph (pydantic-graph)                │        │  - Gemini   │ │
│  │  Nodes, edges, conditions defined in YAML       │        │  - Groq     │ │
│  │                                                 │        │  - etc.     │ │
│  │  ┌───────────┐   condition   ┌───────────┐      │        │             │ │
│  │  │ AgentNode │──────────────▶│ AgentNode │      │        │ + Custom:   │ │
│  │  │ (reviewer)│               │(publisher)│      │        │  LlamaStack │ │
│  │  └─────┬─────┘               └───────────┘      │        │  (unified   │ │
│  │        │                                        │        │   gateway)  │ │
│  │        │ condition      Each AgentNode:         │        └─────────────┘ │
│  │        ▼                • Wraps an Agent        │              ▲         │
│  │  ┌───────────┐          • Adds workflow state   │              │         │
│  │  │ AgentNode │          • Evaluates edges       │──────────────┘         │
│  │  │ (improver)│          • Routes to next node   │   calls Agent          │
│  │  └───────────┘                                  │                        │
│  └─────────────────────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## How Agents Work

1. Define agent in `config.yaml`
2. Agent is created with Pydantic AI at startup

```yaml
agents:
  - name: content_improver
    description: Improves content based on reviewer feedback
    model: openai:gpt-4o-mini
    instructions: |
      You are a content improvement specialist...
```

---

## Multi-Agent Delegation

Agents can delegate to other agents as tools:

```yaml
agents:
  - name: coordinator
    model: openai:gpt-4o
    subagents: [researcher, writer]
    instructions: |
      Coordinate research and writing tasks...

  - name: researcher
    model: openai:gpt-4o-mini
    instructions: |
      Research topics thoroughly...

  - name: writer
    model: openai:gpt-4o-mini
    instructions: |
      Write clear, engaging content...
```

Token usage is accumulated across the delegation chain.

---

## Structured Outputs

Define output schemas in YAML — they become Pydantic models at runtime:

```yaml
agents:
  - name: content_reviewer
    description: Reviews content and decides if it needs revision
    model: openai:gpt-4o-mini
    output_type:
      name: ContentReview
      description: Structured review decision
      fields:
        - name: approved
          type: bool
          description: Whether the content is ready for publication
        - name: quality_score
          type: int
          description: Quality score from 1-10
        - name: issues
          type: list[str]
          description: List of issues found (empty if approved)
        - name: summary
          type: str
          description: Brief summary of the review
    instructions: |
      You are a content reviewer. Analyze the provided content...
```

Supported types: `str`, `int`, `float`, `bool`, `list[T]`, `optional[T]`

---

## How Workflows Work

Workflows are **directed graphs** where:
- **Nodes** execute agents
- **Edges** determine routing based on conditions

```
┌───────────┐      approved       ┌───────────┐
│  Reviewer │ ─────────────────▶  │ Publisher │
└───────────┘                     └───────────┘
      │
      │ not approved
      ▼
┌───────────┐
│  Improver │ ───────────────────▶ (loop back)
└───────────┘
```

```yaml
workflows:
  - name: content_pipeline
    start_node: content_reviewer_node
    nodes:
      - name: content_reviewer_node
        type: agent
        agent: content_reviewer
      - name: content_improver_node
        type: agent
        agent: content_improver
      - name: publisher_node
        type: agent
        agent: publisher
    edges:
      - from: content_reviewer_node
        to: publisher_node
        condition: "output.approved"
      - from: content_reviewer_node
        to: content_improver_node  # Default if not approved
      - from: content_improver_node
        to: content_reviewer_node
      - from: publisher_node
        to: __end__
```

---

## Conditional Routing

Edges support Python expressions for routing:

```yaml
edges:
  - from: reviewer_node
    to: publisher_node
    condition: "output.approved and output.score >= 8"
  - from: reviewer_node
    to: improver_node
    condition: "not output.approved"
  - from: reviewer_node
    to: __end__  # Default fallback (no condition)
```

**Available in expressions:** `output`, `state`, `history`, `input`, `len`, `any`, `all`

---

## Model Providers

Use **any Pydantic AI provider** out of the box:

```yaml
model: openai:gpt-4o-mini
model: anthropic:claude-3-5-sonnet
model: gemini-1.5-pro
model: groq:llama-3.3-70b
```

Adding a custom provider is straightforward — LlamaStack was added relatively easily

```yaml
model: llama-stack:openai/gpt-4o-mini
model: llama-stack:together/meta-llama-3-70b
```

---

## Summary

**Lightspeed Agentic** enables:

- **No-code agent definition** via YAML
- **Complex workflows** with conditional routing
- **Type-safe outputs** validated by Pydantic
- **Multi-model support** via OpenAI and LlamaStack
- **Production-ready API** with FastAPI

**Next steps:**
- Implement agent capabilities/tools (MCP, shields, etc.)
- Orchestrator based `/query` endpoint
- Add authentication and rate limiting
- Non-LLM workflow nodes (code execution, API calls)
- Human-in-the-loop approval gates
- Agent-to-Agent (A2A) protocol support

---

## Questions?

**Repository:** `poc-lightspeed-agentic`

**Tech Stack:**
- Python 3.12+
- FastAPI
- Pydantic AI
- pydantic-graph
- LlamaStack

