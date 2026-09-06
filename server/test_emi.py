# server/test_emi.py

from app.services.emi_engine import calculate_quarterly_emi

result = calculate_quarterly_emi(
    loan_amount=900000,
    annual_interest_rate=8.0,
    tenure_years=7,
    moratorium_months=6,
)

print("Quarterly EMI:", result["quarterly_emi"])
print("Moratorium quarters:", result["moratorium_quarters"])
print("Repayment quarters:", result["repayment_quarters"])
print("Total interest:", result["total_interest"])
print("Total repayment:", result["total_repayment"])
print("\nFirst 3 schedule entries:")
for row in result["schedule"][:3]:
    print(row)