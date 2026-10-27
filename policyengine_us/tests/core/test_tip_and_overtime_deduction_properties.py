"""Invariants of the qualified tips and overtime deductions (26 U.S.C. 224, 225).

Sections 224(b)(2)(A) and 225(b)(2)(A) reduce each deduction, after its cap,
"(but not below zero) by $100 for each $1,000 by which the taxpayer's modified
adjusted gross income exceeds $150,000 ($300,000 in the case of a joint
return)". Schedule 1-A (2025), lines 11 and 19, divide the excess by $1,000
and, if the result "isn't a whole number, decrease the result to the next
lower whole number". Sections 224(f) and 225(e) allow a married individual
either deduction only on a joint return, and the Part II and Part III cautions
say "If married, you must file jointly to claim this deduction."

Sections 224(e)(1) and 225(d)(1) allow no deduction unless the return includes
"such individual's social security number", and the same cautions say "You
and/or your spouse who received qualified tips must have a valid social
security number" (and the same for overtime). So only amounts received by a
head or spouse with a valid SSN count, and a spouse with nothing to claim needs
none. A dependent's tips and overtime are the dependent's own income (section
73(a) for a child's services) and belong on the dependent's own return.

Each test call, and each Hypothesis example, builds one simulation of many tax
units. Joint returns have two spouses, so the combined caps apply as on the
return. Seeded draws also vary each head's and spouse's SSN card type, make
some heads 17, and add dependents (children and adults input as dependents)
with tips and overtime of their own. A 17-year-old filer with only adult
dependents is the case where the model's head-or-spouse inference picks an
input dependent as head; the dependent still counts for nothing. The tests
check:

1. Every seeded draw, evaluated under all five filing statuses, matches an
   independent restatement of Schedule 1-A lines 7-13 (tips) and 15-21
   (overtime) on the amounts that count, with zero for married filing
   separately.
2. Each deduction lies between 0 and its capped qualifying amount, and a
   positive deduction is the capped amount less a whole multiple of $100.
   These follow from 1, and are checked on the model's output directly so
   that an error in the restatement's phase-out arithmetic cannot hide them.
3. At every $1,000 step from each threshold to full phase-out, for each filing
   status that may claim: the amount is the cap less $100 per whole step (not
   below zero); one dollar below each step past the threshold it is $100
   higher (or what is left at the last step); and $999 above the step it is
   unchanged.
4. Raising modified AGI never raises either deduction, and leaves it unchanged
   while the count of whole $1,000 increments over the threshold is unchanged
   (Hypothesis, with incomes drawn around both thresholds and their steps).
5. Removing every dependent, with their tips and overtime, leaves both
   deductions unchanged.
6. Zeroing the tips and overtime of each head or spouse without a valid SSN
   leaves both deductions unchanged.
7. A spouse with no tips or overtime needs no valid SSN: switching that
   spouse's card type between valid and invalid leaves both unchanged.
8. Giving every head and spouse a valid SSN never lowers either deduction.

5-8 compare the model with itself on paired returns, so they do not depend on
the restatement in 1. Their returns come partly from the draws above and partly
from returns below both thresholds and caps, and each checks that its draw
contains returns where breaking the property would change the deduction.

Modified AGI here is adjusted gross income with no section 911, 931 or 933
exclusions; the YAML tests cover the section 911 and 931 add-backs. AGIs are
whole dollars or quarter dollars, which float32 holds exactly at these
magnitudes.
"""

from collections import namedtuple

import numpy as np
import pytest
from hypothesis import Phase, given, settings
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
# Sections 224(e)(2) and 225(d)(2) adopt section 24(h)(7)(B): an SSN the
# Social Security Administration issued to a citizen, or to a noncitizen
# lawfully admitted to work, before the return's due date. The model's card
# types restate that as citizens and noncitizens with valid work authorization.
VALID_SSN = ("CITIZEN", "NON_CITIZEN_VALID_EAD")
SSN_CARD_TYPES = (*VALID_SSN, "OTHER_NON_CITIZEN", "NONE")

