import pytest

from policyengine_us import Simulation


def test_il_ccap_table_b_exact_seasonal_boundaries():
    simulation = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2026": 30},
                },
            },
            "spm_units": {
                "spm_unit": {
                    "members": ["person1"],
                    "il_ccap_countable_income": {
                        "2026-05": 1_000,
                        "2026-06": 1_000,
                        "2026-08": 1_000,
                        "2026-09": 1_000,
                    },
                    "spm_unit_fpg": {"2026": 12_000},
                    "spm_unit_size": {"2026": 2},
                    "il_ccap_all_children_school_age_part_day": {
                        "2026-05": True,
                        "2026-06": True,
                        "2026-08": True,
                        "2026-09": True,
                    },
                },
            },
            "households": {
                "household": {
                    "members": ["person1"],
                    "state_code": {"2026": "IL"},
                },
            },
        },
    )

    # Table B applies through May and resumes in September. June-August
    # use Table A. At/below FPL, Table A is $1 and Table B is $0.50.
    expected_copays = {
        "2026-05": 0.5,
        "2026-06": 1,
        "2026-08": 1,
        "2026-09": 0.5,
    }
    for period, expected in expected_copays.items():
        result = simulation.calculate("il_ccap_copay", period)[0]
        assert result == pytest.approx(expected, abs=0.01)
