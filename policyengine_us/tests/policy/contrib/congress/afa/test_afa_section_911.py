"""Exercise section 911 through the production AFA activation path.

The neighboring YAML policy tests apply structural reforms directly. This
integration test uses Reform.from_dict to verify that enabling AFA updates
the shared bar, retains its pre-2025 formula, and reaches the Puerto Rico
credit consumer after AFA's fully-refundable parameter expires in 2039.
"""

import pytest
from policyengine_core.reforms import Reform

from policyengine_us import Simulation


YEARS = (2024, 2025, 2039, 2040)
BAR = "refundable_ctc_barred_by_section_911_exclusion"
CREDITS = ("refundable_ctc", "pr_refundable_ctc")


def test_afa_activation_preserves_section_911_rules_across_years():
    members = ["parent", "child"]
    situation = {
        "people": {
            "parent": {
                "age": {str(year): 40 for year in YEARS},
                "employment_income": {str(year): 8_000 for year in YEARS},
            },
            "child": {"age": {str(year): 5 for year in YEARS}},
        },
        "tax_units": {
            "tax_unit": {
                "members": members,
                "foreign_earned_income_exclusion": {str(year): 1_000 for year in YEARS},
            }
        },
        "spm_units": {"spm_unit": {"members": members}},
        "households": {
            "household": {
                "members": members,
                "state_code": {str(year): "PR" for year in YEARS},
            }
        },
    }
    # Two independent simulations cover every year without repeated model
    # construction or mutable caches shared between current law and AFA.
    baseline = Simulation(situation=situation)
    for year in YEARS:
        assert baseline.calculate(BAR, year)[0]
        for credit in CREDITS:
            assert baseline.calculate(credit, year)[0] == 0

    reform = Reform.from_dict(
        {"gov.contrib.congress.afa.in_effect": {"2025-01-01.2100-12-31": True}},
        country_id="us",
    )
    afa = Simulation(situation=situation, reform=reform)
    # AFA applies to taxable years beginning after December 31, 2024.
    assert afa.calculate(BAR, 2024)[0]
    for year in (2025, 2039, 2040):
        assert not afa.calculate(BAR, year)[0]
        # Section 32(c)(1)(C) continues to deny EITC under AFA.
        assert afa.calculate("eitc", year)[0] == 0
        expected = 825 if year == 2040 else afa.calculate("ctc", year)[0]
        assert expected > 0
        for credit in CREDITS:
            assert afa.calculate(credit, year)[0] == pytest.approx(expected)
