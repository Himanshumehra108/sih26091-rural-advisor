# server/app/services/emi_engine.py

from typing import Dict, List


def calculate_emi_schedule(
    principal: float,
    annual_interest_rate: float,
    tenure_years: int,
) -> Dict:
    """Compatibility wrapper for the older monthly EMI contract used in tests."""
    months = max(1, tenure_years * 12)
    monthly_rate = annual_interest_rate / 100 / 12

    if monthly_rate == 0:
        monthly_emi = principal / months
    else:
        monthly_emi = (
            principal * monthly_rate * (1 + monthly_rate) ** months
        ) / (((1 + monthly_rate) ** months) - 1)

    return {
        "principal": round(principal, 2),
        "annual_interest_rate": annual_interest_rate,
        "tenure_years": tenure_years,
        "months": months,
        "monthly_emi": round(monthly_emi, 2),
    }


def calculate_quarterly_emi(
    loan_amount: float,
    annual_interest_rate: float,
    tenure_years: int,
    moratorium_months: int,
) -> Dict:
    """
    Calculates quarterly EMI using reducing balance method.
    Moratorium period is interest-only (or fully deferred, per scheme norms) —
    here we assume simple interest accrues during moratorium and is added to principal.
    """

    quarterly_rate = (annual_interest_rate / 100) / 4
    total_quarters = tenure_years * 4
    moratorium_quarters = round(moratorium_months / 3)
    repayment_quarters = total_quarters - moratorium_quarters

    if repayment_quarters <= 0:
        raise ValueError("Moratorium period cannot exceed or equal total tenure.")

    moratorium_interest = loan_amount * quarterly_rate * moratorium_quarters
    principal_after_moratorium = loan_amount + moratorium_interest

    if quarterly_rate == 0:
        emi = principal_after_moratorium / repayment_quarters
    else:
        emi = (
            principal_after_moratorium
            * quarterly_rate
            * (1 + quarterly_rate) ** repayment_quarters
        ) / (((1 + quarterly_rate) ** repayment_quarters) - 1)

    schedule = generate_amortization_schedule(
        principal_after_moratorium, quarterly_rate, repayment_quarters, emi, moratorium_quarters
    )

    total_paid = emi * repayment_quarters
    total_interest = total_paid - loan_amount

    return {
        "quarterly_emi": round(emi, 2),
        "moratorium_quarters": moratorium_quarters,
        "repayment_quarters": repayment_quarters,
        "principal_after_moratorium": round(principal_after_moratorium, 2),
        "moratorium_interest_capitalized": round(moratorium_interest, 2),
        "total_interest": round(total_interest, 2),
        "total_repayment": round(total_paid, 2),
        "schedule": schedule,
    }


def generate_amortization_schedule(
    principal: float,
    quarterly_rate: float,
    repayment_quarters: int,
    emi: float,
    moratorium_quarters: int,
) -> List[Dict]:
    """Generates quarter-by-quarter breakdown after moratorium ends."""
    schedule = []
    balance = principal

    for q in range(1, moratorium_quarters + 1):
        schedule.append({
            "quarter": q,
            "phase": "moratorium",
            "principal_paid": 0,
            "interest_paid": 0,
            "emi": 0,
            "balance": round(balance, 2),
        })

    for q in range(1, repayment_quarters + 1):
        interest_component = balance * quarterly_rate
        principal_component = emi - interest_component
        balance -= principal_component
        balance = max(balance, 0)

        schedule.append({
            "quarter": moratorium_quarters + q,
            "phase": "repayment",
            "principal_paid": round(principal_component, 2),
            "interest_paid": round(interest_component, 2),
            "emi": round(emi, 2),
            "balance": round(balance, 2),
        })

    return schedule