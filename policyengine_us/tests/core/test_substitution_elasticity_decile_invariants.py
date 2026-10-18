"""Invariants of the earnings deciles behind primary earners' substitution elasticity.

CBO sets primary earners' substitution elasticities by earnings decile, from
the lowest decile to the highest, where "a decile includes 10 percent of
earners" (How the Supply of Labor Responds to Changes in Fiscal Policy, 2012,
Table 1). The parameter file holds one value per decile, primary.1 (lowest)
to primary.10 (highest). substitution_elasticity places a primary earner in a
decile using ten earnings markers, each the lowest earnings in its decile.
For every earnings amount:

1. The amount falls in exactly one decile from 1 to 10, and the parameter file
   defines a primary-earner value for each of those deciles.
2. The decile never falls as earnings rise.
3. A nonnegative amount is at or above its decile's marker and below the next
   marker. Decile 10 has no upper limit.
4. The vectorised lookup agrees with a scalar statement of rule 3, in the
   float32 the model computes in as well as in float64.

substitution_elasticity.yaml checks that the formula gives each primary earner
its decile's parameter. These checks build no model.
"""

from pathlib import Path

import numpy as np
import pytest
import yaml
from hypothesis import example, given
from hypothesis import strategies as st

from policyengine_us.variables.gov.simulation.labor_supply_response.substitution_elasticity import (
    EARNINGS_DECILE_MARKERS,
    earnings_decile,
)

PARAMETER_FILE = (
    Path(__file__).parents[2]
    / "parameters/gov/simulation/labor_supply_responses/elasticities/substitution.yaml"
)
PRIMARY = yaml.safe_load(PARAMETER_FILE.read_text())["by_position_and_decile"][
    "primary"
]
DEFINED_DECILES = {key for key in PRIMARY if key != "metadata"}
LAST_DECILE = len(EARNINGS_DECILE_MARKERS)

# Each marker, and amounts just either side of it.
EDGES = sorted(
    {
        marker + offset
        for marker in EARNINGS_DECILE_MARKERS
        for offset in (-1, -0.01, 0, 0.01, 1)
    }
)
amounts = st.one_of(st.floats(allow_nan=False), st.sampled_from(EDGES))


def reference_decile(amount):
    """The highest decile whose marker is at or below the amount.

    An amount below the first marker, which earnings never are, is in decile 1.
    """
    decile = 1
    for number, marker in enumerate(EARNINGS_DECILE_MARKERS, start=1):
        if amount >= marker:
            decile = number
    return decile


def test_parameter_file_defines_one_value_per_decile():
    assert DEFINED_DECILES == set(range(1, LAST_DECILE + 1))


def test_markers_rise_from_zero():
    assert EARNINGS_DECILE_MARKERS[0] == 0
    assert all(np.diff(EARNINGS_DECILE_MARKERS) > 0)


@given(amounts)
@example(0)
@example(13_999)
@example(1_726_000)
@example(5_000_000)
def test_every_amount_falls_in_one_defined_decile(amount):
    deciles = earnings_decile(np.array([amount]))
    assert deciles.shape == (1,)
    assert int(deciles[0]) in DEFINED_DECILES


@given(amounts, amounts)
def test_decile_never_falls_as_earnings_rise(first, second):
    lower, higher = sorted([first, second])
    assert earnings_decile(lower) <= earnings_decile(higher)


@given(st.one_of(st.floats(min_value=0, allow_nan=False), st.sampled_from(EDGES)))
@example(1)
@example(13_999)
@example(14_000)
@example(1_725_999)
@example(1_726_000)
def test_nonnegative_amount_lies_in_its_decile(amount):
    if amount < 0:
        return
    decile = int(earnings_decile(amount))
    assert EARNINGS_DECILE_MARKERS[decile - 1] <= amount
    if decile < LAST_DECILE:
        assert amount < EARNINGS_DECILE_MARKERS[decile]


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
@given(values=st.lists(amounts, max_size=50))
def test_vectorised_lookup_matches_scalar_rule(dtype, values):
    with np.errstate(over="ignore"):
        earnings = np.array(values, dtype=dtype)
    expected = [reference_decile(float(amount)) for amount in earnings]
    assert earnings_decile(earnings).tolist() == expected
