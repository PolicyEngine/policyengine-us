"""Check school-meal take-up across generated SPM units.

Core applies defined_for masks to SPM-unit calculations.
Hypothesis checks those masks across mixed group sizes and participation
settings, including omitted inputs, in one vectorized simulation per example.
YAML covers the fixed policy amounts.

Each simulation has private entities and calculation holders. The tests reuse
the policy system without changing its variables or parameters.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

BENEFITS = (
    "school_meal_net_subsidy",
    "free_school_meals",
    "reduced_price_school_meals",
)
TIERS = (
    "school_meal_tier",
    "school_meal_breakfast_tier",
    "school_meal_lunch_tier",
)
TAKEUP = (None, True, False)
TOLERANCE = 0.01

households = st.tuples(
    st.sampled_from(["AK", "HI", "CA", "FL", "NH", "NJ", "TX", "UT"]),
    st.integers(min_value=0, max_value=500).map(lambda ratio: ratio / 100),
    st.booleans(),
    st.lists(st.integers(min_value=0, max_value=22), max_size=4).map(
        lambda ages: (35, *ages)
    ),
)


def _situation(rows, year):
    situation = {
        name: {}
        for name in (
            "people",
            "spm_units",
            "households",
            "tax_units",
            "families",
            "marital_units",
        )
    }
    for row, (state, ratio, categorical, ages) in enumerate(rows):
        for variant, takes_up in enumerate(TAKEUP):
            unit = f"unit_{row}_{variant}"
            members = []
            for member, age in enumerate(ages):
                person = f"person_{row}_{variant}_{member}"
                members.append(person)
                situation["people"][person] = {"age": {year: age}}
                situation["marital_units"][person] = {"members": [person]}
            for group in ("spm_units", "households", "tax_units", "families"):
                situation[group][unit] = {"members": list(members)}
            situation["households"][unit]["state_code"] = {year: state}
            spm_unit = situation["spm_units"][unit]
            spm_unit["school_meal_fpg_ratio"] = {year: ratio}
            spm_unit["meets_school_meal_categorical_eligibility"] = {year: categorical}
            if takes_up is not None:
                spm_unit["takes_up_school_meals_if_eligible"] = {year: takes_up}
    return situation


def _main_amounts(rows, year, breakfast_tier, lunch_tier):
    # Preserve the annual arithmetic from main at 935b24ff4f022e0548876c0bd859195c517a23bb.
    # Compute each meal separately to check the share-based benefit split.
    p = system.parameters(year).gov.usda.school_meals
    expected = {name: [] for name in BENEFITS}
    for (state, _, _, ages), breakfast, lunch in zip(rows, breakfast_tier, lunch_tier):
        state_group = state if state in ("AK", "HI") else "CONTIGUOUS_US"
        breakfast_rates = p.amount.sbp[state_group]
        lunch_rates = p.amount.nslp[state_group]
        breakfast_value = breakfast_rates[str(breakfast)] - breakfast_rates.PAID
        lunch_value = lunch_rates[str(lunch)] - lunch_rates.PAID
        child_days = sum(5 <= age <= 17 for age in ages) * p.school_days
        expected["school_meal_net_subsidy"].append(
            (breakfast_value + lunch_value) * child_days
        )
        expected["free_school_meals"].append(
            (
                (breakfast_value if breakfast == "FREE" else 0)
                + (lunch_value if lunch == "FREE" else 0)
            )
            * child_days
        )
        expected["reduced_price_school_meals"].append(
            (
                (breakfast_value if breakfast == "REDUCED" else 0)
                + (lunch_value if lunch == "REDUCED" else 0)
            )
            * child_days
        )
    return expected


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    year=st.sampled_from([2020, 2024, 2025, 2026]),
    drawn=st.lists(households, max_size=6),
)
def test_school_meal_takeup_preserves_defaults_and_masks_each_spm_unit(year, drawn):
    rows = [
        # New Hampshire covers the breakfast copay but keeps reduced-price lunch.
        ("NH", 1.8, False, (35, 10)),
        ("FL", 1.8, False, (35, 5, 17)),
        ("FL", 0.5, False, (35, 11)),
        ("CA", 4.0, False, (40,)),
        ("FL", 1.8, False, (35, 4, 18)),
        ("FL", 4.0, False, (35, 10)),
        ("AK", 0.5, False, (40, 6, 10)),
        ("HI", 1.8, False, (40, 8)),
        *drawn,
    ]
    simulation = Simulation(
        tax_benefit_system=system,
        situation=_situation(rows, year),
    )
    participation = simulation.calculate("takes_up_school_meals_if_eligible", year)
    np.testing.assert_array_equal(
        participation.reshape(-1, 3),
        np.tile([True, True, False], (len(rows), 1)),
    )

    tiers = {}
    for variable in TIERS:
        values = simulation.calculate(variable, year).decode_to_str().reshape(-1, 3)
        np.testing.assert_array_equal(values[:, 0], values[:, 1])
        np.testing.assert_array_equal(values[:, 0], values[:, 2])
        tiers[variable] = values[:, 0]
    assert tiers["school_meal_breakfast_tier"][0] == "FREE"
    assert tiers["school_meal_lunch_tier"][0] == "REDUCED"

    for variable in ("school_meal_daily_subsidy", "school_meal_paid_daily_subsidy"):
        values = simulation.calculate(variable, year).reshape(-1, 3)
        np.testing.assert_array_equal(values[:, 0], values[:, 1])
        np.testing.assert_array_equal(values[:, 0], values[:, 2])

    expected = _main_amounts(
        rows,
        year,
        tiers["school_meal_breakfast_tier"],
        tiers["school_meal_lunch_tier"],
    )
    amounts = {}
    for variable in BENEFITS:
        values = simulation.calculate(variable, year).reshape(-1, 3)
        np.testing.assert_array_equal(values[:, 0], values[:, 1])
        np.testing.assert_allclose(
            values[:, 0], expected[variable], rtol=0, atol=TOLERANCE
        )
        np.testing.assert_array_equal(values[:, 2], 0)
        assert (values >= 0).all()
        assert (values[:, 2] <= values[:, 1]).all()
        # Adult-only units and children outside the K-12 age range get no meals.
        np.testing.assert_array_equal(values[3:5], 0)
        amounts[variable] = values

    np.testing.assert_allclose(
        amounts["free_school_meals"] + amounts["reduced_price_school_meals"],
        amounts["school_meal_net_subsidy"],
        rtol=0,
        atol=TOLERANCE,
    )
    assert amounts["free_school_meals"][0, 0] > 0
    assert amounts["reduced_price_school_meals"][0, 0] > 0
