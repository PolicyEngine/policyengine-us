"""Check household isolation and retain the dataset allocation equations.

Python checks the same generated situations in household and dataset mode;
policy YAML cannot exercise that simulation contract.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation


YEAR = 2026
AVERAGE = "medicaid_slcsp_state_average_cost_index"
FILLED = "medicaid_slcsp_cost_index_filled"
DENOMINATOR = "medicaid_slcsp_state_denominator"
VALUE = "medicaid_cost_if_enrolled"
OUTPUTS = (AVERAGE, FILLED, DENOMINATOR, VALUE)
PERSON = st.tuples(st.integers(0, 1_000), st.integers(0, 10_000), st.booleans())
HOUSEHOLD = st.tuples(
    st.sampled_from(["TX", "NY", "CO"]), st.lists(PERSON, min_size=1, max_size=3)
)


def _situation(households):
    people = {}
    groups = {}
    for household_index, (state, members) in enumerate(households):
        names = []
        for member_index, (index, weight, enrolled) in enumerate(members):
            name = f"person_{household_index}_{member_index}"
            names.append(name)
            people[name] = {
                "age": {YEAR: 40},
                "medicaid_slcsp_cost_index": {YEAR: index},
                "person_weight": {YEAR: weight},
                "medicaid_enrolled": {YEAR: enrolled},
            }
        groups[f"household_{household_index}"] = {
            "members": names,
            "state_code": {YEAR: state},
        }
    return {
        "people": people,
        "households": groups,
        **{
            group: {name: {"members": [name]} for name in people}
            for group in ("tax_units", "spm_units", "families", "marital_units")
        },
    }


@pytest.mark.parametrize("dataset", [False, True])
@settings(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@example(
    households=[
        # Fractional weights: (0.5*100 + 1.5*300)/(0.5+1.5) = 250.
        ("TX", [(100, 0.5, True), (300, 1.5, False), (0, 2.5, True)]),
        ("TX", [(900, 1.25, True)]),
    ]
)
@example(
    households=[
        # Household mean = (1*100 + 3*300)/(1+3) = 250.
        # Dataset TX mean = (100 + 900 + 1,800)/6 = 2,800/6;
        # enrolled denominator = 5*(2,800/6) + 100 + 1,800 = 12,700/3.
        ("TX", [(0, 5, True), (100, 1, True), (300, 3, False)]),
        ("TX", [(900, 2, True)]),
        ("NY", [(0, 1, True)]),
        ("CO", [(200, 0, False)]),
    ]
)
@given(households=st.lists(HOUSEHOLD, min_size=2, max_size=4))
def test_household_isolation_preserves_dataset_allocation(households, dataset):
    simulation = Simulation(situation=_situation(households))
    simulation.is_over_dataset = dataset
    if not dataset:
        local = {name: simulation.calculate(name, YEAR).copy() for name in OUTPUTS}
        separate = {name: [] for name in OUTPUTS}
        for household in households:
            alone = Simulation(situation=_situation([household]))
            for name in OUTPUTS:
                separate[name].extend(alone.calculate(name, YEAR))
        for name in OUTPUTS:
            np.testing.assert_array_equal(local[name], separate[name], err_msg=name)
        return

    # Dataset mode must keep the original state equations, including missing
    # indices, zero weights, unenrolled people and states without enrollees.
    indices = simulation.calculate("medicaid_slcsp_cost_index", YEAR)
    weights = simulation.calculate("person_weight", YEAR)
    enrolled = simulation.calculate("medicaid_enrolled", YEAR)
    states = np.array([state for state, members in households for _ in members])
    average = np.ones_like(indices)
    denominator = np.zeros_like(indices)
    p = simulation.tax_benefit_system.parameters(
        str(YEAR)
    ).calibration.gov.hhs.medicaid.totals
    spending = np.array([p.spending[str(state)] for state in states])
    for state in set(states):
        in_state = states == state
        state_weights = weights[in_state]
        state_indices = indices[in_state]
        positive = state_indices > 0
        positive_weight = (state_weights * positive).sum()
        if positive_weight > 0:
            average[in_state] = (
                state_weights * state_indices * positive
            ).sum() / positive_weight
    filled = np.where(indices > 0, indices, average)
    for state in set(states):
        in_state = states == state
        denominator[in_state] = (
            weights[in_state] * filled[in_state] * enrolled[in_state]
        ).sum()
    expected = {
        AVERAGE: average,
        FILLED: filled,
        DENOMINATOR: denominator,
        VALUE: np.divide(
            spending * filled,
            denominator,
            out=np.zeros_like(denominator),
            where=denominator > 0,
        ),
    }
    for name in OUTPUTS:
        np.testing.assert_array_equal(
            simulation.calculate(name, YEAR), expected[name], err_msg=name
        )
