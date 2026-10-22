"""Invariants of the qualified tips and overtime deductions (26 U.S.C. 224, 225).

Sections 224(b)(2)(A) and 225(b)(2)(A) reduce each deduction, after its cap,
"(but not below zero) by $100 for each $1,000 by which the taxpayer's modified
adjusted gross income exceeds $150,000 ($300,000 in the case of a joint
return)". Schedule 1-A (2025), lines 11 and 19, divide the excess by $1,000
and, if the result "isn't a whole number, decrease the result to the next
lower whole number". Sections 224(f) and 225(e) allow a married individual
either deduction only on a joint return, and the Part II and Part III cautions
say "If married, you must file jointly to claim this deduction."

Tax units share one simulation per draw. Joint returns have two spouses, so
the combined caps and the both-spouses SSN rule apply as on the return. The
tests check:

1. Every random draw, evaluated under all five filing statuses, matches an
   independent restatement of Schedule 1-A lines 7-13 (tips) and 15-21
   (overtime); married filing separately gets zero for every input.
2. Each deduction lies between 0 and its capped qualifying amount, and the
   capped amount less the deduction is a whole multiple of $100.
3. At every $1,000 step from each threshold to full phase-out, for each filing
   status that may claim: one dollar below the step and the step itself differ
   by exactly $100 (or by what is left at the last step), and the deduction is
   the same from the step to $999 above it.
4. Raising modified AGI never raises either deduction, and leaves it unchanged
   while the count of whole $1,000 increments is unchanged (Hypothesis).

Modified AGI here is adjusted gross income with no section 911, 931 or 933
exclusions; the YAML tests cover those add-backs. AGIs are whole dollars or
quarter dollars, which float32 holds exactly at these magnitudes.
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEAR = 2025
STATUSES = ("SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE")
CLAIMING = tuple(status for status in STATUSES if status != "SEPARATE")

# Schedule 1-A (2025), restated from the form rather than read from the
# parameter files. Lines 9 and 17: "$150,000 ($300,000 if married filing
# jointly)". Line 7: "the smaller of the amount on line 6 or $25,000". Line 15:
# "the smaller of the amount on line 14c or $12,500 ($25,000 if married filing
# jointly)".
THRESHOLD = {"JOINT": 300_000}
DEFAULT_THRESHOLD = 150_000
TIP_CAP = 25_000
OVERTIME_CAP = {"JOINT": 25_000}
DEFAULT_OVERTIME_CAP = 12_500
INCREMENT = 1_000
REDUCTION = 100
OUTPUTS = ("tip_income_deduction", "overtime_income_deduction")


@pytest.fixture(scope="module")
def reference_system():
    # Read-only policy source shared across simulations; each Simulation gets
    # its own entities and calculation holders.
    return system


def _threshold(status):
    return THRESHOLD.get(status, DEFAULT_THRESHOLD)


def _caps(status):
    return TIP_CAP, OVERTIME_CAP.get(status, DEFAULT_OVERTIME_CAP)


def _schedule_1a(qualifying, cap, magi, status):
    """Lines 7-13 (tips) or 15-21 (overtime) of Schedule 1-A, restated."""
    if status == "SEPARATE":
        return 0
    capped = min(qualifying, cap)  # line 7 / line 15
    excess = magi - _threshold(status)  # line 10 / line 18
    if excess <= 0:
        return capped
    increments = int(excess // INCREMENT)  # line 11 / line 19
    return max(capped - increments * REDUCTION, 0)  # lines 12-13 / 20-21


def _simulate(reference_system, units):
    """One tax unit per entry of (status, magi, head tips, spouse tips, head
    overtime, spouse overtime); joint units get a spouse, others one person."""
    period = str(YEAR)
    people, tax_units, marital_units, households = {}, {}, {}, {}
    for i, (status, magi, tips, spouse_tips, overtime, spouse_overtime) in enumerate(
        units
    ):
        members = [f"head{i}"]
        incomes = [(tips, overtime)]
        if status == "JOINT":
            members.append(f"spouse{i}")
            incomes.append((spouse_tips, spouse_overtime))
        for name, (person_tips, person_overtime) in zip(members, incomes):
            people[name] = {
                "age": {period: 40},
                "ssn_card_type": {period: "CITIZEN"},
                "treasury_tipped_occupation_code": {period: 102},
                "tip_income": {period: float(person_tips)},
                "fsla_overtime_premium": {period: float(person_overtime)},
            }
        tax_units[f"t{i}"] = {
            "members": members,
            "filing_status": {period: status},
            "adjusted_gross_income": {period: float(magi)},
        }
        marital_units[f"m{i}"] = {"members": members}
        households[f"h{i}"] = {"members": members, "state_code": {period: "TX"}}
    simulation = Simulation(
        tax_benefit_system=reference_system,
        situation={
            "people": people,
            "tax_units": tax_units,
            "marital_units": marital_units,
            "households": households,
        },
    )
    magi = simulation.calculate("agi_plus_section_911_931_933_exclusions", period)
    np.testing.assert_array_equal(magi, [unit[1] for unit in units])
    return {name: simulation.calculate(name, period) for name in OUTPUTS}


def _expected(units):
    tips, overtime = [], []
    for status, magi, head_tips, spouse_tips, head_ot, spouse_ot in units:
        tip_cap, overtime_cap = _caps(status)
        joint = status == "JOINT"
        total_tips = head_tips + (spouse_tips if joint else 0)
        total_ot = head_ot + (spouse_ot if joint else 0)
        tips.append(_schedule_1a(total_tips, tip_cap, magi, status))
        overtime.append(_schedule_1a(total_ot, overtime_cap, magi, status))
    return {"tip_income_deduction": tips, "overtime_income_deduction": overtime}


def _draw(seed, n=150):
    """Random returns concentrated around the $1,000 steps of each threshold."""
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(n):
        kind = rng.integers(3)
        threshold = rng.choice([DEFAULT_THRESHOLD, THRESHOLD["JOINT"]])
        if kind == 0:
            magi = float(rng.integers(0, 700_001))
        elif kind == 1:
            step = threshold + INCREMENT * int(rng.integers(0, 261))
            magi = float(step + rng.choice([-1, 0, 1, 999]))
        else:
            # Quarter dollars from $2,000 below to $260,000 above.
            magi = threshold + int(rng.integers(-8_000, 1_040_000)) / 4
        amounts = [
            int(rng.choice([0, 12_500, 25_000, int(rng.integers(0, 40_001))]))
            for _ in range(4)
        ]
        draws.append((magi, *amounts))
    return draws


@pytest.mark.parametrize("seed", [0, 1])
def test_deductions_match_schedule_1a_under_every_filing_status(reference_system, seed):
    draws = _draw(seed)
    units = [(status, *draw) for draw in draws for status in STATUSES]
    results = _simulate(reference_system, units)
    expected = _expected(units)
    statuses = np.array([unit[0] for unit in units])
    for name in OUTPUTS:
        actual = results[name]
        # 1. Schedule 1-A, with nothing for married filing separately.
        np.testing.assert_array_equal(actual, expected[name], err_msg=name)
        assert np.all(actual[statuses == "SEPARATE"] == 0), name

    # 2. Bounds, and whole $100 reductions from the capped amount.
    for name, cap_index in (
        ("tip_income_deduction", 0),
        ("overtime_income_deduction", 1),
    ):
        for unit, value in zip(units, results[name]):
            status, _, head_tips, spouse_tips, head_ot, spouse_ot = unit
            joint = status == "JOINT"
            qualifying = (
                head_tips + (spouse_tips if joint else 0)
                if cap_index == 0
                else head_ot + (spouse_ot if joint else 0)
            )
            capped = min(qualifying, _caps(status)[cap_index])
            assert 0 <= value <= capped, (name, unit, value)
            if status != "SEPARATE" and value > 0:
                assert (capped - value) % REDUCTION == 0, (name, unit, value)


def test_each_thousand_dollar_step_reduces_by_one_hundred(reference_system):
    units, index = [], {}
    for status in CLAIMING:
        tip_cap, overtime_cap = _caps(status)
        threshold = _threshold(status)
        steps = max(tip_cap, overtime_cap) // REDUCTION + 1
        for k in range(steps + 1):
            for offset in (-1, 0, 999):
                index[(status, k, offset)] = len(units)
                head_ot = overtime_cap if status != "JOINT" else overtime_cap // 2
                spouse_ot = overtime_cap - head_ot
                # Joint returns split tips and overtime between the spouses, so
                # the combined caps bind.
                head_tips = tip_cap if status != "JOINT" else 10_000
                spouse_tips = tip_cap - head_tips
                magi = threshold + INCREMENT * k + offset
                units.append((status, magi, head_tips, spouse_tips, head_ot, spouse_ot))
    results = _simulate(reference_system, units)

    for status in CLAIMING:
        for name, cap in zip(OUTPUTS, _caps(status)):
            value = results[name]
            steps = max(_caps(status)) // REDUCTION + 1
            for k in range(steps + 1):
                at_step = value[index[(status, k, 0)]]
                below = value[index[(status, k, -1)]]
                top = value[index[(status, k, 999)]]
                # 3. The amount after k whole increments, flat across the
                # step, and a drop of $100 (or what is left) into it.
                assert at_step == max(cap - REDUCTION * k, 0), (status, name, k)
                assert top == at_step, (status, name, k)
                drop = 0 if k == 0 else min(REDUCTION, below)
                assert below - at_step == drop, (status, name, k)


magis = st.one_of(
    st.integers(min_value=0, max_value=700_000),
    st.integers(min_value=0, max_value=2_800_000).map(lambda quarters: quarters / 4),
)
amounts = st.integers(min_value=0, max_value=40_000)


@settings(max_examples=6, deadline=None, derandomize=True)
@given(
    cases=st.lists(
        st.tuples(magis, st.integers(min_value=0, max_value=60_000), amounts, amounts),
        min_size=20,
        max_size=20,
    )
)
def test_more_income_never_raises_either_deduction(reference_system, cases):
    units = []
    for magi, raise_by, tips, overtime in cases:
        for status in STATUSES:
            for income in (magi, magi + raise_by):
                units.append((status, income, tips, tips, overtime, overtime))
    results = _simulate(reference_system, units)
    for name in OUTPUTS:
        lower, higher = results[name][0::2], results[name][1::2]
        # 4. Non-increasing in modified AGI.
        assert np.all(higher <= lower), name
        steps = []
        for magi, raise_by, *_ in cases:
            for status in STATUSES:
                threshold = _threshold(status)
                steps.append(
                    (
                        max(magi - threshold, 0) // INCREMENT,
                        max(magi + raise_by - threshold, 0) // INCREMENT,
                    )
                )
        same_step = np.array([before == after for before, after in steps])
        # Piecewise constant: equal while the whole increments are equal.
        np.testing.assert_array_equal(higher[same_step], lower[same_step], name)
