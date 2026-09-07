from app.core.constants import MARGIN_CUTOFF
from app.services.scheme_selector import select_scheme


def test_cutoff_uses_micro_finance():
    assert select_scheme(MARGIN_CUTOFF)['name'] == 'Micro Finance'
