"""Invariants of the car loan interest deduction (26 U.S.C. 163(h)(4)).

Section 163(h)(4)(C)(i) limits the qualified passenger vehicle loan interest
taken into account to $10,000. Section 163(h)(4)(C)(ii)(I) then reduces the
deduction "(but not below zero) by $200 for each $1,000 (or portion thereof)
by which the modified adjusted gross income of the taxpayer for the taxable
year exceeds $100,000 ($200,000 in the case of a joint return)". Schedule 1-A
(2025), lines 24-30, restate this: line 26 is "$100,000 ($200,000 if married
filing jointly)", and line 28 divides the excess by $1,000 and, if the result
isn't a whole number, increases it to the next higher whole number. The 2025
Form 1040 instructions give "All other filing statuses—$100,000", so a
surviving spouse, who does not file a joint return, uses $100,000. Section
163(h)(4) has no joint-return requirement, so separate filers may claim.

Each test call, and each Hypothesis example, builds one simulation of many tax
units, each in its own household. The tests check:

1. Seeded draws, evaluated under all five filing statuses, match an
   independent restatement of Schedule 1-A lines 24-30.
2. The deduction lies between 0 and the capped interest, and a positive
   deduction is the capped interest less a whole multiple of $200. These
   follow from 1, and are checked on the model's output directly so that an
   error in the restatement's arithmetic cannot hide them.
3. At every $1,000 step from each threshold to full phase-out, for each filing
   status and for interest below, at and above the cap: k whole steps over the
   threshold leave the capped interest less $200 per step (not below zero),
   and $1, $500 or $999 more takes another $200, because a portion of $1,000
   counts as a whole one. One dollar below the threshold the capped interest
   is left.
4. A single filer, a head of household, a separate filer and a surviving
   spouse get the same deduction at every income, and a joint return at
   modified AGI m gets what a single filer gets at m - $100,000.
5. Raising modified AGI never raises the deduction, and leaves it unchanged
   while the count of $1,000 increments (a portion rounded up) over the
   threshold is unchanged; raising the interest never lowers it (Hypothesis).

Modified AGI here is adjusted gross income with no section 911, 931 or 933
exclusions; the YAML tests cover the section 933 add-back. Incomes are whole
or quarter dollars, which float32 holds exactly at these magnitudes.
"""

import numpy as np
import pytest
from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEAR = 2025
STATUSES = ("SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE")
NON_JOINT = tuple(status for status in STATUSES if status != "JOINT")

# Schedule 1-A (2025), restated from the form rather than read from the
# parameter files. Line 24: "the smaller of the amount on line 23 or $10,000".
# Line 26: "$100,000 ($200,000 if married filing jointly)". Lines 28-29: each
# $1,000 of excess, a fraction rounded up, times $200.
CAP = 10_000
THRESHOLD = {"JOINT": 200_000}
DEFAULT_THRESHOLD = 100_000
INCREMENT = 1_000
REDUCTION = 200
# Steps that take the full cap to zero.
STEPS = CAP // REDUCTION


def _threshold(status):
    return THRESHOLD.get(status, DEFAULT_THRESHOLD)


