"""Exact current-law compatibility for the shared AIME indexing helpers.

These tests use small synthetic Person arrays and annual parameter snapshots,
without constructing a model. The reference preserves the pre-extraction
algorithm, including its historical dtype promotion and absence of rounding.
"""

from types import SimpleNamespace

import numpy as np
import pytest
from policyengine_core.periods import period

from policyengine_us.tools.social_security.earnings import highest_earnings
from policyengine_us.variables.gov.ssa.social_security.ss_aime import _compute_aime


CURRENT_YEAR = 2039
AGES = (0, 21, 22, 23, 59, 60, 61, 62, 64, 65, 69, 70, 71, 95)


class AnnualPerson:
    """Return deterministic arrays with cap, loss and precision edge cases."""

    def __init__(self, ages, dtype):
        self.ages = np.asarray(ages, dtype=np.int32)
        self.count = len(ages)
        self.dtype = dtype
        self.calls = []

    def __call__(self, name, instant):
        year = instant.start.year
        self.calls.append((name, year))
        if name == "age":
            return self.ages
        index = np.arange(self.count)
        if name == "employment_income":
            amount = 19_687.33 + (year % 17) * 1_234.567 + index * 217.039
            amount *= np.where((year + index) % 11 == 0, 7, 1)
        elif name == "total_self_employment_income":
            amount = np.where((year + index) % 5 == 0, -3_456.789, 6_789.123)
        elif name == "owners_draw_credited_earnings":
            amount = np.where((year + index) % 3 == 0, 55_410.17, 0)
        else:
            raise AssertionError(name)
        return np.asarray(amount, dtype=self.dtype)


def annual_parameters(
    lookback, dtype, *, minimum_age=22, maximum_age=69, indexing_age=60, years=35
):
    aime = SimpleNamespace(
        minimum_age_for_earnings=minimum_age,
        max_earnings_age=maximum_age,
        indexing_age=indexing_age,
        years_of_earnings=years,
        months_per_year=12,
    )

    def parameters(instant):
        year = instant.start.year
        cap = 50_000 + (year - 1950) * 3_432.17
        # Integer annual inputs must retain the old integer assignment/truncation
        # behavior when the annual cap is also integral.
        if np.issubdtype(dtype, np.integer):
            cap = int(cap)
        return SimpleNamespace(
            gov=SimpleNamespace(
                simulation=SimpleNamespace(aime_lookback_years=lookback),
                ssa=SimpleNamespace(
                    nawi=19_000.123 + (year - 1950) * 837.619,
                    social_security=SimpleNamespace(wage_base=cap, aime=aime),
                ),
            )
        )

    return parameters


def legacy_aime(person, instant, parameters, additional_earnings_variable=None):
    """Independent pre-extraction window, assignment, selection and summation."""
    ages = person("age", instant)
    current_year = instant.start.year
    policy = parameters(instant).gov.ssa.social_security.aime
    indexing_years = current_year - ages + policy.indexing_age
    annual_amounts = []
    lookback = parameters(instant).gov.simulation.aime_lookback_years
    for years_ago in range(lookback + 1):
        year = current_year - years_ago
        year_ages = ages - years_ago
        eligible = (year_ages >= policy.minimum_age_for_earnings) & (
            year_ages <= policy.max_earnings_age
        )
        if not np.any(eligible):
            continue
        annual_period = instant.this_year.offset(-int(years_ago))
        total = person("employment_income", annual_period) + person(
            "total_self_employment_income", annual_period
        )
        if additional_earnings_variable is not None:
            total = total + person(additional_earnings_variable, annual_period)
        cap = parameters(annual_period).gov.ssa.social_security.wage_base
        covered = np.minimum(total, cap)
        indexed = np.zeros_like(covered)
        indexing = eligible & (year <= indexing_years)
        if np.any(indexing):
            year_nawi = parameters(annual_period).gov.ssa.nawi
            for indexing_year in np.unique(indexing_years[eligible].astype(int)):
                members = (
                    eligible & indexing & (indexing_years.astype(int) == indexing_year)
                )
                if np.any(members) and indexing_year <= current_year:
                    anchor_period = instant.this_year.offset(
                        -int(current_year - indexing_year)
                    )
                    anchor_nawi = parameters(anchor_period).gov.ssa.nawi
                    indexed[members] = covered[members] * (anchor_nawi / year_nawi)
        unindexed = eligible & (year > indexing_years)
        indexed[unindexed] = covered[unindexed]
        indexed[~eligible] = 0
        annual_amounts.append(indexed)

    matrix = (
        np.column_stack(annual_amounts)
        if annual_amounts
        else np.zeros((person.count, 1))
    )
    ordered = np.sort(matrix, axis=1)[:, ::-1]
    count = min(ordered.shape[1], policy.years_of_earnings)
    selected = ordered[:, :count]
    if count < policy.years_of_earnings:
        selected = np.hstack(
            [selected, np.zeros((person.count, policy.years_of_earnings - count))]
        )
    return np.sum(selected, axis=1) / (
        policy.years_of_earnings * policy.months_per_year
    )


def assert_exact_legacy_match(ages, dtype, lookback, additional=None, **policy):
    instant = period(str(CURRENT_YEAR))
    parameters = annual_parameters(lookback, dtype, **policy)
    old_person = AnnualPerson(ages, dtype)
    new_person = AnnualPerson(ages, dtype)
    expected = legacy_aime(old_person, instant, parameters, additional)
    actual = _compute_aime(new_person, instant, parameters, additional)
    assert actual.dtype == expected.dtype
    np.testing.assert_array_equal(actual, expected)
    # Sharing helpers must not expand the legacy earnings-input window.
    assert new_person.calls == old_person.calls


@pytest.mark.parametrize("dtype", [np.float32, np.float64, np.int32, np.int64])
@pytest.mark.parametrize("lookback", [0, 1, 10, 34, 35, 36, 50, 75])
@pytest.mark.parametrize("additional", [None, "owners_draw_credited_earnings"])
def test_shared_helpers_preserve_legacy_results_and_dtype(dtype, lookback, additional):
    assert_exact_legacy_match(AGES, dtype, lookback, additional)


@pytest.mark.parametrize(
    "ages, lookback, policy",
    [
        ((0, 1, 21, 1000), 0, {}),  # Entirely empty eligible history.
        ((22,), 0, {}),  # Minimum earnings age, future indexing anchor.
        ((69,), 0, {}),  # Maximum earnings age, unindexed earnings.
        ((70,), 1, {}),  # First included year is just before maximum age.
        ((20, 21, 22, 60, 61), 45, {"minimum_age": 21, "maximum_age": 60}),
        ((59, 60, 61, 62, 100), 75, {"indexing_age": 59, "years": 40}),
        ((65, 66), 12, {"years": 1}),
        ((65, 66), 12, {"years": 20}),
    ],
)
def test_age_boundaries_empty_careers_and_alternative_selection_windows(
    ages, lookback, policy
):
    assert_exact_legacy_match(
        ages, np.float32, lookback, "owners_draw_credited_earnings", **policy
    )


@pytest.mark.parametrize("dtype", [np.float32, np.float64, np.int32, np.int64])
def test_short_career_padding_retains_legacy_float64_promotion(dtype):
    amounts = np.arange(14, dtype=dtype).reshape(2, 7)
    expected = np.hstack([np.sort(amounts, axis=1)[:, ::-1], np.zeros((2, 28))])
    actual = highest_earnings(amounts, 35)
    assert actual.dtype == expected.dtype == np.dtype("float64")
    np.testing.assert_array_equal(actual, expected)
