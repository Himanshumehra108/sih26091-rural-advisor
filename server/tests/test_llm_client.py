import json

from app.services.llm_client import (
    ADVISORY_SYSTEM_PROMPT,
    FEASIBILITY_ANALYSIS_TOOL,
    LLMNotConfigured,
    analyze_feasibility,
    anthropic_tools,
    build_anthropic_request,
    build_openai_request,
    extract_json,
    generate_text,
    normalize_messages,
    openai_tools,
    parse_anthropic_response,
    parse_openai_response,
)


def test_normalize_messages_lifts_system_role():
    system, messages = normalize_messages(
        [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "Hello"},
        ],
        system=ADVISORY_SYSTEM_PROMPT,
    )
    assert "Be concise." in system
    assert "rural business" in system
    assert messages == [{"role": "user", "content": "Hello"}]


def test_extract_json_from_fenced_block():
    parsed = extract_json('Sure.\n```json\n{"opportunity_analysis": "Demand exists"}\n```')
    assert parsed == {"opportunity_analysis": "Demand exists"}


def test_openai_request_embeds_system_and_forced_tool():
    body = build_openai_request(
        system="You are an advisor.",
        messages=[{"role": "user", "content": "Analyze dairy in Nashik"}],
        tools=[FEASIBILITY_ANALYSIS_TOOL],
        tool_choice={"name": FEASIBILITY_ANALYSIS_TOOL["name"]},
        temperature=0.2,
        max_tokens=512,
    )
    assert body["messages"][0] == {"role": "system", "content": "You are an advisor."}
    assert body["tools"] == openai_tools([FEASIBILITY_ANALYSIS_TOOL])
    assert body["tool_choice"]["function"]["name"] == "submit_feasibility_analysis"
    assert body["max_tokens"] == 512


def test_anthropic_request_uses_top_level_system_and_input_schema():
    body = build_anthropic_request(
        system="You are an advisor.",
        messages=[{"role": "user", "content": "Analyze dairy in Nashik"}],
        tools=[FEASIBILITY_ANALYSIS_TOOL],
        tool_choice={"name": "submit_feasibility_analysis"},
    )
    assert body["system"] == "You are an advisor."
    assert "role" not in body["messages"][0] or body["messages"][0]["role"] == "user"
    assert body["tools"] == anthropic_tools([FEASIBILITY_ANALYSIS_TOOL])
    assert body["tool_choice"] == {"type": "tool", "name": "submit_feasibility_analysis"}
    assert "input_schema" in body["tools"][0]


def test_parse_openai_tool_call():
    payload = {
        "model": "gpt-4o-mini",
        "choices": [{
            "message": {
                "content": None,
                "tool_calls": [{
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "submit_feasibility_analysis",
                        "arguments": json.dumps({
                            "opportunity_analysis": "Unmet dairy demand near the haat.",
                            "swot": {
                                "strengths": ["Local milk supply"],
                                "weaknesses": ["Cold chain gaps"],
                                "opportunities": ["School midday meals"],
                                "threats": ["Seasonal surplus"],
                            },
                            "threats": ["Seasonal surplus"],
                            "pricing_suggestion": {
                                "suggested_price_range": "₹40–50 per litre",
                                "reasoning": "Matches nearby mandi quotes.",
                            },
                        }),
                    },
                }],
            }
        }],
    }
    parsed = parse_openai_response(payload)
    assert parsed.content == ""
    assert parsed.tool_calls[0].name == "submit_feasibility_analysis"
    assert parsed.structured["pricing_suggestion"]["suggested_price_range"] == "₹40–50 per litre"


def test_parse_anthropic_tool_use():
    payload = {
        "model": "claude-3-5-haiku-latest",
        "content": [
            {"type": "text", "text": "Filing the advisory now."},
            {
                "type": "tool_use",
                "id": "toolu_1",
                "name": "submit_feasibility_analysis",
                "input": {"opportunity_analysis": "Retail gap in the block."},
            },
        ],
    }
    parsed = parse_anthropic_response(payload)
    assert "Filing the advisory" in parsed.content
    assert parsed.structured == {"opportunity_analysis": "Retail gap in the block."}


def test_generate_text_returns_empty_without_api_key(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "llm_api_key", None)
    assert generate_text("Hello") == ""


def test_analyze_feasibility_uses_tool_call(monkeypatch):
    import httpx

    from app.core.config import settings

    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "llm_model", "gpt-4o-mini")

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode())
        assert body["messages"][0]["role"] == "system"
        assert body["tool_choice"]["function"]["name"] == "submit_feasibility_analysis"
        return httpx.Response(
            200,
            json={
                "model": "gpt-4o-mini",
                "choices": [{
                    "message": {
                        "content": "",
                        "tool_calls": [{
                            "id": "call_1",
                            "function": {
                                "name": "submit_feasibility_analysis",
                                "arguments": json.dumps({
                                    "opportunity_analysis": "Demand for tailoring near the bus stand.",
                                    "swot": {
                                        "strengths": ["Low rent"],
                                        "weaknesses": ["Few machines"],
                                        "opportunities": ["School uniforms"],
                                        "threats": ["Urban shops"],
                                    },
                                    "threats": ["Urban shops undercutting prices"],
                                    "pricing_suggestion": {
                                        "suggested_price_range": "₹150–250 per garment",
                                        "reasoning": "Aligned with local tailor rates.",
                                    },
                                }),
                            },
                        }],
                    }
                }],
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    result = analyze_feasibility(
        business_category="Tailoring",
        location_label="Sinnar, Nashik",
        context="2 tailors within 7 km; weekly haat on Friday.",
        language="en",
        client=client,
    )
    assert result["swot"]["opportunities"] == ["School uniforms"]
    assert result["pricing_suggestion"]["suggested_price_range"].startswith("₹")


def test_generate_text_raises_when_caller_expects_chat_without_key(monkeypatch):
    from app.core.config import settings
    from app.services.llm_client import chat

    monkeypatch.setattr(settings, "llm_api_key", "")
    try:
        chat("Hello")
        raise AssertionError("expected LLMNotConfigured")
    except LLMNotConfigured:
        pass