# One tax unit: filing status, modified AGI, the head's and (joint returns
# only) the spouse's tips and overtime, the head's and spouse's SSN card
# types, dependents as (age, SSN card type, tips, overtime), and the head's
# and spouse's ages. Every head and spouse is input as a filer (not a
# dependent) and every dependent as a dependent.
Unit = namedtuple(
    "Unit",
    "status magi head_tips spouse_tips head_overtime spouse_overtime ssns "
    "dependents ages",
    defaults=(("CITIZEN", "CITIZEN"), (), (40, 40)),
)


@pytest.fixture(scope="module")
def reference_system():
    # Read-only policy source shared across simulations; each Simulation gets
    # its own entities and calculation holders.
    return system


def _threshold(status):
    return THRESHOLD.get(status, DEFAULT_THRESHOLD)


def _caps(status):
    return TIP_CAP, OVERTIME_CAP.get(status, DEFAULT_OVERTIME_CAP)


def _counted(unit):
    """Tips and overtime that count: the head's, and on a joint return the
    spouse's, when that person has a valid SSN; never a dependent's, whatever
    role the model infers for them."""
    filers = [(unit.ssns[0], unit.head_tips, unit.head_overtime)]
    if unit.status == "JOINT":
        filers.append((unit.ssns[1], unit.spouse_tips, unit.spouse_overtime))
    tips = sum(tips for ssn, tips, _ in filers if ssn in VALID_SSN)
    overtime = sum(overtime for ssn, _, overtime in filers if ssn in VALID_SSN)
    return tips, overtime


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
    """One tax unit per Unit (or a tuple of its leading fields); joint units
    get a spouse, others one filer, and each dependent is added as a member."""
    period = str(YEAR)
    units = [Unit(*unit) for unit in units]
    people, tax_units, marital_units, households = {}, {}, {}, {}
    for i, unit in enumerate(units):
        # (name, age, SSN card type, tips, overtime, input as a dependent)
        filers = [
            (f"head{i}", unit.ages[0], unit.ssns[0], unit.head_tips, unit.head_overtime)
        ]
        if unit.status == "JOINT":
            filers.append(
                (
                    f"spouse{i}",
                    unit.ages[1],
                    unit.ssns[1],
                    unit.spouse_tips,
                    unit.spouse_overtime,
                )
            )
        dependents = [
            (f"dependent{i}_{j}", *dependent)
            for j, dependent in enumerate(unit.dependents)
        ]
        members = [person[0] for person in filers + dependents]
        for name, age, ssn, tips, overtime, dependent in [
            (*filer, False) for filer in filers
        ] + [(*dependent, True) for dependent in dependents]:
            people[name] = {
                "age": {period: age},
                "is_tax_unit_dependent": {period: dependent},
                "ssn_card_type": {period: ssn},
                "treasury_tipped_occupation_code": {period: 102},
                "tip_income": {period: float(tips)},
                "fsla_overtime_premium": {period: float(overtime)},
            }
        tax_units[f"t{i}"] = {
            "members": members,
            "filing_status": {period: unit.status},
            "adjusted_gross_income": {period: float(unit.magi)},
        }
        marital_units[f"m{i}"] = {"members": [filer[0] for filer in filers]}
        for dependent in dependents:
            marital_units[f"m_{dependent[0]}"] = {"members": [dependent[0]]}
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
    np.testing.assert_array_equal(magi, [unit.magi for unit in units])
    return {name: simulation.calculate(name, period) for name in OUTPUTS}


def _expected(units):
    tips, overtime = [], []
    for unit in (Unit(*unit) for unit in units):
        tip_cap, overtime_cap = _caps(unit.status)
        counted_tips, counted_overtime = _counted(unit)
        tips.append(_schedule_1a(counted_tips, tip_cap, unit.magi, unit.status))
        overtime.append(
            _schedule_1a(counted_overtime, overtime_cap, unit.magi, unit.status)
        )
    return {"tip_income_deduction": tips, "overtime_income_deduction": overtime}


def _ssn(rng):
    return str(rng.choice(SSN_CARD_TYPES, p=[0.55, 0.15, 0.15, 0.15]))


