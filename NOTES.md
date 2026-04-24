# Example Request Bodies

A collection of example request bodies for demonstrating the workflows and agents.

---

## Agent Examples

### Content Reviewer

Reviews content and provides structured feedback with approval status and quality score.

```json
POST /agents/run
{
  "message": "Please review this article: 'Cats are amazing pets. They sleep a lot and like to play with yarn. The end.'",
  "agent_name": "content_reviewer"
}
```

```json
POST /agents/run
{
  "message": "Review this blog post: 'The Majestic Maine Coon: Standing as one of the largest domesticated cat breeds, the Maine Coon captivates with its tufted ears, bushy tail, and gentle giant personality. Originally from the northeastern United States, these cats are known for their intelligence, playful nature, and dog-like loyalty to their owners.'",
  "agent_name": "content_reviewer"
}
```

### Content Improver

Takes feedback and improves the content quality.

```json
POST /agents/run
{
  "message": "Improve this cat article based on feedback that it's too short and lacks detail: 'Cats are amazing pets. They sleep a lot and like to play with yarn. The end.'",
  "agent_name": "content_improver"
}
```

```json
POST /agents/run
{
  "message": "The reviewer said this needs more personality and specific examples. Please improve: 'Siamese cats are vocal. They have blue eyes. They come from Thailand.'",
  "agent_name": "content_improver"
}
```

### Publisher

Prepares approved content for publication with metadata.

```json
POST /agents/run
{
  "message": "Prepare this for publication: 'Why Cats Make Purrfect Companions: From their soothing purrs that can lower human blood pressure to their independent yet affectionate nature, cats have earned their place as beloved household companions for over 10,000 years.'",
  "agent_name": "publisher"
}
```

### Researcher

Researches topics thoroughly.

```json
POST /agents/run
{
  "message": "Research the history of cats as pets, including when they were first domesticated and how they spread across different civilizations.",
  "agent_name": "researcher"
}
```

```json
POST /agents/run
{
  "message": "I need research on the top 5 most popular cat breeds in America and what makes each unique.",
  "agent_name": "researcher"
}
```

### Writer

Writes clear, engaging content.

```json
POST /agents/run
{
  "message": "Write a short, engaging blog post about why cats knock things off tables.",
  "agent_name": "writer"
}
```

```json
POST /agents/run
{
  "message": "Write a fun listicle: '7 Signs Your Cat Secretly Rules Your Household'",
  "agent_name": "writer"
}
```

### Coordinator (Multi-Agent Delegation)

Coordinates the researcher and writer subagents to complete complex tasks.

```json
POST /agents/run
{
  "message": "Create a well-researched article about the science behind why cats purr. First research the topic, then write an engaging piece for a general audience.",
  "agent_name": "coordinator"
}
```

```json
POST /agents/run
{
  "message": "I need an article comparing indoor vs outdoor cats. Research the pros and cons of each lifestyle, then write a balanced piece that helps cat owners make an informed decision.",
  "agent_name": "coordinator"
}
```

```json
POST /agents/run
{
  "message": "Research cat nutrition myths and then write a myth-busting article that separates fact from fiction for cat owners.",
  "agent_name": "coordinator"
}
```

---

## Workflow Examples

### Content Pipeline

The content pipeline workflow demonstrates conditional routing and looping:
1. **Reviewer** evaluates quality and decides if content is approved
2. If approved (quality_score >= 8), routes to **Publisher**
3. If not approved, routes to **Improver**, then loops back to **Reviewer**

#### Example: Low-Quality Content (Will Loop)

This content is too short and will likely need improvement before approval.

```json
POST /workflows/run
{
  "message": "Cats are cute. They meow.",
  "workflow_name": "content_pipeline"
}
```

#### Example: Medium-Quality Content (Might Loop)

This content has some substance but may need polish.

```json
POST /workflows/run
{
  "message": "The domestic cat, also known as Felis catus, is a small carnivorous mammal. Cats have been associated with humans for at least 9,500 years. They are valued for companionship and their ability to hunt vermin.",
  "workflow_name": "content_pipeline"
}
```

