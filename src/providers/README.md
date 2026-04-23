# Custom Model Providers

This module contains custom Pydantic AI model providers.

## LlamaStackModel

A Pydantic AI model provider that runs [LlamaStack](https://github.com/llamastack/llama-stack) as an in-process library using `AsyncLlamaStackAsLibraryClient`.

### Usage

```python
from pydantic_ai import Agent
from src.providers import LlamaStackModel

# Create the model provider with the "starter" distribution
model = LlamaStackModel(
    model_id="meta-llama/Llama-3.1-8B-Instruct",
    distro="starter",  # Default distribution
    provider_data=None,  # Optional provider-specific data
)

# Use with a Pydantic AI agent
agent = Agent(model, instructions="You are a helpful assistant.")
result = agent.run_sync("Hello, how are you?")
print(result.output)
```

### With Tools

```python
from pydantic_ai import Agent, RunContext
from src.providers import LlamaStackModel

model = LlamaStackModel(
    model_id="meta-llama/Llama-3.1-70B-Instruct",
    distro="starter",
)

agent = Agent(model)

@agent.tool_plain
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"The weather in {city} is sunny and 72F"

result = agent.run_sync("What's the weather in San Francisco?")
print(result.output)
```

### Streaming

```python
import asyncio
from pydantic_ai import Agent
from src.providers import LlamaStackModel

model = LlamaStackModel(
    model_id="meta-llama/Llama-3.1-8B-Instruct",
    distro="starter",
)

agent = Agent(model)

async def main():
    async with agent.run_stream("Tell me a story") as stream:
        async for text in stream.stream_text():
            print(text, end="", flush=True)
    print()

asyncio.run(main())
```

### Configuration

The model accepts the following settings via `model_settings`:

- `temperature`: Float for sampling randomness (0.0-2.0)
- `max_tokens`: Maximum tokens to generate
- `top_p`: Float for nucleus sampling (0.0-1.0)

```python
result = agent.run_sync(
    "Explain quantum computing",
    model_settings={"temperature": 0.7, "max_tokens": 500}
)
```

### Environment Variables

The model automatically picks up API keys from environment variables:

| Environment Variable | Provider |
|---------------------|----------|
| `OPENAI_API_KEY` | OpenAI models (e.g., `openai/gpt-4o-mini`) |
| `ANTHROPIC_API_KEY` | Anthropic models |
| `TOGETHER_API_KEY` | Together AI models |
| `FIREWORKS_API_KEY` | Fireworks AI models |
| `GEMINI_API_KEY` | Google Gemini models |

You can also pass API keys directly via `provider_data`:

```python
model = LlamaStackModel(
    model_id="openai/gpt-4o-mini",
    provider_data={"openai_api_key": "sk-..."},
)
```

### Installation

Make sure you have the llama-stack package installed with the starter distribution:

```bash
uv pip install llama-stack[starter]
```