def _draw(seed, n=150):
    """Random returns concentrated around the $1,000 steps of each threshold,
    with random SSN card types and up to two dependents."""
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
        ssns = (_ssn(rng), _ssn(rng))
        dependents = tuple(
            (
                int(rng.choice([10, 17, 22, 70])),
                _ssn(rng),
                int(rng.choice([0, int(rng.integers(0, 30_001))])),
                int(rng.choice([0, int(rng.integers(0, 20_001))])),
            )
            for _ in range(int(rng.integers(0, 3)))
        )
        ages = (int(rng.choice([40, 17], p=[0.8, 0.2])), 40)
        draws.append((magi, *amounts, ssns, dependents, ages))
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
        for unit, value in zip((Unit(*unit) for unit in units), results[name]):
            qualifying = _counted(unit)[cap_index]
            capped = min(qualifying, _caps(unit.status)[cap_index])
            assert 0 <= value <= capped, (name, unit, value)
            if unit.status != "SEPARATE" and value > 0:
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


thresholds = st.sampled_from([DEFAULT_THRESHOLD, THRESHOLD["JOINT"]])
magis = st.one_of(
    # On or next to a $1,000 step of either threshold.
    st.tuples(
        thresholds,
        st.integers(min_value=0, max_value=260),
        st.sampled_from([-1, 0, 1, 500, 999]),
    ).map(lambda t: t[0] + INCREMENT * t[1] + t[2]),
    # Anywhere in or near either phase-out range, in quarter dollars.
    st.tuples(thresholds, st.integers(min_value=-8_000, max_value=1_040_000)).map(
        lambda t: t[0] + t[1] / 4
    ),
    st.integers(min_value=0, max_value=700_000),
)
raises = st.one_of(
    st.integers(min_value=0, max_value=999),
    st.integers(min_value=0, max_value=4_000).map(lambda quarters: quarters / 4),
    st.integers(min_value=0, max_value=60_000),
)
amounts = st.one_of(
    st.sampled_from([12_500, 25_000]), st.integers(min_value=0, max_value=40_000)
)


