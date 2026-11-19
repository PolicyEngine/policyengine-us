"""Joint itemization stays isolated by branch and tax year."""

from math import isclose, isfinite

import numpy as np
import pytest
from hypothesis import assume, example, given, settings, strategies as st
from microdf import MicroSeries
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.tools.state_itemization import choose_joint_itemization


@settings(max_examples=32)
@given(
    offsets=st.lists(
        st.lists(
            st.sampled_from((None, 0, 0.004, 0.009, 0.01, 0.010001, 0.018, 1)),
            min_size=4,
            max_size=4,
        ),
        min_size=3,
        max_size=3,
    ),
    preferences=st.tuples(st.booleans(), st.booleans(), st.booleans()),
)
@example(
    offsets=[[0, None, 0.018, 0.009], [None, 0, 0.018, 0], [None, None, 0, 0]],
    preferences=(True, False, True),
)
def test_joint_election_uses_the_global_absolute_tie_window(offsets, preferences):
    assume(all(any(offset is not None for offset in row) for row in offsets))
    # Include refunds and a large liability, where a relative tolerance could
    # incorrectly admit a candidate more than one cent above the global minimum.
    costs = np.array(
        [
            [np.inf if offset is None else base + offset for offset in row]
            for base, row in zip((-250.0, 10_000_000.0, 900.0), offsets, strict=True)
        ]
    )
    federal_methods = (False, False, True, True)
    expected = []
    for row, preferred in zip(costs, preferences, strict=True):
        minimum = min(cost for cost in row if isfinite(cost))
        tied = [
            index
            for index, cost in enumerate(row)
            if isclose(cost, minimum, rel_tol=0.0, abs_tol=0.01)
        ]
        expected.append(
            min(tied, key=lambda index: (federal_methods[index] != preferred, index))
        )
    np.testing.assert_array_equal(
        choose_joint_itemization(costs.T, federal_methods, preferences), expected
    )


def test_joint_election_requires_a_finite_choice_for_every_unit():
    with pytest.raises(ValueError, match="legal finite deduction election"):
        choose_joint_itemization(
            np.array([[0.0, np.inf], [1.0, np.inf]]), (False, True), [False, True]
        )


def test_joint_election_accepts_microsimulation_federal_tie_preferences():
    preferences = MicroSeries([False, True, False], weights=[2, 8, 15])
    costs = np.array([[10.0, 10.0, 10.0], [10.0, 10.0, 9.0]])
    np.testing.assert_array_equal(
        choose_joint_itemization(costs, (False, True), preferences), [0, 1, 1]
    )


def test_warm_joint_choice_is_recomputed_for_a_filed_election_in_a_branch():
    # The policy examples cover the tax arithmetic. This test exercises the
    # ordinary runtime after two years of results have already been cached.
    years = (2024, 2025)
    simulation = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": dict.fromkeys(years, 40),
                    "employment_income": dict.fromkeys(years, 150_000),
                    "deductible_mortgage_interest": dict.fromkeys(years, 13_500),
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "state_and_local_sales_or_income_tax": dict.fromkeys(years, 2_500),
                },
            },
            "households": {
                "household": {
                    "members": ["person1"],
                    "state_code": dict.fromkeys(years, "DC"),
                }
            },
        }
    )
    simulation.apply_reform(
        Reform.from_dict(
            {"gov.simulation.joint_federal_state_itemization": {"2025": True}}
        )
    )
    default_policy = Simulation.default_tax_benefit_system_instance.parameters(
        "2025-01-01"
    )
    assert not default_policy.gov.simulation.joint_federal_state_itemization
    baseline_2024 = simulation.calculate("federal_state_income_tax", 2024)

    # Query the state side first. The joint choice is for both taxes, so it
    # must also be available when state liability triggers the calculation.
    np.testing.assert_allclose(simulation.calculate("state_income_tax", 2025), [9_875])
    np.testing.assert_array_equal(
        simulation.calculate("tax_unit_itemizes", 2025), [False]
    )
    np.testing.assert_array_equal(
        simulation.calculate("state_deduction_method", 2025).decode_to_str(),
        ["STANDARD"],
    )

    alternate = simulation.get_branch("filed_federal_itemized_return")
    alternate.set_input("tax_unit_itemizes", 2025, [True])
    np.testing.assert_allclose(
        alternate.calculate("state_income_tax", 2025), [10_002.50]
    )
    np.testing.assert_array_equal(
        alternate.calculate("state_deduction_method", 2025).decode_to_str(),
        ["ITEMIZED"],
    )
    np.testing.assert_allclose(alternate.calculate("income_tax", 2025), [25_007])
    np.testing.assert_allclose(
        simulation.calculate("federal_state_income_tax", 2025), [34_942]
    )
    np.testing.assert_array_equal(
        alternate.calculate("federal_state_income_tax", 2024), baseline_2024
    )
