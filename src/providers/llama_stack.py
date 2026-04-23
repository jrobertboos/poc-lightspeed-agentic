"""Pydantic AI model provider for LlamaStack.

This module provides a custom Model implementation that uses LlamaStack
as an in-process library via AsyncLlamaStackAsLibraryClient.
"""

from __future__ import annotations

import io
import json
import os
import sys
from contextlib import contextmanager
from typing import Any, Iterator, Literal, TypedDict

from llama_stack.core.library_client import AsyncLlamaStackAsLibraryClient
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelResponsePart,
    RetryPromptPart,
    SystemPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models import Model, ModelRequestParameters
from pydantic_ai.settings import ModelSettings
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.usage import RequestUsage


@contextmanager
def _suppress_stdout() -> Iterator[None]:
    """Temporarily suppress stdout to hide llama_stack config dump."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout


class LlamaStackModelSettings(TypedDict, total=False):
    """Settings for LlamaStack model requests."""

    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    stop: str | list[str]
    seed: int
    reasoning_effort: Literal["none", "low", "medium", "high", "xhigh"]


class LlamaStackModel(Model):
    """Pydantic AI Model implementation for LlamaStack.

    This model provider runs LlamaStack as an in-process library using
    AsyncLlamaStackAsLibraryClient with the specified distribution.

    Example:
        ```python
        from pydantic_ai import Agent
        from src.providers import LlamaStackModel

        model = LlamaStackModel(
            model_id="meta-llama/Llama-3.1-8B-Instruct",
            distro="starter",
        )
        agent = Agent(model)
        result = agent.run_sync("Hello!")
        ```
    """

    def __init__(
        self,
        model_id: str,
        *,
        distro: str = "starter",
        provider_data: dict[str, Any] | None = None,
    ) -> None:
        self._model_id = model_id
        self._distro = distro
        self._provider_data = self._build_provider_data(provider_data)
        self._client: AsyncLlamaStackAsLibraryClient | None = None
        self._initialized = False

    def _build_provider_data(
        self, provider_data: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Build provider data with API keys from environment variables."""
        data = dict(provider_data) if provider_data else {}

        env_mappings = {
            "openai_api_key": "OPENAI_API_KEY",
            "anthropic_api_key": "ANTHROPIC_API_KEY",
            "together_api_key": "TOGETHER_API_KEY",
            "fireworks_api_key": "FIREWORKS_API_KEY",
            "gemini_api_key": "GEMINI_API_KEY",
        }

        for key, env_var in env_mappings.items():
            if key not in data and os.environ.get(env_var):
                data[key] = os.environ[env_var]

        return data

    async def _ensure_initialized(self) -> AsyncLlamaStackAsLibraryClient:
        """Lazily initialize the client on first use."""
        if self._client is None:
            with _suppress_stdout():            # Prevent llama_stack from reconfiguring logging
                import llama_stack.core.library_client as llama_client_module
                original_setup = llama_client_module.setup_logging
                llama_client_module.setup_logging = lambda *args, **kwargs: None
                try:
                    self._client = AsyncLlamaStackAsLibraryClient(
                        self._distro,
                        provider_data=self._provider_data,
                    )
                finally:
                    llama_client_module.setup_logging = original_setup

        if not self._initialized:
            with _suppress_stdout():
                await self._client.initialize()
            self._initialized = True
        return self._client

    @property
    def model_name(self) -> str:
        """Return the model identifier."""
        return self._model_id

    @property
    def system(self) -> str:
        """Return the provider identifier for OpenTelemetry."""
        return "llama-stack"

    async def request(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
    ) -> ModelResponse:
        """Make a non-streaming request to LlamaStack."""
        client = await self._ensure_initialized()

        llama_messages = self._map_messages(messages)
        tools = self._map_tools(model_request_parameters.function_tools)

        settings = self._merge_settings(model_settings)

        response_format = self._build_response_format(model_request_parameters)
        if response_format:
            settings["response_format"] = response_format

        response = await client.chat.completions.create(
            model=self._model_id,
            messages=llama_messages,
            tools=tools if tools else None,
            stream=False,
            **settings,
        )

        return self._process_response(response)

    def _build_response_format(
        self, model_request_parameters: ModelRequestParameters
    ) -> dict[str, Any] | None:
        """Build response_format for structured output modes."""
        output_mode = model_request_parameters.output_mode
        output_object = model_request_parameters.output_object

        if output_mode in ("native", "auto") and output_object is not None:
            return {
                "type": "json_schema",
                "json_schema": {
                    "name": output_object.name,
                    "schema": output_object.json_schema,
                    "strict": output_object.strict,
                },
            }
        elif output_mode == "prompted":
            return {"type": "json_object"}

        return None

    async def __aenter__(self) -> LlamaStackModel:
        """Enter async context."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context and cleanup."""
        if self._client is not None:
            await self._client.shutdown()
            self._client = None
            self._initialized = False

    def _map_messages(self, messages: list[ModelMessage]) -> list[dict[str, Any]]:
        """Convert Pydantic AI messages to LlamaStack format."""
        result: list[dict[str, Any]] = []

        for message in messages:
            if isinstance(message, ModelRequest):
                result.extend(self._map_request(message))
            elif isinstance(message, ModelResponse):
                result.extend(self._map_response(message))

        return result

    def _map_request(self, request: ModelRequest) -> list[dict[str, Any]]:
        """Map a ModelRequest to LlamaStack messages."""
        messages: list[dict[str, Any]] = []

        for part in request.parts:
            if isinstance(part, SystemPromptPart):
                messages.append({
                    "role": "system",
                    "content": part.content,
                })
            elif isinstance(part, UserPromptPart):
                messages.append({
                    "role": "user",
                    "content": part.content,
                })
            elif isinstance(part, ToolReturnPart):
                messages.append({
                    "role": "tool",
                    "tool_call_id": part.tool_call_id,
                    "content": part.content if isinstance(part.content, str) else json.dumps(part.content),
                })
            elif isinstance(part, RetryPromptPart):
                content = part.content
                if isinstance(content, list):
                    content = "\n".join(str(item) for item in content)
                messages.append({
                    "role": "user",
                    "content": f"Please retry. {content}",
                })

        return messages

    def _map_response(self, response: ModelResponse) -> list[dict[str, Any]]:
        """Map a ModelResponse to LlamaStack messages."""
        content_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []

        for part in response.parts:
            if isinstance(part, TextPart):
                content_parts.append(part.content)
            elif isinstance(part, ToolCallPart):
                tool_calls.append({
                    "id": part.tool_call_id,
                    "type": "function",
                    "function": {
                        "name": part.tool_name,
                        "arguments": part.args_as_json_str(),
                    },
                })

        message: dict[str, Any] = {"role": "assistant"}

        if content_parts:
            message["content"] = "".join(content_parts)

        if tool_calls:
            message["tool_calls"] = tool_calls

        return [message] if content_parts or tool_calls else []

    def _map_tools(
        self, tools: list[ToolDefinition] | None
    ) -> list[dict[str, Any]] | None:
        """Convert Pydantic AI tool definitions to LlamaStack format."""
        if not tools:
            return None

        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.parameters_json_schema,
                },
            }
            for tool in tools
        ]

    def _merge_settings(
        self, model_settings: ModelSettings | None
    ) -> dict[str, Any]:
        """Merge model settings into request parameters."""
        if model_settings is None:
            return {}

        settings: dict[str, Any] = {}

        if model_settings.get("temperature") is not None:
            settings["temperature"] = model_settings["temperature"]
        if model_settings.get("max_tokens") is not None:
            settings["max_tokens"] = model_settings["max_tokens"]
        if model_settings.get("top_p") is not None:
            settings["top_p"] = model_settings["top_p"]

        return settings

    def _process_response(self, response: Any) -> ModelResponse:
        """Process a LlamaStack response into Pydantic AI format."""
        parts: list[ModelResponsePart] = []

        choice = response.choices[0]
        message = choice.message

        if message.content:
            parts.append(TextPart(content=message.content))

        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                args = tool_call.function.arguments
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        pass

                parts.append(
                    ToolCallPart(
                        tool_name=tool_call.function.name,
                        args=args,
                        tool_call_id=tool_call.id,
                    )
                )

        usage = RequestUsage(
            input_tokens=getattr(response.usage, "prompt_tokens", 0),
            output_tokens=getattr(response.usage, "completion_tokens", 0),
        )

        return ModelResponse(parts=parts, model_name=self._model_id, usage=usage)
