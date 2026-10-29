"""Hypothesis checks for Maine's childless EITC age expansion.

The invariants and helpers are in test_me_childless_eitc_age_gate.py.
Hypothesis is a dev extra, so this module skips without it.
"""

import pytest

from test_me_childless_eitc_age_gate import check

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

# Filers are 18 or older: the model makes a married 17-year-old a dependent,
# not a spouse. The YAML cases and the under-18 witness cover age 17. The
# fractional ages test "has not attained 25". None falls between 64 and 65:
# the federal test (eitc_demographic_eligible, unchanged here) compares the
# exact age with 64, and the oracle copies it.
fractional_ages = st.sampled_from([18.5, 23.5, 24.5, 24.99])
spouse_strategy = st.fixed_dictionaries(
    {
        "age": st.one_of(st.integers(18, 80), fractional_ages),
        "student": st.booleans(),
        "wages": st.one_of(st.just(0), st.integers(1, 20_000)),
        "ssn": st.booleans(),
    }
)

household_strategy = st.fixed_dictionaries(
    {
        # Mostly Maine's 18-24 range, sometimes any age.
        "head_age": st.one_of(
            st.integers(18, 24), st.integers(18, 80), fractional_ages
        ),
        "head_student": st.booleans(),
        "spouse": st.one_of(st.none(), spouse_strategy),
        # Age 17 at most: the model treats an unmarried filer's 18-year-old
        # as a spouse.
        "child_ages": st.one_of(st.just([]), st.lists(st.integers(0, 17), max_size=2)),
        "wages": st.integers(0, 40_000),
        "unemployment": st.one_of(st.just(0), st.integers(1, 20_000)),
        "interest": st.one_of(st.just(0), st.integers(1, 20_000)),
        "ssn": st.booleans(),
        "claimed": st.booleans(),
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
    st.lists(household_strategy, min_size=1, max_size=20),
    st.sampled_from([2020, 2021, 2022, 2025, 2026]),
)
def test_random_households(households, year):
    check(households, year)