def _increments(magi, status):
    """Lines 27-28: whole $1,000s over the threshold, a portion rounded up."""
    # Quarter dollars keep the arithmetic exact.
    excess = round(4 * magi) - 4 * _threshold(status)
    return max(-(-excess // (4 * INCREMENT)), 0)


def _schedule_1a(interest, magi, status):
    """Lines 24-30 of Schedule 1-A, restated."""
    line_24 = min(interest, CAP)
    line_29 = _increments(magi, status) * REDUCTION
    return max(line_24 - line_29, 0)


def _simulate(units):
    """One tax unit per (status, magi, interest); joint units get a spouse."""
    period = str(YEAR)
    people, tax_units, marital_units, households = {}, {}, {}, {}
    for i, (status, magi, interest) in enumerate(units):
        members = [f"head{i}"]
        if status == "JOINT":
            members.append(f"spouse{i}")
        for name in members:
            people[name] = {"age": {period: 40}}
        tax_units[f"t{i}"] = {
            "members": members,
            "filing_status": {period: status},
            "adjusted_gross_income": {period: float(magi)},
        }
        marital_units[f"m{i}"] = {"members": members}
        households[f"h{i}"] = {
            "members": members,
            "state_code": {period: "TX"},
            "qualified_passenger_vehicle_loan_interest": {period: float(interest)},
        }
    simulation = Simulation(
        tax_benefit_system=system,
        situation={
            "people": people,
            "tax_units": tax_units,
            "marital_units": marital_units,
            "households": households,
        },
    )
    magi = simulation.calculate("agi_plus_section_911_931_933_exclusions", period)
    np.testing.assert_array_equal(magi, [unit[1] for unit in units])
    return simulation.calculate("auto_loan_interest_deduction", period)


def _draw(seed, n=120):
    """Random (magi, interest) pairs concentrated around each threshold's steps."""
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(n):
        kind = rng.integers(3)
        threshold = int(rng.choice([DEFAULT_THRESHOLD, THRESHOLD["JOINT"]]))
        if kind == 0:
            magi = float(rng.integers(0, 400_001))
        elif kind == 1:
            step = threshold + INCREMENT * int(rng.integers(0, STEPS + 2))
            magi = float(step + rng.choice([-1, 0, 1, 999, 1_000]))
        else:
            # Quarter dollars from $2,000 below to $52,000 above.
            magi = threshold + int(rng.integers(-8_000, 208_001)) / 4
        interest = float(rng.choice([0, 5_000, CAP, int(rng.integers(0, 15_001))]))
        draws.append((magi, interest))
    return draws


@pytest.mark.parametrize("seed", [0, 1])
def test_deduction_matches_schedule_1a_under_every_filing_status(seed):
    units = [
        (status, magi, interest)
        for magi, interest in _draw(seed)
        for status in STATUSES
    ]
    actual = _simulate(units)
    # 1. Schedule 1-A lines 24-30.
    expected = [
        _schedule_1a(interest, magi, status) for status, magi, interest in units
    ]
    np.testing.assert_array_equal(actual, expected)

    # 2. Bounds, and whole $200 reductions from the capped interest.
    for unit, value in zip(units, actual):
        capped = min(unit[2], CAP)
        assert 0 <= value <= capped, (unit, value)
        if value > 0:
            assert (capped - value) % REDUCTION == 0, (unit, value)


def test_each_thousand_dollars_or_portion_takes_two_hundred():
    # Interest below, at and above the cap, so the walk also sees the cap and
    # that it applies before the reduction.
    interests = (5_000, CAP, 12_000)
    units, index = [], {}
    for status in STATUSES:
        threshold = _threshold(status)
        for interest in interests:
            index[(status, interest, "below")] = len(units)
            units.append((status, threshold - 1, interest))
            for k in range(STEPS + 2):
                for offset in (0, 1, 500, 999):
                    index[(status, interest, k, offset)] = len(units)
                    magi = threshold + INCREMENT * k + offset
                    units.append((status, magi, interest))
    value = _simulate(units)

    for status in STATUSES:
        for interest in interests:
            capped = min(interest, CAP)
            key = (status, interest)
            assert value[index[(*key, "below")]] == capped, key
            for k in range(STEPS + 2):
                # 3. k whole steps over the threshold take $200 each ...
                at_step = value[index[(*key, k, 0)]]
                assert at_step == max(capped - REDUCTION * k, 0), (*key, k)
                # ... and any portion of the next $1,000 takes another $200.
                for offset in (1, 500, 999):
                    assert value[index[(*key, k, offset)]] == max(
                        capped - REDUCTION * (k + 1), 0
                    ), (*key, k, offset)


def test_only_a_joint_return_has_the_higher_threshold():
    # Incomes of at least $100,000, so a single filer at m - $100,000 has a
    # nonnegative AGI.
    draws = [
        (magi if magi >= DEFAULT_THRESHOLD else magi + DEFAULT_THRESHOLD, interest)
        for magi, interest in _draw(2)
    ]
    units = []
    for magi, interest in draws:
        units.extend((status, magi, interest) for status in STATUSES)
        units.append(("SINGLE", magi - DEFAULT_THRESHOLD, interest))
    value = _simulate(units).reshape(len(draws), len(STATUSES) + 1)
    by_status = {status: value[:, i] for i, status in enumerate(STATUSES)}

    # 4. The four statuses without a joint return share every amount ...
    for status in NON_JOINT:
        np.testing.assert_array_equal(by_status[status], by_status["SINGLE"], status)
    # ... and a joint return is a single filer $100,000 lower.
    np.testing.assert_array_equal(by_status["JOINT"], value[:, -1])


thresholds = st.sampled_from([DEFAULT_THRESHOLD, THRESHOLD["JOINT"]])
magis = st.one_of(
    # On or next to a $1,000 step of either threshold.
    st.tuples(
        thresholds,
        st.integers(min_value=0, max_value=STEPS + 1),
        st.sampled_from([-1, 0, 1, 500, 999]),
    ).map(lambda t: t[0] + INCREMENT * t[1] + t[2]),
    # Anywhere in or near either phase-out range, in quarter dollars.
    st.tuples(thresholds, st.integers(min_value=-8_000, max_value=208_000)).map(
        lambda t: t[0] + t[1] / 4
    ),
    st.integers(min_value=0, max_value=400_000),
)
raises = st.one_of(
    st.integers(min_value=0, max_value=999),
    st.integers(min_value=0, max_value=4_000).map(lambda quarters: quarters / 4),
    st.integers(min_value=0, max_value=60_000),
)
interests = st.one_of(
    st.sampled_from([0, 5_000, CAP]), st.integers(min_value=0, max_value=15_000)
)
more_interest = st.integers(min_value=0, max_value=5_000)


# Each example is one simulation of 300 tax units, so a few examples keep the
# run short; shrinking is skipped and a failing example is still reported.
@settings(
    max_examples=7,
    deadline=None,
    derandomize=True,
    phases=(Phase.explicit, Phase.generate),
)
@given(
    cases=st.lists(
        st.tuples(magis, raises, interests, more_interest),
        min_size=20,
        max_size=20,
    )
)
def test_more_income_never_raises_and_more_interest_never_lowers_it(cases):
    units, same_step = [], []
    for magi, raise_by, interest, extra in cases:
        for status in STATUSES:
            units.append((status, magi, interest))
            units.append((status, magi + raise_by, interest))
            units.append((status, magi, interest + extra))
            same_step.append(
                _increments(magi, status) == _increments(magi + raise_by, status)
            )
    value = _simulate(units)
    base, richer, more = value[0::3], value[1::3], value[2::3]
    same_step = np.array(same_step)
    # 5. Non-increasing in modified AGI, and piecewise constant: equal while
    # the rounded-up increments are equal ...
    assert np.all(richer <= base)
    np.testing.assert_array_equal(richer[same_step], base[same_step])
    # ... and non-decreasing in interest.
    assert np.all(more >= base)
