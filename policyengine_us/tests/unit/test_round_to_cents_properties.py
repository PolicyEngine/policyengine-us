"""Hypothesis check that splitting a total into cents doesn't change a limit test.

Account balances are stored as float32, so three balances that add to a limit
in cents can sum a fraction of a cent above or below it. Asset tests round the
sum to cents before comparing it with the limit (``round_to_cents``).

The property checks the helper alone, without a model, on both ways the model
sums inputs: float32 addition within one entity, and a float64 sum cast back
to float32 when person inputs are added up to a group entity. The YAML cases
at each fixed limit check the model. Hypothesis is a dev extra, so this module
skips without it.
"""

import numpy as np
import pytest

from policyengine_us.tools.general import round_to_cents

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

# Three float32 parts and two float32 additions each err by at most half a
# unit in the last place of the total. Below 2**15 dollars a half unit is at
# most 2**-10, so the sum stays within 5 / 2**10 < 0.005 of the total.
MAX_CENTS = 2**15 * 100 - 1


@st.composite
def cent_split(draw, total_cents):
    """Three whole-cent parts that add to total_cents."""
    cuts = sorted(draw(st.integers(0, total_cents)) for _ in range(2))
    return (cuts[0], cuts[1] - cuts[0], total_cents - cuts[1])


@st.composite
def total_and_split(draw):
    total = draw(st.integers(0, MAX_CENTS))
    return total, draw(cent_split(total))


@hypothesis.settings(max_examples=2_000, deadline=None)
@hypothesis.given(total_and_split())
def test_rounded_sum_of_float32_parts_is_the_total(case):
    total, parts = case
    values = [np.float32(part / 100) for part in parts]
    # Float32 addition, as a formula adding one entity's own inputs.
    float32_sum = values[0] + values[1] + values[2]
    # A float64 sum stored as float32, as an aggregate to a group entity.
    float64_sum = np.float32(sum(float(value) for value in values))
    for amount in (float32_sum, float64_sum):
        assert round_to_cents(amount) == total / 100
