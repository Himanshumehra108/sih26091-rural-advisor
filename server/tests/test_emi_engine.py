from app.services.emi_engine import calculate_emi_schedule


def test_zero_rate_emi():
    result = calculate_emi_schedule(1200, 0, 12)
    assert result['monthly_emi'] == 100
