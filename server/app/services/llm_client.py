"""LLM backbone for advisory: chat messages, system prompts, and tool calling."""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

OPENAI_BASE_URL = "https://api.openai.com/v1"
ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
ANTHROPIC_VERSION = "2023-06-01"

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
    "groq": "llama-3.3-70b-versatile",
    "openai_compatible": "gpt-4o-mini",
}

ADVISORY_SYSTEM_PROMPT = """You are a rural business feasibility advisor for India.
Use only the supplied location, market, and scheme context. Do not invent census
figures, competitor names, or prices that are not supported by that context.
If evidence is thin, say so and keep recommendations conservative.
Write in the language the user requested. Prefer short, practical bullet points
a first-time rural entrepreneur can act on."""

FEASIBILITY_ANALYSIS_TOOL: dict[str, Any] = {
    "name": "submit_feasibility_analysis",
    "description": (
        "Return the structured feasibility advisory: opportunity write-up, SWOT, "
        "key threats, and a local pricing suggestion."
    ),
    "parameters": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "opportunity_analysis": {
                "type": "string",
                "description": "2-4 sentences on unmet demand and why this business can work here.",
            },
            "swot": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "strengths": {"type": "array", "items": {"type": "string"}},
                    "weaknesses": {"type": "array", "items": {"type": "string"}},
                    "opportunities": {"type": "array", "items": {"type": "string"}},
                    "threats": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["strengths", "weaknesses", "opportunities", "threats"],
            },
            "threats": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Top standalone threats to surface in the report.",
            },
            "pricing_suggestion": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "suggested_price_range": {"type": "string"},
                    "reasoning": {"type": "string"},
                },
                "required": ["suggested_price_range", "reasoning"],
            },
        },
        "required": [
            "opportunity_analysis",
            "swot",
            "threats",
            "pricing_suggestion",
        ],
    },
}

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_client: httpx.Client | None = None


class LLMError(RuntimeError):
    """Raised when the LLM provider rejects or cannot complete a request."""


class LLMNotConfigured(LLMError):
    """Raised when no API key is configured."""


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]
    id: str | None = None


@dataclass
class LLMResponse:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    provider: str = ""
    model: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def structured(self) -> dict[str, Any] | None:
        if self.tool_calls:
            return self.tool_calls[0].arguments
        return extract_json(self.content)


def is_configured() -> bool:
    return bool(settings.llm_api_key and settings.llm_api_key.strip())


def provider_name() -> str:
    return (settings.llm_provider or "openai").strip().lower()


def resolved_model() -> str:
    if settings.llm_model:
        return settings.llm_model
    return DEFAULT_MODELS.get(provider_name(), DEFAULT_MODELS["openai"])


def resolved_base_url() -> str:
    if settings.llm_base_url:
        return settings.llm_base_url.rstrip("/")
    name = provider_name()
    if name == "anthropic":
        return ANTHROPIC_BASE_URL
    if name == "groq":
        return GROQ_BASE_URL
    return OPENAI_BASE_URL


def _http() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(
            timeout=httpx.Timeout(settings.llm_timeout_seconds),
            follow_redirects=True,
        )
    return _client


def normalize_messages(
    messages: str | Sequence[str | Mapping[str, Any]],
    *,
    system: str | None = None,
) -> tuple[str | None, list[dict[str, str]]]:
    """Normalize chat input into (system, [{role, content}, ...])."""
    if isinstance(messages, str):
        items: list[dict[str, str]] = [{"role": "user", "content": messages}]
    else:
        items = []
        for message in messages:
            if isinstance(message, str):
                items.append({"role": "user", "content": message})
                continue
            role = str(message.get("role") or "user")
            content = message.get("content")
            if content is None:
                continue
            items.append({"role": role, "content": str(content)})

    system_text = system
    chat: list[dict[str, str]] = []
    for item in items:
        if item["role"] == "system":
            system_text = f"{system_text}\n{item['content']}".strip() if system_text else item["content"]
        else:
            chat.append(item)
    if not chat:
        raise ValueError("At least one user or assistant message is required.")
    return system_text, chat


