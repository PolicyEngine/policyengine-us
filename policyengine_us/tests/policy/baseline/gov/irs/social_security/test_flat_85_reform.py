import pytest
from policyengine_us import Microsimulation
import numpy as np


def test_flat_85_percent_ss_taxation():
    """Test that minimal parametric reform achieves flat 85% SS taxation."""

    # Create reform with 3 parameter changes
    reform = {
        "gov.irs.social_security.taxability.combined_income_ss_fraction": {
            "2024-01-01": 1.0  # Change from 0.5 to 1.0
        },
        "gov.irs.social_security.taxability.threshold.base.main.SINGLE": {
            "2024-01-01": 0  # Change from 25000 to 0
        },
        "gov.irs.social_security.taxability.threshold.adjusted_base.main.SINGLE": {
            "2024-01-01": 0  # Change from 34000 to 0
        },
    }

    # Test with various SS benefit amounts
    test_cases = [
        (10_000, 8_500),   # 85% of 10k
        (20_000, 17_000),  # 85% of 20k
        (40_000, 34_000),  # 85% of 40k
        (50_000, 42_500),  # 85% of 50k
    ]

    for ss_benefit, expected_taxable in test_cases:
        # Create a simple single-person simulation
        sim = Microsimulation(reform=reform)

        # Find a single person tax unit
        single_mask = sim.calculate("filing_status", 2024) == "SINGLE"
        if not single_mask.any():
            continue

        # Get the first single filer
        person_id = np.where(single_mask)[0][0]

        # Set their SS benefits
        sim.set_input("social_security", 2024, ss_benefit, entity_id=person_id)
        sim.set_input("interest_income", 2024, 0, entity_id=person_id)

        # Calculate taxable SS
        taxable_ss = sim.calculate("tax_unit_taxable_social_security", 2024)[person_id]

        # Check that it equals 85% of benefits
        assert abs(taxable_ss - expected_taxable) < 1, (
            f"SS benefits {ss_benefit:,} should have taxable amount {expected_taxable:,}, "
            f"but got {taxable_ss:,.0f}"
        )


def test_parametric_reform_parameters_exist():
    """Test that all 5 separated parameters exist and have correct values."""
    from policyengine_us.system import system

    params = system.parameters(2024).gov.irs.social_security.taxability.rate

    # Check all 5 parameters exist with correct values
    assert params.tier1_benefit_cap == 0.5
    assert params.tier1_excess == 0.5
    assert params.tier1_bracket == 0.5
    assert params.tier2_excess == 0.85
    assert params.tier2_benefit_cap == 0.85