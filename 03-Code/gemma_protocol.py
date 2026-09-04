"""Gemma 4 prompt formatting and tool-call parsing."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


TURN_START = "<|turn>"
TURN_END = "<turn|>"
THINK = "<|think|>"
CHANNEL_START = "<|channel>"
CHANNEL_END = "<channel|>"
TOOL_CALL_START = "<|tool_call>"
TOOL_CALL_END = "<tool_call|>"
TOOL_RESPONSE_START = "<|tool_response>"


@dataclass(frozen=True)
class Message:
    role: str
    content: str = ""
    tool_calls: list[dict[str, Any]] | None = None
    tool_responses: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return f'<|"|>{value}<|"|>'
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def render_tool_declaration(name: str, description: str, parameters: dict[str, Any]) -> str:
    """Render a compact declaration inside Gemma's system turn."""
    payload = json.dumps(parameters, ensure_ascii=False, separators=(",", ":"))
    return f"declaration:{name}{{description:<|\"|>{description}<|\"|>,parameters:{payload}}}"


def render_prompt(
    messages: list[Message],
    tool_declarations: list[str] | None = None,
    enable_thinking: bool = False,
) -> str:
    """Render chat history using Gemma 4 control tokens."""
    rendered: list[str] = []
    for message in messages:
        content = message.content
        if message.role == "system" and enable_thinking:
            content = f"{THINK}{content}"
        if message.tool_calls:
            content += "".join(
                f"{TOOL_CALL_START}call:{call['function']['name']}"
                f"{_render_arguments(call['function'].get('arguments', {}))}{TOOL_CALL_END}"
                for call in message.tool_calls
            )
        if message.tool_responses:
            content += "".join(
                f"{TOOL_RESPONSE_START}response:{response['name']}"
                f"{_render_arguments(response.get('response', {}))}<tool_response|>"
                for response in message.tool_responses
            )
        rendered.append(f"{TURN_START}{message.role}\n{content}{TURN_END}")

    if tool_declarations:
        system_prefix = f"{THINK if enable_thinking else ''}<|tool>" + "".join(tool_declarations) + "<tool|>"
        if rendered and rendered[0].startswith(f"{TURN_START}system"):
            rendered[0] = rendered[0].replace("\n", f"\n{system_prefix}\n", 1)
        else:
            rendered.insert(0, f"{TURN_START}system\n{system_prefix}{TURN_END}")
    return "\n".join(rendered)


def _render_arguments(arguments: dict[str, Any]) -> str:
    return "{" + ",".join(f"{key}:{_stringify(value)}" for key, value in arguments.items()) + "}"


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith('<|"|>') and raw.endswith('<|"|>'):
        return raw[5:-5]
    if raw in {"true", "false"}:
        return raw == "true"
    if raw == "null":
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _split_fields(body: str) -> list[str]:
    fields: list[str] = []
    start = 0
    depth = 0
    in_string = False
    index = 0
    while index < len(body):
        if body.startswith('<|"|>', index):
            in_string = not in_string
            index += 5
            continue
        char = body[index]
        if not in_string:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            elif char == "," and depth == 0:
                fields.append(body[start:index])
                start = index + 1
        index += 1
    fields.append(body[start:])
    return fields


def _parse_arguments(body: str) -> dict[str, Any]:
    body = body.strip()
    if not body.startswith("{") or not body.endswith("}"):
        raise ValueError("Los argumentos de la herramienta no tienen formato de objeto")
    arguments: dict[str, Any] = {}
    for field in _split_fields(body[1:-1]):
        if not field.strip():
            continue
        key, separator, raw_value = field.partition(":")
        if not separator:
            raise ValueError(f"Campo de argumento inválido: {field}")
        arguments[key.strip()] = _parse_value(raw_value)
    return arguments


def parse_tool_calls(text: str) -> list[ToolCall]:
    """Extract Gemma tool calls while ignoring private thought channels."""
    pattern = re.compile(r"<\|tool_call\s*>call:([A-Za-z_][\w.-]*)\s*(\{.*?\})<tool_call\|>", re.DOTALL)
    return [ToolCall(name, _parse_arguments(body)) for name, body in pattern.findall(text)]


def visible_text(text: str) -> str:
    """Remove control blocks that should never be shown to an end user."""
    text = re.sub(r"<\|channel\s*>thought.*?<channel\|>", "", text, flags=re.DOTALL)
    text = re.sub(r"<\|tool_call\s*>.*?<tool_call\|>", "", text, flags=re.DOTALL)
    return text.replace(TOOL_RESPONSE_START, "").strip()