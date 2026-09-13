# server/app/services/scheme_selector.py

from app.core.constants import (
    MARGIN_PERCENTAGE,
    LOAN_PERCENTAGE,
    MICRO_FINANCE_SCHEME,
    TERM_LOAN_SCHEME,
)


def calculate_project_cost(available_margin: float) -> float:
    """Project Cost = Available Margin / 10%"""
    return available_margin / MARGIN_PERCENTAGE


def calculate_loan_amount(project_cost: float) -> float:
    """Loan Amount = 90% of Project Cost"""
    return project_cost * LOAN_PERCENTAGE


def select_scheme(available_margin: float) -> dict:
    """
    Takes user's available margin capital, calculates project cost,
    and routes to the correct scheme.

    Logic A: project_cost <= ₹1.40L -> Micro Finance Scheme
    Logic B: ₹1.40L < project_cost <= ₹50.00L -> Term Loan Scheme
    Cap: project_cost > ₹50.00L -> capped at Term Loan Scheme ceiling
    """
    project_cost = calculate_project_cost(available_margin)

    if project_cost <= MICRO_FINANCE_SCHEME["max_project_cost"]:
        scheme = MICRO_FINANCE_SCHEME
        loan_amount = calculate_loan_amount(project_cost)
        return {
            "scheme_name": scheme["name"],
            "project_cost": round(project_cost, 2),
            "loan_amount": round(loan_amount, 2),
            "interest_rate": scheme["interest_rate"],
            "tenure_years": scheme["tenure_years"],
            "moratorium_months": scheme["moratorium_months"],
            "capped": False,
        }

    elif project_cost <= TERM_LOAN_SCHEME["max_project_cost"]:
        scheme = TERM_LOAN_SCHEME
        loan_amount = calculate_loan_amount(project_cost)
        return {
            "scheme_name": scheme["name"],
            "project_cost": round(project_cost, 2),
            "loan_amount": round(loan_amount, 2),
            "interest_rate": scheme["interest_rate"],
            "tenure_years": scheme["tenure_years"],
            "moratorium_months": scheme["moratorium_months"],
            "capped": False,
        }

    else:
        # Cap at ₹50L ceiling, per your decision earlier
        scheme = TERM_LOAN_SCHEME
        capped_project_cost = scheme["max_project_cost"]
        loan_amount = calculate_loan_amount(capped_project_cost)
        return {
            "scheme_name": scheme["name"],
            "project_cost": capped_project_cost,
            "loan_amount": round(loan_amount, 2),
            "interest_rate": scheme["interest_rate"],
            "tenure_years": scheme["tenure_years"],
            "moratorium_months": scheme["moratorium_months"],
            "capped": True,
            "original_project_cost": round(project_cost, 2),
            "message": (
                f"Your margin capital supports a project cost of "
                f"₹{round(project_cost, 2):,}, but scheme rules cap eligible "
                f"project cost at ₹{capped_project_cost:,}. Your loan is "
                f"capped at ₹{round(loan_amount, 2):,}."
            ),
        }