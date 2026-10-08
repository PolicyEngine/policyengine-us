"""Keep calculation-order coverage in Python; policy examples live in YAML."""

import pytest

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM


def test_medicare_part_b_premium_does_not_depend_on_calculation_order():
    no_msp_eligibility = {
        f"{year}-{month:02d}": False
        for year in ("2025", "2026")
        for month in range(1, 13)
    }
    situation = {
        "people": {
            "person": {
                "age": {"2025": 65, "2026": 66},
                "is_medicare_eligible": {"2025": True, "2026": True},
                "medicare_enrolled": {"2025": True, "2026": True},
                "gross_medicare_part_b_premium": {"2025": 2_220, "2026": 2_220},
                "base_part_b_premium": {"2025": 2_220, "2026": 2_220},
                "msp_income_eligible": no_msp_eligibility,
                "msp_asset_eligible": no_msp_eligibility,
            }
        },
        "households": {"household": {"members": ["person"]}},
        "tax_units": {"tax_unit": {"members": ["person"]}},
        "spm_units": {"spm_unit": {"members": ["person"]}},
        "families": {"family": {"members": ["person"]}},
        "marital_units": {"marital_unit": {"members": ["person"]}},
    }

    ordered_sim = Simulation(tax_benefit_system=SYSTEM, situation=situation)
    ordered_sim.calculate("medicare_part_b_premium", "2025")
    ordered_result = ordered_sim.calculate("medicare_part_b_premium", "2026")[0]

    fresh_sim = Simulation(tax_benefit_system=SYSTEM, situation=situation)
    fresh_result = fresh_sim.calculate("medicare_part_b_premium", "2026")[0]

    assert ordered_result == pytest.approx(fresh_result)
    assert ordered_result == pytest.approx(2_220)
