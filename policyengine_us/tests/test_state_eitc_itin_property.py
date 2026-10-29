"""Hypothesis checks for the Maryland and Maine EITC waivers of 26 U.S.C. 32(m).

The invariants and helpers are in test_state_eitc_itin.py. Hypothesis is a dev
extra, so this module skips without it.
"""

import pytest

from test_state_eitc_itin import ID_TYPES, STATES, check

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

household_strategy = st.fixed_dictionaries(
    {
        "state": st.sampled_from(STATES),
        "head_age": st.integers(18, 80),
        "spouse_age": st.integers(18, 80),
        "head_id": st.sampled_from(ID_TYPES),
        "spouse_id": st.one_of(st.none(), st.sampled_from(ID_TYPES)),
        # Children are aged 3, 7 and 11 (see build_situation).
        "child_ids": st.lists(st.sampled_from(ID_TYPES), max_size=3),
        "wages": st.integers(0, 60_000),
        "exclusion": st.one_of(st.just(0), st.integers(1, 60_000)),
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
    st.sampled_from([2019, 2020, 2021, 2022, 2025, 2026]),
)
def test_random_households(households, year):
    check(households, year)
