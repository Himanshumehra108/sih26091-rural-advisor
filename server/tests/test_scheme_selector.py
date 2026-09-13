from app.core.constants import MICRO_FINANCE_SCHEME
from app.services.scheme_selector import select_scheme


def test_cutoff_uses_micro_finance():
    # available_margin at exactly 10% of the cutoff project cost
    margin_at_cutoff = MICRO_FINANCE_SCHEME["max_project_cost"] * 0.10
    assert select_scheme(margin_at_cutoff)['scheme_name'] == 'Micro Finance Scheme'