#### Example: High-Quality Content (Should Pass)

Well-written content that should pass review and go straight to publishing.

```json
POST /workflows/run
{
  "message": "The Secret Language of Cat Tails: When your feline friend approaches with their tail held high and slightly curved at the tip, they're offering you the warmest of cat greetings. This tail position, often accompanied by a gentle purr, signals contentment and trust. Conversely, a puffed-up tail indicates fear or aggression, while a slowly swishing tail suggests your cat is focused and potentially hunting - even if their prey is just a dust bunny under the couch. Understanding these subtle signals can transform your relationship with your cat from cohabitation to true companionship.",
  "workflow_name": "content_pipeline"
}
```

#### Example: Creative Content

```json
POST /workflows/run
{
  "message": "A Day in the Life of a House Cat: 3 AM - Sprint through hallway at maximum velocity for no apparent reason. 6 AM - Wake human by sitting on their face. 8 AM - Ignore expensive cat food, demand whatever human is eating. 10 AM - Find single sunbeam, nap for 4 hours. 2 PM - Knock pen off desk, watch it fall with great interest. 3 PM - Demand attention. Immediately reject attention. 5 PM - Stare at wall. There's nothing there. Or is there? 8 PM - Act like never been fed in entire life. 11 PM - Bring human a gift (it's a sock). Midnight - Repeat 3 AM activities.",
  "workflow_name": "content_pipeline"
}
```

#### Example: Educational Content

```json
POST /workflows/run
{
  "message": "Why Do Cats Knead? That rhythmic pushing motion cats make with their paws, often called 'making biscuits,' traces back to kittenhood. Newborn kittens knead their mother's belly to stimulate milk flow during nursing. Adult cats retain this behavior as a self-soothing mechanism, often kneading when they feel safe, content, or sleepy. The behavior releases endorphins and may also be a way of marking territory, as cats have scent glands in their paw pads. So when your cat kneads your lap (claws and all), take it as the highest compliment - they're telling you that you make them feel as safe and content as they did with their mother.",
  "workflow_name": "content_pipeline"
}
```

---

## Quick Reference

### List Available Agents
```
GET /agents
```

### List Available Workflows
```
GET /workflows
```

### Get Agent Details
```
GET /agents/content_reviewer
GET /agents/coordinator
```

### Get Workflow Details
```
GET /workflows/content_pipeline
```

---

## Response Examples

### Agent Response Structure
```json
{
  "output": {
    "approved": true,
    "quality_score": 9,
    "feedback": "Well-written and engaging content about cats."
  },
  "tool_calls": [],
  "tool_results": []
}
```

### Workflow Response Structure
```json
{
  "output": "Published content with metadata...",
  "history": [
    {
      "node": "content_reviewer_node",
      "output": {"approved": true, "quality_score": 9, "feedback": "..."},
      "output_text": "{\"approved\": true, ...}",
      "agent": "content_reviewer"
    },
    {
      "node": "publisher_node",
      "output": {"title": "...", "content": "...", "tags": ["cats"]},
      "output_text": "{...}",
      "agent": "publisher"
    }
  ]
}
```

### Coordinator Response (with Tool Calls)
```json
{
  "output": "Here's your researched article about cat purring...",
  "tool_calls": [
    {
      "tool_name": "researcher",
      "tool_call_id": "call_abc123",
      "args": {"message": "Research the science behind cat purring"}
    },
    {
      "tool_name": "writer",
      "tool_call_id": "call_def456",
      "args": {"message": "Write an engaging article based on this research..."}
    }
  ],
  "tool_results": [
    {
      "tool_name": "researcher",
      "tool_call_id": "call_abc123",
      "content": "Research findings about cat purring...",
      "outcome": "success"
    },
    {
      "tool_name": "writer",
      "tool_call_id": "call_def456",
      "content": "The finished article...",
      "outcome": "success"
    }
  ]
}
```
