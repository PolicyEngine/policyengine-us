"""Leaf-input identities, worksheet semantics, and legacy-input precedence."""

import numpy as np
import pytest

from policyengine_us import Simulation

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

YEAR = 2025
LEAVES = (
    "foreign_earned_income_exclusion_amount",
    "foreign_housing_exclusion",
    "foreign_earned_income_exclusion_allocable_deductions",
    "foreign_housing_deduction",
    "foreign_earned_income_exclusion_disallowed_deductions",
)


def simulation_for_tax_units(inputs):
    """Independent single-person tax units, with uniform input presence."""
    people, tax_units, households = {}, {}, {}
    groups = {"marital_units": {}, "spm_units": {}, "families": {}}
    for index, tax_unit_inputs in enumerate(inputs):
        person = f"person_{index}"
        members = [person]
        people[person] = {
            "age": {YEAR: 40},
            "irs_gross_income": {YEAR: 50_000},
        }
        tax_units[f"tax_unit_{index}"] = {
            "members": members,
            **tax_unit_inputs,
        }
        households[f"household_{index}"] = {
            "members": members,
            "state_code": {YEAR: "MA", YEAR + 1: "MA"},
        }
        for name in groups:
            groups[name][f"{name}_{index}"] = {"members": members}
    return Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            **groups,
        }
    )


def leaf_simulation(rows):
    return simulation_for_tax_units(
        [{name: {YEAR: value} for name, value in zip(LEAVES, row)} for row in rows]
    )


@hypothesis.settings(max_examples=5, deadline=None, derandomize=True)
@hypothesis.example([(-10_000, 1_000, 0, 0, 0), (8_000, 2_000, 1_000, 500, 700)])
@hypothesis.given(
    st.lists(
        st.tuples(
            st.integers(-100_000, 150_000),
            st.integers(-100_000, 150_000),
            st.integers(0, 100_000),
            st.integers(0, 100_000),
            st.integers(0, 100_000),
        ),
        min_size=1,
        max_size=8,
    )
)
def test_gross_sum_and_nonnegative_massachusetts_addback(rows):
    simulation = leaf_simulation(rows)
    amounts = np.asarray(rows, dtype=float)
    gross = amounts[:, 0] + amounts[:, 1]
    section_911 = gross - amounts[:, 2] + amounts[:, 3]
    federal = np.maximum(0, section_911 - amounts[:, 4])
    np.testing.assert_array_equal(
        simulation.calculate("foreign_earned_income_exclusion_gross", YEAR),
        gross,
    )
    addback = simulation.calculate("ma_foreign_earned_income_exclusion_addback", YEAR)
    np.testing.assert_array_equal(addback, np.maximum(0, gross))
    assert (addback >= 0).all()
    np.testing.assert_array_equal(
        simulation.calculate("foreign_earned_income_exclusion", YEAR), federal
    )
    # MAGI adds Form 2555 lines 45 and 50, before worksheet line 2b.
    np.testing.assert_array_equal(
        simulation.calculate("section_911_excluded_income", YEAR), section_911
    )


@pytest.mark.parametrize(
    "first",
    [
        "foreign_earned_income_exclusion_gross",
        "foreign_earned_income_exclusion_amount",
        "foreign_housing_exclusion",
    ],
)
def test_explicit_zero_leaves_are_period_specific_and_ignore_default_caches(first):
    simulation = simulation_for_tax_units(
        [
            {
                "foreign_earned_income_exclusion": {
                    YEAR: 9_000,
                    YEAR + 1: 11_000,
                },
                "foreign_earned_income_exclusion_amount": {YEAR + 1: 0},
                "foreign_housing_exclusion": {YEAR + 1: 0},
            }
        ]
    )
    # Computing an unset leaf or the gross formula in another period must
    # not turn its default zero into an explicitly supplied leaf input.
    simulation.calculate(first, YEAR)
    simulation.calculate(first, YEAR + 1)
    np.testing.assert_array_equal(
        simulation.calculate("foreign_earned_income_exclusion", YEAR), [9_000]
    )
    np.testing.assert_array_equal(
        simulation.calculate("foreign_earned_income_exclusion", YEAR + 1),
        [11_000],
    )
    np.testing.assert_array_equal(
        simulation.calculate("ma_foreign_earned_income_exclusion_addback", YEAR),
        [9_000],
    )
    np.testing.assert_array_equal(
        simulation.calculate("ma_foreign_earned_income_exclusion_addback", YEAR + 1),
        [0],
    )


