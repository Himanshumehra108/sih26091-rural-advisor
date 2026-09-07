from app.schemas.advisory import FeasibilityRequest, ReportOutput, SWOTResponse
from app.services.llm_client import LLMError, analyze_feasibility, is_configured


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
