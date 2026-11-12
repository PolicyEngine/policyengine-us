"""Check population independence through Core's masks and entity projectors.

YAML covers payment amounts. Hypothesis varies states, household membership,
tax units, income, bills and child care ratings, then compares each household
with its results in isolation. Fresh simulations share the default US system;
they keep their own inputs and calculation caches. This file runs in the
existing rest-python core group.
"""

import numpy as np
from hypothesis import example, given, settings, strategies as st

from policyengine_us import Simulation
from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)

YEAR = 2026
STATES = tuple(state.name for state in StateCode)[:51]
OUTPUTS = (
    "dc_liheap_payment",
    "il_liheap_base_payment",
    "il_liheap",
    "il_ihwap_categorically_eligible",
    "il_ihwap_eligible",
    "la_school_readiness_credit",
    "la_school_readiness_credit_non_refundable",
    "la_school_readiness_credit_refundable",
)


@st.composite
def households(draw):
    return (
        draw(st.sampled_from(STATES)),
        draw(
            st.lists(
                st.tuples(
                    st.integers(0, 2),  # children per tax unit
                    st.integers(0, 100_000),  # adult earnings
                    st.integers(0, 5_000),  # heating bill
                    st.integers(0, 500),  # child care credit
                    st.integers(1, 5),  # facility rating
                ),
                min_size=1,
                max_size=2,
            )
        ),
    )


def _calculate(households):
    situation = {
        group: {}
        for group in (
            "people",
            "marital_units",
            "tax_units",
            "families",
            "spm_units",
            "households",
        )
    }
    for i, (state, tax_units) in enumerate(households):
        household_members = []
        for j, (children, earnings, bill, credit, rating) in enumerate(tax_units):
            adult = f"adult_{i}_{j}"
            members = [adult] + [f"child_{i}_{j}_{k}" for k in range(children)]
            household_members.extend(members)
            for member in members:
                situation["people"][member] = {
                    "age": {YEAR: 40 if member == adult else 3},
                    "employment_income": {YEAR: earnings if member == adult else 0},
                    "heating_expense_person": {YEAR: bill if member == adult else 0},
                    "la_quality_rating_of_child_care_facility": {YEAR: rating},
                }
                situation["marital_units"][member] = {"members": [member]}
            situation["tax_units"][f"tax_unit_{i}_{j}"] = {
                "members": members,
                "la_refundable_cdcc": {YEAR: credit},
                "la_non_refundable_cdcc": {YEAR: 0},
            }
        for group in ("families", "spm_units", "households"):
            situation[group][f"{group}_{i}"] = {"members": household_members}
        situation["households"][f"households_{i}"]["state_code"] = {YEAR: state}
    simulation = Simulation(situation=situation)
    return {name: simulation.calculate(name, YEAR).copy() for name in OUTPUTS}


@settings(max_examples=8, deadline=None, derandomize=True, database=None)
@example(population=[(state, [(1, 0, 2_000, 50, 5)]) for state in STATES])
@example(
    population=[
        ("DC", [(0, 0, 2_000, 0, 1)]),
        ("IL", [(0, 0, 2_000, 0, 1)]),
        ("LA", [(1, 0, 0, 50, 5), (0, 40_000, 0, 120, 4)]),
        ("LA", [(2, 30_000, 0, 75, 3)]),
        ("NY", [(0, 0, 0, 0, 1)]),
    ]
)
@given(population=st.lists(households(), min_size=1, max_size=5))
def test_households_keep_their_results_in_any_state_mix(population):
    combined = _calculate(population)
    isolated = [_calculate([household]) for household in population]
    for name in OUTPUTS:
        expected = np.concatenate([result[name] for result in isolated])
        np.testing.assert_array_equal(combined[name], expected, err_msg=name)
