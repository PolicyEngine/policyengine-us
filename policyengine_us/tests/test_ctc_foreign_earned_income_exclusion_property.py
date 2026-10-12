"""Hypothesis checks for the section 911 bar on the refundable Child Tax Credit.

The invariants and helpers are in test_ctc_foreign_earned_income_exclusion.py.
Hypothesis is a dev extra, so this module skips without it.
"""

import pytest

from test_ctc_foreign_earned_income_exclusion import check

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

household_strategy = st.fixed_dictionaries(
    {
        "married": st.booleans(),
        # Age 17 at most: the model treats an unmarried filer's 18-year-old
        # as a spouse.
        "dependent_ages": st.lists(st.integers(0, 17), max_size=4),
        "wages": st.integers(0, 500_000),
        "exclusion": st.one_of(st.just(0), st.integers(1, 130_000)),
    }
)


@hypothesis.settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[
        hypothesis.HealthCheck.too_slow,
        hypothesis.HealthCheck.data_too_large,
    ],
)
@hypothesis.given(
    st.lists(household_strategy, min_size=1, max_size=25),
    st.sampled_from([2018, 2022, 2025, 2026]),
)
def test_random_households(households, year):
    check(households, year)
