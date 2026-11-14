"""Exhaustive checks of Head Start and school meal qualifying months.

One simulation holds every pattern of SNAP receipt over the twelve months of
2025 (4,096 patterns) at two incomes: one at the paid school meal tier and
one at the reduced-price tier. Each family has a parent, a five-year-old (of
Head Start age and in school) and a one-year-old (of Early Head Start age).
SNAP is the only assistance, so a family qualifies for Head Start and for
free school meals only in the months from its first month of SNAP.

Invariants:
- Months: a family with SNAP qualifies from its first month of SNAP through
  December, 12 - (first month's index) months, so later months never matter
  and adding a month of SNAP never lowers the count.
- Head Start and Early Head Start: the value is the full-year value times
  months / 12, and zero without SNAP.
- School meals: each value is the value without categorical eligibility
  plus months / 12 of the gain from a full year of it.
- Accounting: free plus reduced-price meals equal the net subsidy.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2025
MONTHS = [f"{YEAR}-{month:02d}" for month in range(1, 13)]
PATTERNS = np.arange(2**12)
# Earnings for three people at about 300% and 160% of the 2025 poverty
# guideline ($26,650): the paid and reduced-price school meal tiers.
INCOMES = [80_000, 42_640]
COUNT = len(INCOMES) * len(PATTERNS)
MEMBERS = ["parent", "child", "infant"]


def build_simulation():
    """Copy one family along an axis, then set each copy's income and SNAP."""
    situation = {
        "people": {
            "parent": {"age": {YEAR: 30}},
            "child": {"age": {YEAR: 5}},
            "infant": {"age": {YEAR: 1}},
        },
        "spm_units": {"spm_unit": {"members": MEMBERS}},
        "tax_units": {"tax_unit": {"members": MEMBERS}},
        "families": {"family": {"members": MEMBERS}},
        # Each person is a marital unit of one.
        "marital_units": {
            f"{person}_marital_unit": {"members": [person]} for person in MEMBERS
        },
        "households": {"household": {"members": MEMBERS, "state_code": {YEAR: "GA"}}},
        "axes": [
            [
                {
                    "name": "employment_income",
                    "min": 0,
                    "max": COUNT - 1,
                    "count": COUNT,
                    "period": YEAR,
                }
            ]
        ],
    }
    simulation = Simulation(situation=situation)
    # One copy per income and pattern, incomes outermost.
    income = np.repeat(INCOMES, len(PATTERNS)).astype(float)
    pattern = np.tile(PATTERNS, len(INCOMES))
    parent = np.tile([True, False, False], COUNT)
    simulation.set_input(
        "employment_income", YEAR, np.where(parent, np.repeat(income, 3), 0)
    )
    # SNAP is the only assistance.
    simulation.set_input("tanf", YEAR, np.zeros(COUNT))
    for index, month in enumerate(MONTHS):
        simulation.set_input("snap", month, 100.0 * (pattern >> index & 1))
        simulation.set_input("ssi", month, np.zeros(3 * COUNT))
    return simulation


def expected_months(pattern):
    """12 minus the index of the first month of SNAP; 12 without SNAP."""
    pattern = int(pattern)
    if pattern == 0:
        return 12
    first = (pattern & -pattern).bit_length() - 1
    return 12 - first


