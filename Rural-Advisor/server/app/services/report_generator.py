from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.schemas.advisory import FeasibilityRequest, ReportOutput, SWOTResponse
from app.services.llm_client import LLMError, analyze_feasibility, is_configured


@dataclass
class AdvisoryReport:
    query: str
    scheme_name: str | None
    summary: str
    eligible: bool | None
    key_deadline: str | None
    sources: list[str] = field(default_factory=list)
    confidence: str = "grounded"
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "scheme_name": self.scheme_name,
            "summary": self.summary,
            "eligible": self.eligible,
            "key_deadline": self.key_deadline,
            "sources": self.sources,
            "confidence": self.confidence,
            "generated_at": self.generated_at,
        }

    def to_display_text(self) -> str:
        lines = []
        if self.scheme_name:
            lines.append(f"**{self.scheme_name}**")
        lines.append(self.summary)
        if self.eligible is not None:
            lines.append(f"Eligibility: {'Likely eligible' if self.eligible else 'May not be eligible'} based on what's available.")
        if self.key_deadline:
            lines.append(f"Deadline: {self.key_deadline}")
        if self.sources:
            lines.append(f"Source(s): {', '.join(self.sources)}")
        return "\n\n".join(lines)


def from_structured_result(query: str, structured: dict) -> AdvisoryReport:
    return AdvisoryReport(
        query=query,
        scheme_name=structured.get("scheme_name"),
        summary=structured.get("answer_summary", ""),
        eligible=structured.get("eligible"),
        key_deadline=structured.get("key_deadline"),
        sources=structured.get("sources") or [],
        confidence="grounded",
    )


def from_free_text(query: str, text: str, sources: list[str]) -> AdvisoryReport:
    return AdvisoryReport(
        query=query,
        scheme_name=None,
        summary=text,
        eligible=None,
        key_deadline=None,
        sources=sources,
        confidence="grounded",
    )


def from_no_context_fallback(query: str, fallback_text: str) -> AdvisoryReport:
    return AdvisoryReport(
        query=query,
        scheme_name=None,
        summary=fallback_text,
        eligible=None,
        key_deadline=None,
        sources=[],
        confidence="no_context",
    )


def generate_report(request: FeasibilityRequest) -> ReportOutput:
    title = f"{request.business_type} feasibility report"
    if not is_configured():
        return ReportOutput(title=title, summary="", swot=SWOTResponse())

    try:
        analysis = analyze_feasibility(
            business_category=request.business_type,
            location_label=request.location,
            context=f"Available capital: ₹{request.available_capital}",
        )
    except LLMError:
        return ReportOutput(title=title, summary="", swot=SWOTResponse())

    swot_data = analysis.get("swot") or {}
    return ReportOutput(
        title=title,
        summary=str(analysis.get("opportunity_analysis") or ""),
        swot=SWOTResponse(
            strengths=list(swot_data.get("strengths") or []),
            weaknesses=list(swot_data.get("weaknesses") or []),
            opportunities=list(swot_data.get("opportunities") or []),
            threats=list(swot_data.get("threats") or []),
        ),
    )
