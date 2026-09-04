"""Small model-agnostic agent loop for Gemma 4."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from gemma_protocol import Message, ToolCall, parse_tool_calls, render_prompt, visible_text


class Model(Protocol):
    def generate(self, prompt: str) -> str: ...


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    function: Callable[..., Any]


class Agent:
    def __init__(self, model: Model, system_prompt: str, tools: list[Tool] | None = None, thinking: bool = False):
        self.model = model
        self.tools = {tool.name: tool for tool in tools or []}
        self.messages = [Message("system", system_prompt)]
        self.thinking = thinking

    def _declarations(self) -> list[str]:
        return [
            f"declaration:{tool.name}{{description:<|\"|>{tool.description}<|\"|>,parameters:{tool.parameters}}}"
            for tool in self.tools.values()
        ]

    def run(self, user_text: str, max_steps: int = 8) -> str:
        self.messages.append(Message("user", user_text))
        for _ in range(max_steps):
            prompt = render_prompt(self.messages, self._declarations(), self.thinking)
            raw_response = self.model.generate(prompt)
            calls = parse_tool_calls(raw_response)
            if not calls:
                self.messages.append(Message("model", visible_text(raw_response)))
                return visible_text(raw_response)
            self.messages.append(
                Message(
                    "model",
                    tool_calls=[{"function": {"name": call.name, "arguments": call.arguments}} for call in calls],
                )
            )
            responses = [self._execute(call) for call in calls]
            self.messages.append(Message("model", tool_responses=responses))
        raise RuntimeError("El agente alcanzó el límite de iteraciones de herramientas")

    def _execute(self, call: ToolCall) -> dict[str, Any]:
        tool = self.tools.get(call.name)
        if tool is None:
            return {"name": call.name, "response": {"error": "Herramienta no registrada"}}
        try:
            result = tool.function(**call.arguments)
        except Exception as error:  # Keep tool failures inside the model protocol.
            result = {"error": f"{type(error).__name__}: {error}"}
        if not isinstance(result, dict):
            result = {"result": result}
        return {"name": call.name, "response": result}