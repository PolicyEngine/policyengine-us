"""Optional Hypothesis properties for Maryland's capital gains surtax.

The deterministic grid and statute/form witnesses remain in the invariants
module and run without Hypothesis.
"""

import pytest

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

from policyengine_us.tests.test_md_capital_gains_surtax_invariants import (
    assert_properties,
    household,
    person,
)

GAIN = st.integers(min_value=-300_000, max_value=300_000)
DISTRIBUTIONS = st.integers(min_value=-5_000, max_value=50_000)
DIVIDENDS = st.integers(min_value=0, max_value=50_000)
WAGES = st.integers(min_value=0, max_value=800_000)


@st.composite
def random_household(draw):
    def filer(role):
        return person(
            role,
            draw(GAIN),
            draw(GAIN),
            draw(DISTRIBUTIONS),
            draw(DIVIDENDS),
            draw(WAGES),
        )

    people = [filer("head")]
    if draw(st.booleans()):
        people.append(filer("spouse"))
    for _ in range(draw(st.integers(min_value=0, max_value=2))):
        people.append(person("dependent", draw(GAIN), draw(GAIN), draw(DISTRIBUTIONS)))
    excepted = draw(st.sampled_from([0, 0, 10_000, draw(GAIN)]))
    return household(people, excepted)


@hypothesis.settings(
    max_examples=25,
    derandomize=True,
    deadline=None,
    suppress_health_check=[
        hypothesis.HealthCheck.too_slow,
        hypothesis.HealthCheck.data_too_large,
    ],
)
@hypothesis.given(
    st.lists(random_household(), min_size=1, max_size=8),
    st.integers(min_value=1, max_value=100_000),
)
def test_properties(households, delta):
    assert_properties(households, delta)