# Shrinking a failure takes minutes on a simulation this size; the failing
# example is still reported.
@settings(
    # The first generated example is the minimal one (every case at one
    # income with no raise), so the seventh keeps six informative examples.
    max_examples=7,
    deadline=None,
    derandomize=True,
    phases=(Phase.explicit, Phase.generate),
)
@given(
    cases=st.lists(
        st.tuples(magis, raises, amounts, amounts),
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


def _without_invalid_filers(unit):
    head_valid, spouse_valid = (ssn in VALID_SSN for ssn in unit.ssns)
    return unit._replace(
        head_tips=unit.head_tips * head_valid,
        head_overtime=unit.head_overtime * head_valid,
        spouse_tips=unit.spouse_tips * spouse_valid,
        spouse_overtime=unit.spouse_overtime * spouse_valid,
    )


def _observable(unit, output, extra):
    """Whether counting `extra` more of output 0 (tips) or 1 (overtime) would
    change the deduction: modified AGI at or below the threshold, so nothing
    phases out, and room under the cap."""
    cap = _caps(unit.status)[output]
    counted = _counted(unit)[output]
    return (
        unit.status != "SEPARATE"
        and unit.magi <= _threshold(unit.status)
        and min(counted + extra, cap) > min(counted, cap)
    )


def _low_income_draw(seed, n):
    """Returns below both thresholds with amounts under the caps, so each
    paired comparison below can show a difference."""
    rng = np.random.default_rng(seed)

    def amount():
        return int(rng.choice([0, int(rng.integers(1, 6_001))]))

    units = []
    for _ in range(n):
        status = str(rng.choice(CLAIMING))
        magi = float(rng.integers(20_000, DEFAULT_THRESHOLD - 10_000))
        amounts = [amount() for _ in range(4)]
        ssns = (_ssn(rng), _ssn(rng))
        dependents = tuple(
            (int(rng.choice([10, 17, 22, 70])), _ssn(rng), amount(), amount())
            for _ in range(int(rng.integers(0, 3)))
        )
        ages = (int(rng.choice([40, 17], p=[0.8, 0.2])), 40)
        units.append(Unit(status, magi, *amounts, ssns, dependents, ages))
    return units


def _valid_dependent_amount(unit, output, adults_only=False):
    """Output 0 (tips) or 1 (overtime) of dependents with valid SSNs, the
    amounts a mask that ignored dependent status would count."""
    return sum(
        dependent[2 + output]
        for dependent in unit.dependents
        if dependent[1] in VALID_SSN and (dependent[0] >= 18 or not adults_only)
    )


def test_dependents_and_filers_without_valid_ssns_add_nothing(reference_system):
    rng = np.random.default_rng(2)
    # Returns around the thresholds and caps, and returns well below them.
    base = [Unit(str(rng.choice(CLAIMING)), *draw) for draw in _draw(seed=3, n=60)]
    base += _low_income_draw(seed=4, n=100)
    # Filers under 18 whose only adult is an input dependent, at low income: the
    # model infers that dependent as head, so a role-based mask would count the
    # dependent's amounts and drop the filer's (round-1 review).
    base += [
        Unit(
            status,
            60_000,
            4_000,
            0,
            3_000,
            0,
            ("CITIZEN", "CITIZEN"),
            ((45, "CITIZEN", 1_000, 500), (10, "CITIZEN", 0, 0)),
            (17, 40),
        )
        for status in ("SINGLE", "HEAD_OF_HOUSEHOLD")
    ]
    idle_spouse = [unit._replace(spouse_tips=0, spouse_overtime=0) for unit in base]
    variants = {
        "base": base,
        "no dependents": [unit._replace(dependents=()) for unit in base],
        "no invalid filers' amounts": list(map(_without_invalid_filers, base)),
        "idle spouse, valid SSN": [
            unit._replace(ssns=(unit.ssns[0], "CITIZEN")) for unit in idle_spouse
        ],
        "idle spouse, no valid SSN": [
            unit._replace(ssns=(unit.ssns[0], "OTHER_NON_CITIZEN"))
            for unit in idle_spouse
        ],
        "all valid SSNs": [unit._replace(ssns=("CITIZEN", "CITIZEN")) for unit in base],
    }
    results = _simulate(
        reference_system, [unit for units in variants.values() for unit in units]
    )
    n = len(base)
    joint = np.array([unit.status == "JOINT" for unit in base])
    for name in OUTPUTS:
        value = {
            label: results[name][k * n : (k + 1) * n]
            for k, label in enumerate(variants)
        }
        # 5. Dependents' tips and overtime add nothing.
        np.testing.assert_array_equal(value["base"], value["no dependents"], name)
        # 6. Nor do those of a head or spouse without a valid SSN.
        np.testing.assert_array_equal(
            value["base"], value["no invalid filers' amounts"], name
        )
        # 7. A spouse with nothing to claim needs no valid SSN.
        np.testing.assert_array_equal(
            value["idle spouse, valid SSN"], value["idle spouse, no valid SSN"], name
        )
        # 8. A valid SSN never lowers either deduction.
        assert np.all(value["all valid SSNs"] >= value["base"]), name

        # Each property has returns in the draw where breaking it would change
        # the deduction: dependents' or invalid filers' amounts that would
        # move the capped, unphased amount; a filer under 18 whose adult
        # dependent has an amount; a joint return whose spouse lacks a valid
        # SSN and whose head has something to claim.
        output = 0 if name == "tip_income_deduction" else 1
        dependent_amounts = [
            _observable(unit, output, _valid_dependent_amount(unit, output))
            for unit in base
        ]
        invalid_amounts = [
            _observable(
                unit,
                output,
                _counted(unit._replace(ssns=("CITIZEN", "CITIZEN")))[output]
                - _counted(unit)[output],
            )
            for unit in base
        ]
        # A role-based mask counts these adult dependents, inferred as head
        # (and spouse), and nothing once they are removed.
        minor_filer_with_adult_dependents = [
            unit.status != "JOINT"
            and unit.ages[0] < 18
            and unit.magi <= _threshold(unit.status)
            and _valid_dependent_amount(unit, output, adults_only=True) > 0
            for unit in base
        ]
        assert sum(dependent_amounts) >= 30, name
        assert sum(invalid_amounts) >= 15, name
        assert sum(minor_filer_with_adult_dependents) >= 3, name
        assert (joint & (value["idle spouse, valid SSN"] > 0)).sum() >= 10, name
        assert (value["all valid SSNs"] > value["base"]).sum() >= 10, name
