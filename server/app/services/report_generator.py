from app.schemas.advisory import FeasibilityRequest, ReportOutput, SWOTResponse


def generate_report(request: FeasibilityRequest) -> ReportOutput:
    return ReportOutput(title=f'{request.business_type} feasibility report', summary='', swot=SWOTResponse())