@pytest.fixture(scope="module")
def results():
    simulation = build_simulation()
    # The axis lays out each copy's parent, child and infant in turn, and
    # SPM units in copy order.
    age = np.asarray(simulation.calculate("age", YEAR))
    np.testing.assert_array_equal(age, np.tile([30, 5, 1], COUNT))
    spm_unit_of_person = simulation.populations["spm_unit"].members_entity_id
    np.testing.assert_array_equal(spm_unit_of_person, np.repeat(np.arange(COUNT), 3))

    def person(variable, role):
        return np.asarray(simulation.calculate(variable, YEAR))[role::3]

    def spm_unit(variable):
        return np.asarray(simulation.calculate(variable, YEAR))

    values = {
        "head_start_months": person("head_start_qualifying_months", 1),
        "early_head_start_months": person("head_start_qualifying_months", 2),
        "head_start": person("head_start", 1),
        "early_head_start": person("early_head_start", 2),
        "school_meal_months": spm_unit("school_meal_categorical_eligibility_months"),
        "free": spm_unit("free_school_meals"),
        "reduced": spm_unit("reduced_price_school_meals"),
        "net": spm_unit("school_meal_net_subsidy"),
        "daily": spm_unit("school_meal_daily_subsidy"),
    }
    # One row per income, one column per pattern.
    return {
        name: array.reshape(len(INCOMES), len(PATTERNS))
        for name, array in values.items()
    }


EXPECTED = np.array([expected_months(pattern) for pattern in PATTERNS])
HAS_SNAP = PATTERNS > 0
FULL_YEAR = PATTERNS == 2**12 - 1


def test_head_start_months_start_at_the_first_month_of_snap(results):
    for name in ["head_start_months", "early_head_start_months"]:
        for row in results[name]:
            np.testing.assert_array_equal(row, EXPECTED)


def test_adding_a_month_of_snap_never_lowers_the_months(results):
    # Families without SNAP do not qualify, so their months stay out.
    for months in results["head_start_months"]:
        for index in range(12):
            with_month = PATTERNS[HAS_SNAP] | (1 << index)
            assert (months[with_month] >= months[HAS_SNAP]).all()


def test_head_start_values_are_the_full_year_value_times_months(results):
    for name in ["head_start", "early_head_start"]:
        for row in results[name]:
            full = row[FULL_YEAR][0]
            assert full > 0
            expected = np.where(HAS_SNAP, full * EXPECTED / 12, 0)
            np.testing.assert_allclose(row, expected, rtol=1e-6, atol=1e-6)


def test_school_meal_months_match_head_start_months(results):
    for row in results["school_meal_months"]:
        np.testing.assert_array_equal(row, np.where(HAS_SNAP, EXPECTED, 0))


@pytest.mark.parametrize("name", ["free", "reduced", "net", "daily"])
def test_school_meal_values_weight_the_year_by_months(results, name):
    for row in results[name]:
        without = row[0]
        full_year = row[FULL_YEAR][0]
        share = np.where(HAS_SNAP, EXPECTED / 12, 0)
        expected = without + share * (full_year - without)
        np.testing.assert_allclose(row, expected, rtol=1e-6, atol=1e-6)


def test_free_and_reduced_meals_add_up_to_the_net_subsidy(results):
    np.testing.assert_allclose(
        results["free"] + results["reduced"], results["net"], rtol=1e-6, atol=1e-6
    )


def test_full_year_and_no_snap_values_match_the_2025_rates(results):
    # The weighting test anchors on these values, so check them against the
    # calendar 2025 contiguous rates: breakfast FREE 2.37, REDUCED 2.07, PAID
    # 0.39; lunch FREE 4.43, REDUCED 4.03, PAID 0.42; 180 school days. They
    # also guard the setup: without SNAP, the first income pays full price
    # and the second pays the reduced price.
    free_year = (2.37 - 0.39 + 4.43 - 0.42) * 180
    reduced_year = (2.07 - 0.39 + 4.03 - 0.42) * 180
    np.testing.assert_allclose(
        results["free"][:, FULL_YEAR].ravel(), [free_year, free_year], rtol=1e-6
    )
    np.testing.assert_allclose(results["free"][:, 0], [0, 0], atol=1e-6)
    np.testing.assert_allclose(results["reduced"][:, 0], [0, reduced_year], rtol=1e-6)
    np.testing.assert_allclose(
        results["daily"][:, 0], [0.39 + 0.42, 2.07 + 4.03], rtol=1e-6
    )
