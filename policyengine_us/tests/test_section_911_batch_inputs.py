"""Public simulation batches must preserve each tax unit's input representation.

Python coverage exercises JSON provenance and the Simulation constructor, which
the YAML runner's Core SimulationBuilder does not exercise.
"""

from copy import deepcopy

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.tests.test_foreign_earned_income_exclusion_leaves import (
    LEAVES,
    YEAR,
    simulation_for_tax_units,
)

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

OUTPUTS = (
    "foreign_earned_income_exclusion",
    "section_911_excluded_income",
    "foreign_earned_income_exclusion_gross",
    "ma_foreign_earned_income_exclusion_addback",
    "ma_gross_income",
)


@pytest.fixture(scope="module")
def scalar_period_situation():
    # Reuse only the raw entity layout, with independent dictionaries per case.
    return simulation_for_tax_units([{}, {}]).situation_input


@pytest.mark.parametrize("constructor_style", ["keyword", "positional"])
@pytest.mark.parametrize("other_period", [YEAR, YEAR + 1])
def test_scalar_leaf_period_matches_constructor_default_input_period(
    scalar_period_situation, constructor_style, other_period
):
    situation = deepcopy(scalar_period_situation)
    situation["tax_units"]["tax_unit_0"]["foreign_earned_income_exclusion_amount"] = (
        8_000
    )
    situation["tax_units"]["tax_unit_1"]["foreign_earned_income_exclusion_amount"] = {
        other_period: 2_000
    }

    def construct():
        if constructor_style == "keyword":
            return Simulation(situation=situation, default_input_period=YEAR)
        # Core's default_input_period is its seventh positional argument.
        return Simulation(None, None, situation, None, None, False, YEAR)

    if other_period != YEAR:
        with pytest.raises(ValueError, match=r"(?i)(batch|tax.unit)"):
            construct()
    else:
        simulation = construct()
        for variable in (
            "foreign_earned_income_exclusion",
            "section_911_excluded_income",
            "ma_foreign_earned_income_exclusion_addback",
        ):
            np.testing.assert_array_equal(
                simulation.calculate(variable, YEAR), [8_000, 2_000]
            )


@pytest.mark.parametrize(
    "inputs",
    [
        [
            {"foreign_earned_income_exclusion": {YEAR: 10_000}},
            {
                "foreign_earned_income_exclusion_amount": {YEAR: 8_000},
                "foreign_housing_exclusion": {YEAR: 2_000},
            },
        ],
        [
            {"foreign_earned_income_exclusion": {YEAR: 0}},
            {"foreign_earned_income_exclusion_amount": {YEAR: 10_000}},
        ],
        [
            {
                "foreign_earned_income_exclusion": {YEAR: 10_000},
                "foreign_housing_exclusion": {YEAR: 0},
            },
            {"foreign_earned_income_exclusion": {YEAR: 20_000}},
        ],
    ],
    ids=["aggregate-and-leaves", "explicit-zero-aggregate", "explicit-zero-leaf"],
)
def test_mixed_tax_unit_representations_raise_a_clear_error(inputs):
    # Core fills omitted entity inputs with zeros. A global leaf switch or
    # aggregate input array would silently replace one unit's own amounts.
    with pytest.raises(ValueError, match=r"(?i)(batch|tax.unit)"):
        simulation_for_tax_units(inputs)


@pytest.mark.parametrize("with_aggregate", [False, True])
def test_temporally_mixed_leaf_components_raise_despite_matching_union_coverage(
    with_aggregate,
):
    inputs = [
        {
            "foreign_earned_income_exclusion_amount": {YEAR: 1_000},
            "foreign_housing_exclusion": {YEAR + 1: 100},
        },
        {
            "foreign_earned_income_exclusion_amount": {YEAR + 1: 2_000},
            "foreign_housing_exclusion": {YEAR: 200},
        },
    ]
    if with_aggregate:
        for row in inputs:
            row["foreign_earned_income_exclusion"] = {YEAR: 10_000}
    # Each unit supplies some leaf in both years, but the later arrays zero-fill
    # the other unit's carried amount for each individual component.
    with pytest.raises(ValueError, match=r"(?i)(batch|tax.unit)"):
        simulation_for_tax_units(inputs)


def assert_batch_matches_individual_tax_units(inputs):
    """Changing population composition cannot change a unit's own results."""
    batch = simulation_for_tax_units(inputs)
    individuals = [simulation_for_tax_units([row]) for row in inputs]
    for period in (YEAR, YEAR + 1):
        for variable in OUTPUTS:
            expected = np.array(
                [
                    simulation.calculate(variable, period)[0]
                    for simulation in individuals
                ]
            )
            np.testing.assert_array_equal(batch.calculate(variable, period), expected)


@hypothesis.settings(max_examples=3, deadline=None, derandomize=True)
@hypothesis.example([0, 10_000, -5_000])
@hypothesis.given(st.lists(st.integers(-100_000, 150_000), min_size=2, max_size=4))
def test_uniform_legacy_batches_match_isolated_tax_units(values):
    assert_batch_matches_individual_tax_units(
        [{"foreign_earned_income_exclusion": {YEAR: value}} for value in values]
    )


@hypothesis.settings(max_examples=3, deadline=None, derandomize=True)
@hypothesis.example([(0, 0, 0, 0, 0), (8_000, 2_000, 1_000, 500, 700)])
@hypothesis.given(
    st.lists(
        st.tuples(
            st.integers(-100_000, 150_000),
            st.integers(-100_000, 150_000),
            st.integers(0, 100_000),
            st.integers(0, 100_000),
            st.integers(0, 100_000),
        ),
        min_size=2,
        max_size=4,
    )
)
def test_uniform_leaf_batches_match_isolated_tax_units(rows):
    assert_batch_matches_individual_tax_units(
        [{name: {YEAR: value} for name, value in zip(LEAVES, row)} for row in rows]
    )


def test_leaf_batches_can_supply_different_form_2555_components():
    assert_batch_matches_individual_tax_units(
        [
            {"foreign_earned_income_exclusion_amount": {YEAR: 8_000}},
            {"foreign_housing_exclusion": {YEAR: 2_000}},
            {"foreign_housing_deduction": {YEAR: 0}},
        ]
    )


def test_none_does_not_turn_a_legacy_unit_into_a_leaf_unit():
    assert_batch_matches_individual_tax_units(
        [
            {
                "foreign_earned_income_exclusion": {YEAR: 10_000},
                "foreign_housing_exclusion": {YEAR: None},
            },
            {"foreign_earned_income_exclusion": {YEAR: 20_000}},
        ]
    )


def test_uniform_aggregate_overrides_with_explicit_zero_leaves_remain_valid():
    assert_batch_matches_individual_tax_units(
        [
            {
                "foreign_earned_income_exclusion": {YEAR: 10_000},
                "foreign_housing_exclusion": {YEAR: 0},
            },
            {
                "foreign_earned_income_exclusion": {YEAR: 20_000},
                "foreign_housing_exclusion": {YEAR: 2_000},
            },
        ]
    )