@pytest.mark.parametrize("entered", [0, 6_000])
def test_set_input_marks_a_leaf_explicit_after_its_default_was_cached(entered):
    simulation = simulation_for_tax_units(
        [{"foreign_earned_income_exclusion": {YEAR: 10_000}}]
    )
    np.testing.assert_array_equal(
        simulation.calculate("foreign_housing_exclusion", YEAR), [0]
    )
    simulation.set_input(
        "foreign_housing_exclusion", YEAR, np.array([entered], dtype=float)
    )
    np.testing.assert_array_equal(
        simulation.calculate("foreign_earned_income_exclusion_gross", YEAR),
        [entered],
    )
    np.testing.assert_array_equal(
        simulation.calculate("ma_foreign_earned_income_exclusion_addback", YEAR),
        [entered],
    )
    np.testing.assert_array_equal(
        simulation.calculate("foreign_earned_income_exclusion", YEAR), [10_000]
    )


def expected_legacy_carry(simulation, entered):
    # The original pure dollar input used default uprating, then the system
    # converted that national total to its per-capita series. Adding a
    # formula must preserve the projected value.
    parameters = simulation.tax_benefit_system.parameters
    before = parameters(
        str(YEAR)
    ).calibration.gov.cbo.income_by_source.adjusted_gross_income_per_capita
    after = parameters(
        str(YEAR + 1)
    ).calibration.gov.cbo.income_by_source.adjusted_gross_income_per_capita
    return np.array([entered], dtype=np.float32) * (after / before)


@pytest.mark.parametrize("legacy", [0, 10_000, -5_000])
def test_legacy_aggregate_keeps_its_existing_carry_over(legacy):
    simulation = simulation_for_tax_units(
        [{"foreign_earned_income_exclusion": {YEAR: legacy}}]
    )
    expected = expected_legacy_carry(simulation, legacy)
    np.testing.assert_array_equal(
        simulation.calculate("foreign_earned_income_exclusion", YEAR + 1),
        expected,
    )
    np.testing.assert_array_equal(
        simulation.calculate("ma_foreign_earned_income_exclusion_addback", YEAR + 1),
        np.maximum(0, expected),
    )


def test_carried_leaf_inputs_keep_gross_and_federal_net_distinct():
    simulation = leaf_simulation([(8_000, 2_000, 1_000, 0, 0)])
    federal = simulation.calculate("foreign_earned_income_exclusion", YEAR + 1)
    earned = simulation.calculate("foreign_earned_income_exclusion_amount", YEAR + 1)
    housing = simulation.calculate("foreign_housing_exclusion", YEAR + 1)
    deductions = simulation.calculate(
        "foreign_earned_income_exclusion_allocable_deductions", YEAR + 1
    )
    gross = earned + housing
    np.testing.assert_array_equal(federal, gross - deductions)
    np.testing.assert_array_equal(
        simulation.calculate("foreign_earned_income_exclusion_gross", YEAR + 1), gross
    )
    np.testing.assert_array_equal(
        simulation.calculate("ma_foreign_earned_income_exclusion_addback", YEAR + 1),
        gross,
    )
    assert (gross > federal).all()


def test_future_leaf_inputs_do_not_replace_legacy_carry():
    simulation = simulation_for_tax_units(
        [
            {
                "foreign_earned_income_exclusion": {YEAR: 10_000},
                "foreign_earned_income_exclusion_amount": {YEAR + 2: 20_000},
            }
        ]
    )
    expected = expected_legacy_carry(simulation, 10_000)
    np.testing.assert_array_equal(
        simulation.calculate("foreign_earned_income_exclusion", YEAR + 1), expected
    )
    np.testing.assert_array_equal(
        simulation.calculate("ma_foreign_earned_income_exclusion_addback", YEAR + 1),
        expected,
    )


@hypothesis.settings(max_examples=3, deadline=None, derandomize=True)
@hypothesis.given(st.integers(1, 150_000), st.integers(0, 150_000))
def test_form_2555_filers_skip_worksheet_b_even_when_stacking_is_zero(amount, excess):
    simulation = simulation_for_tax_units(
        [
            {
                "foreign_earned_income_exclusion_amount": {YEAR: amount},
                "foreign_earned_income_exclusion_allocable_deductions": {
                    YEAR: amount + excess
                },
                "ctc_qualifying_children": {YEAR: 1},
            }
        ]
    )
    np.testing.assert_array_equal(
        simulation.calculate("foreign_earned_income_exclusion", YEAR), [0]
    )
    np.testing.assert_array_equal(
        simulation.calculate("ctc_credit_limit_worksheet_b_applies", YEAR), [False]
    )
