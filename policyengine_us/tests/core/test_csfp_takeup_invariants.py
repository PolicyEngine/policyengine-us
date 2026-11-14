"""Check CSFP take-up across people and years in one vectorized simulation.

YAML covers fixed policy cases. With explicit flags for each year, Hypothesis
checks that changing one person's input changes only their payment for that
year. Each example
also compares all-true take-up with the payment before the take-up gate and
recomputes eligibility after each change to detect any take-up dependency.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = (2019, 2024, 2025, 2026)
BENEFIT = "commodity_supplemental_food_program"
ELIGIBILITY = "commodity_supplemental_food_program_eligible"
TAKEUP = "takes_up_csfp_if_eligible"

people = st.tuples(
    st.integers(0, 100),
    st.sampled_from([0.0, 0.5, 1.0, 1.3, 1.5, 2.0, 3.0]),
    st.tuples(*(st.booleans() for _ in YEARS)),
)


def _simulation(rows):
    persons = {}
    groups = {
        name: {} for name in ("tax_units", "marital_units", "spm_units", "families")
    }
    for i, (age, ratio, _) in enumerate(rows):
        person = f"person_{i}"
        persons[person] = {
            "age": {year: age for year in YEARS},
            "tx_dta_csfp_income_eligible": {year: False for year in YEARS},
            "ks_dcf_csfp_categorically_eligible": {
                f"{year}-12": False for year in YEARS
            },
        }
        for name, units in groups.items():
            units[f"{name}_{i}"] = {"members": [person]}
        groups["spm_units"][f"spm_units_{i}"]["school_meal_fpg_ratio"] = {
            year: ratio for year in YEARS
        }
    # Share a household so a household-wide take-up gate would fail.
    household = {
        "members": list(persons),
        "state_code": {year: "CA" for year in YEARS},
    }
    for name in (
        "ks_dcf_csfp_county_eligible",
        "ma_dese_csfp_county_eligible",
        "il_dhs_csfp_county_eligible",
    ):
        household[name] = {year: True for year in YEARS}
    return Simulation(
        situation={
            "people": persons,
            "households": {"household": household},
            **groups,
        }
    )


def _recalculate(simulation, year):
    # Clear both outputs to recompute eligibility after changing take-up.
    simulation.delete_arrays(BENEFIT, year)
    simulation.delete_arrays(ELIGIBILITY, year)
    eligibility = np.asarray(simulation.calculate(ELIGIBILITY, year)).copy()
    benefit = np.asarray(simulation.calculate(BENEFIT, year)).copy()
    return eligibility, benefit


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    drawn=st.lists(people, min_size=4, max_size=12),
    changed_year=st.sampled_from(YEARS),
)
def test_csfp_takeup_invariants(drawn, changed_year):
    # Anchor an eligible person and two people who fail age or income.
    rows = [
        (70, 0.0, (False, True, False, True)),
        (30, 0.0, (True, False, True, False)),
        (70, 100.0, (True, True, True, True)),
        *drawn,
    ]
    simulation = _simulation(rows)
    eligibility_before = {}
    old_payments = {}
    for year in YEARS:
        amount = simulation.tax_benefit_system.parameters(year).gov.usda.csfp.amount
        eligibility_before[year], default_benefit = _recalculate(simulation, year)
        assert eligibility_before[year][0]
        assert not eligibility_before[year][1:3].any()
        old_payments[year] = eligibility_before[year] * amount
        assert not np.asarray(simulation.calculate(TAKEUP, year)).any()
        np.testing.assert_array_equal(default_benefit, np.zeros(len(rows)))

    for year in YEARS:
        amount = simulation.tax_benefit_system.parameters(year).gov.usda.csfp.amount
        flags = np.array([row[2][YEARS.index(year)] for row in rows])
        simulation.set_input(TAKEUP, year, flags)
        eligible, benefit = _recalculate(simulation, year)
        np.testing.assert_array_equal(eligible, eligibility_before[year])
        assert (benefit >= 0).all()
        assert (benefit <= amount).all()
        assert (benefit[~flags | ~eligible] == 0).all()
        np.testing.assert_array_equal(benefit, old_payments[year] * flags)

    for year in YEARS:
        simulation.set_input(TAKEUP, year, np.ones(len(rows), dtype=bool))
        eligible, benefit = _recalculate(simulation, year)
        np.testing.assert_array_equal(eligible, eligibility_before[year])
        np.testing.assert_array_equal(benefit, old_payments[year])

    flags = np.ones(len(rows), dtype=bool)
    flags[0] = False
    simulation.set_input(TAKEUP, changed_year, flags)
    for year in YEARS:
        eligible, benefit = _recalculate(simulation, year)
        np.testing.assert_array_equal(eligible, eligibility_before[year])
        expected = old_payments[year].copy()
        if year == changed_year:
            expected[0] = 0
        np.testing.assert_array_equal(benefit, expected)