def extract_json(text: str) -> dict[str, Any] | None:
    """Parse a JSON object from model text, including fenced blocks."""
    if not text or not text.strip():
        return None
    candidate = text.strip()
    fenced = _JSON_FENCE.search(candidate)
    if fenced:
        candidate = fenced.group(1)
    else:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start == -1 or end <= start:
            return None
        candidate = candidate[start : end + 1]
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _parse_arguments(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    return {}


def openai_tools(tools: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    payload = []
    for tool in tools:
        payload.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description") or "",
                "parameters": tool.get("parameters") or {"type": "object", "properties": {}},
            },
        })
    return payload


def anthropic_tools(tools: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    payload = []
    for tool in tools:
        payload.append({
            "name": tool["name"],
            "description": tool.get("description") or "",
            "input_schema": tool.get("parameters") or {"type": "object", "properties": {}},
        })
    return payload


def openai_tool_choice(choice: str | Mapping[str, Any] | None) -> Any:
    if choice is None:
        return None
    if isinstance(choice, Mapping):
        return {"type": "function", "function": {"name": choice["name"]}} if choice.get("name") else choice
    if choice == "auto":
        return "auto"
    if choice in {"required", "any"}:
        return "required"
    return choice


def anthropic_tool_choice(choice: str | Mapping[str, Any] | None) -> Any:
    if choice is None:
        return None
    if isinstance(choice, Mapping):
        return {"type": "tool", "name": choice["name"]} if choice.get("name") else choice
    if choice == "auto":
        return {"type": "auto"}
    if choice in {"required", "any"}:
        return {"type": "any"}
    return choice


def build_openai_request(
    *,
    system: str | None,
    messages: Sequence[Mapping[str, str]],
    tools: Sequence[Mapping[str, Any]] | None = None,
    tool_choice: str | Mapping[str, Any] | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    chat: list[dict[str, str]] = []
    if system:
        chat.append({"role": "system", "content": system})
    chat.extend(dict(message) for message in messages)
    body: dict[str, Any] = {
        "model": resolved_model(),
        "messages": chat,
        "temperature": settings.llm_temperature if temperature is None else temperature,
        "max_tokens": settings.llm_max_tokens if max_tokens is None else max_tokens,
    }
    if tools:
        body["tools"] = openai_tools(tools)
        mapped = openai_tool_choice(tool_choice)
        if mapped is not None:
            body["tool_choice"] = mapped
    return body


def build_anthropic_request(
    *,
    system: str | None,
    messages: Sequence[Mapping[str, str]],
    tools: Sequence[Mapping[str, Any]] | None = None,
    tool_choice: str | Mapping[str, Any] | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": resolved_model(),
        "max_tokens": settings.llm_max_tokens if max_tokens is None else max_tokens,
        "temperature": settings.llm_temperature if temperature is None else temperature,
        "messages": [dict(message) for message in messages],
    }
    if system:
        body["system"] = system
    if tools:
        body["tools"] = anthropic_tools(tools)
        mapped = anthropic_tool_choice(tool_choice)
        if mapped is not None:
            body["tool_choice"] = mapped
    return body


def parse_openai_response(payload: Mapping[str, Any]) -> LLMResponse:
    choices = payload.get("choices") or []
    if not choices:
        raise LLMError("OpenAI response contained no choices.")
    message = choices[0].get("message") or {}
    tool_calls: list[ToolCall] = []
    for call in message.get("tool_calls") or []:
        function = call.get("function") or {}
        try:
            arguments = _parse_arguments(function.get("arguments"))
        except json.JSONDecodeError as exc:
            raise LLMError("OpenAI tool arguments were not valid JSON.") from exc
        tool_calls.append(ToolCall(
            name=str(function.get("name") or ""),
            arguments=arguments,
            id=call.get("id"),
        ))
    return LLMResponse(
        content=str(message.get("content") or ""),
        tool_calls=tool_calls,
        provider="openai",
        model=str(payload.get("model") or resolved_model()),
        raw=dict(payload),
    )


def parse_anthropic_response(payload: Mapping[str, Any]) -> LLMResponse:
    text_parts: list[str] = []
    tool_calls: list[ToolCall] = []
    for block in payload.get("content") or []:
        block_type = block.get("type")
        if block_type == "text":
            text_parts.append(str(block.get("text") or ""))
        elif block_type == "tool_use":
            arguments = block.get("input") or {}
            if not isinstance(arguments, dict):
                arguments = {}
            tool_calls.append(ToolCall(
                name=str(block.get("name") or ""),
                arguments=arguments,
                id=block.get("id"),
            ))
    return LLMResponse(
        content="".join(text_parts),
        tool_calls=tool_calls,
        provider="anthropic",
        model=str(payload.get("model") or resolved_model()),
        raw=dict(payload),
    )


def _headers(name: str) -> dict[str, str]:
    key = (settings.llm_api_key or "").strip()
    if name == "anthropic":
        return {
            "x-api-key": key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
    return {
        "Authorization": f"Bearer {key}",
        "content-type": "application/json",
    }


def chat(
    messages: str | Sequence[str | Mapping[str, Any]],
    *,
    system: str | None = None,
    tools: Sequence[Mapping[str, Any]] | None = None,
    tool_choice: str | Mapping[str, Any] | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    client: httpx.Client | None = None,
) -> LLMResponse:
    """Send a chat completion to the configured provider (OpenAI-style or Claude)."""
    if not is_configured():
        raise LLMNotConfigured("LLM_API_KEY is not set.")

    system_text, chat_messages = normalize_messages(messages, system=system)
    name = provider_name()
    http = client or _http()

    if name == "anthropic":
        url = resolved_base_url() + "/messages"
        body = build_anthropic_request(
            system=system_text,
            messages=chat_messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        url = resolved_base_url() + "/chat/completions"
        body = build_openai_request(
            system=system_text,
            messages=chat_messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    try:
        response = http.post(url, headers=_headers(name), json=body)
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:500]
        raise LLMError(f"LLM provider HTTP {exc.response.status_code}: {detail}") from exc
    except httpx.HTTPError as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    parsed = parse_anthropic_response(payload) if name == "anthropic" else parse_openai_response(payload)
    parsed.provider = name
    return parsed


def generate_text(
    prompt: str,
    *,
    system: str | None = None,
    client: httpx.Client | None = None,
) -> str:
    """Simple text completion. Returns '' when no API key is configured."""
    if not is_configured():
        return ""
    result = chat(prompt, system=system, client=client)
    if result.content:
        return result.content
    structured = result.structured
    return json.dumps(structured, ensure_ascii=False) if structured else ""


def complete_structured(
    messages: str | Sequence[str | Mapping[str, Any]],
    *,
    tool: Mapping[str, Any] | None = None,
    system: str | None = None,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Force a tool call (or JSON fallback) and return the parsed object."""
    schema_tool = dict(tool or FEASIBILITY_ANALYSIS_TOOL)
    result = chat(
        messages,
        system=system,
        tools=[schema_tool],
        tool_choice={"name": schema_tool["name"]},
        client=client,
    )
    for call in result.tool_calls:
        if call.name == schema_tool["name"] and call.arguments:
            return call.arguments
    if result.tool_calls and result.tool_calls[0].arguments:
        return result.tool_calls[0].arguments
    parsed = extract_json(result.content)
    if parsed:
        return parsed
    raise LLMError("Model did not return structured tool arguments or JSON.")


def analyze_feasibility(
    *,
    business_category: str,
    location_label: str,
    context: str,
    language: str = "en",
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Advisory helper: one tool call that fills SWOT, opportunity, threats, pricing."""
    user_prompt = (
        f"Business category: {business_category}\n"
        f"Location: {location_label}\n"
        f"Response language: {language}\n\n"
        "Evidence and market context:\n"
        f"{context}\n\n"
        f"Call {FEASIBILITY_ANALYSIS_TOOL['name']} with the feasibility advisory."
    )
    return complete_structured(
        user_prompt,
        tool=FEASIBILITY_ANALYSIS_TOOL,
        system=ADVISORY_SYSTEM_PROMPT,
        client=client,
    )