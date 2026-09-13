# server/app/core/constants.py

# ─── Scheme Thresholds & Rules ───────────────────────────────

MARGIN_PERCENTAGE = 0.10          # beneficiary contributes 10%
LOAN_PERCENTAGE = 0.90            # agency provides 90%

MICRO_FINANCE_SCHEME = {
    "name": "Micro Finance Scheme",
    "max_project_cost": 140000,       # ₹1.40 lakh
    "max_loan_amount": 125000,        # ₹1.25 lakh
    "interest_rate": 6.5,             # % per annum
    "tenure_years": 3,
    "moratorium_months": 3,
}

TERM_LOAN_SCHEME = {
    "name": "Term Loan Scheme",
    "min_project_cost": 140001,       # just above Micro Finance ceiling
    "max_project_cost": 5000000,      # ₹50.00 lakh
    "max_loan_amount": 4500000,       # ₹45 lakh
    "interest_rate": 8.0,             # % per annum
    "tenure_years": 7,
    "moratorium_months": 6,
}

# ─── Business Categories (for Module 1 dropdown/validation) ──

BUSINESS_CATEGORIES = [
    "Dairy",
    "Retail",
    "Textiles",
    "Food Processing",
    "Handicrafts",
    "Poultry",
    "Agriculture Inputs",
    "Tailoring",
    "Transport",
    "Other",
]

# ─── Supported Languages ──────────────────────────────────────

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    # extend based on Bhashini's supported list
}

# ─── Market Reach Defaults ─────────────────────────────────────

DEFAULT_MARKET_RADIUS_KM = 7   # midpoint of the 5-10km range specified in PS