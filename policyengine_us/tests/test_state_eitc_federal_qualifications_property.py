"""Hypothesis checks for state EITCs that recompute or replace the federal credit.

The invariants and helpers are in test_state_eitc_federal_qualifications.py.
Hypothesis is a dev extra, so this module skips without it.
"""

import pytest

from test_state_eitc_federal_qualifications import STATES, check

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

household_strategy = st.fixed_dictionaries(
    {
        "state": st.sampled_from(STATES),
        "head_age": st.integers(18, 80),
        "spouse_age": st.one_of(st.none(), st.integers(18, 80)),
        # Age 17 at most: the model treats an unmarried filer's 18-year-old
        # as a spouse.
        "child_ages": st.lists(st.integers(0, 17), max_size=3),
        "student": st.booleans(),
        "wages": st.integers(0, 60_000),
        "unemployment": st.one_of(st.just(0), st.integers(1, 30_000)),
        "exclusion": st.one_of(st.just(0), st.integers(1, 60_000)),
        "ssn": st.booleans(),
        "takes_up": st.booleans(),
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
    st.sampled_from([2021, 2022, 2025, 2026]),
)
def test_random_households(households, year):
    check(households, year)
