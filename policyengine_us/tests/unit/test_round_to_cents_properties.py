"""Hypothesis checks that splitting a total into cents doesn't change a limit test.

Account balances are stored as float32, so three balances that add to a limit
in cents can sum a fraction of a cent above or below it. Asset tests round the
sum to cents before comparing it with the limit (``round_to_cents``).

The first property checks the helper alone, without a model, on both ways
the model sums inputs: float32 addition within one entity, and a float64 sum
cast back to float32 when person inputs are added up to a group entity.

The second property runs the model. Each example is one situation of
single-person households. Each household splits a total at, a cent below or
a cent above the SSI and SNAP limits among bank, stock and bond assets, and
its result must match the result for the same total held in one account.
Hypothesis is a dev extra, so this module skips without it.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.tools.general import round_to_cents

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

ACCOUNTS = ("bank_account_assets", "stock_assets", "bond_assets")

# Three float32 parts and two float32 additions each err by at most half a
# unit in the last place of the total. Below 2**14 dollars that unit is at
# most 2**-10, so the sum stays within 5 / 2**11 < 0.005 of the total.
MAX_CENTS = 2**14 * 100 - 1


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


YEAR = 2026
# 20 CFR 416.1205: the individual limit is 2,000. Everyone is 70, so SNAP
# applies its FY2026 limit for households with an elderly member, 4,500
# (7 U.S.C. 2014(g)(1)).
LIMITS = {"meets_ssi_resource_test": 2_000, "meets_snap_asset_test": 4_500}


@st.composite
def household(draw):
    test = draw(st.sampled_from(sorted(LIMITS)))
    total = LIMITS[test] * 100 + draw(st.sampled_from([-1, 0, 1]))
    return test, draw(cent_split(total))


def build_situation(households):
    people = {}
    groups = {}
    for i, (_, parts) in enumerate(households):
        for split in (False, True):
            name = f"h{i}_{'split' if split else 'whole'}"
            amounts = parts if split else (sum(parts), 0, 0)
            person = {
                "age": {YEAR: 70},
                "is_ssi_aged_blind_disabled": {YEAR: True},
            }
            for account, cents in zip(ACCOUNTS, amounts):
                person[account] = {YEAR: cents / 100}
            people[name] = person
            groups[name] = {"members": [name]}
    return {
        "people": people,
        **{
            entity: groups
            for entity in (
                "tax_units",
                "spm_units",
                "families",
                "marital_units",
                "households",
            )
        },
    }


@hypothesis.settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[
        hypothesis.HealthCheck.too_slow,
        hypothesis.HealthCheck.data_too_large,
    ],
)
@hypothesis.given(st.lists(household(), min_size=1, max_size=20))
# Hypothesis favours splits at the edges, which don't drift, so these pin
# splits whose float32 sums land above the limit: 2,000.0001 for SSI and
# 4,500.0005 for SNAP.
@hypothesis.example(
    [
        ("meets_ssi_resource_test", (17_857, 154_779, 27_364)),
        ("meets_snap_asset_test", (418_399, 3_831, 27_770)),
    ]
)
def test_split_accounts_match_one_account(households):
    simulation = Simulation(situation=build_situation(households))
    period = f"{YEAR}-01"
    results = {test: np.asarray(simulation.calculate(test, period)) for test in LIMITS}
    # People alternate whole, split, so each person's group holds only them.
    for i, (test, parts) in enumerate(households):
        whole, split = results[test][2 * i], results[test][2 * i + 1]
        assert split == whole, (test, parts)
