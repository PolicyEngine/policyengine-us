"""Property tests: South Carolina TANF dependent children's earnings, child
support paid and whole-dollar amounts.

S.C. Code Regs. Chapter 114 and SC DSS TANF Policy Manual, Volume 67:

- 114-1140(N)(1) and Section 7.5 (PDF page 105): "Earned income of a
  dependent child(ren) is excluded" from eligibility and the benefit;
  Section 8.16 B (page 134).
- 114-1140(L), Section 8.11 (page 131) and Section 8.16 D and F (page 134):
  child support that a benefit group member pays outside the home comes off
  that member's own income, after the Section 8.12 earned income
  disregards, and never takes it below zero.
- 114-1140(A)(4) and the Section 8.15 table notes (page 133): the need
  standard and the payment drop their cents. 114-1150(A) sets the gross
  income limit at 185 percent of the need standard, cents included.

For every generated South Carolina benefit group:

(a) sc_tanf is a whole number of dollars, and is 0 or at least $10.
(b) Countable income is at least 0. It never rises when child support paid
    rises, and $1 more support lowers it by at most $1.
(c) Changing a dependent child's earned income never changes
    sc_tanf_gross_income, sc_tanf_countable_income or sc_tanf.
(d) sc_tanf never rises when an adult's wages rise.
(e) Child support paid never changes sc_tanf_gross_income.
(f) With no dependent-child earnings and no child support paid,
    sc_tanf_countable_income equals the formula before these rules, frozen
    below as `previous_countable_income`.

Generated groups have no self-employment income and nobody receives SSI, so
earned income is never negative. Each group and its variants share one
vectorized simulation.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
MONTHS = ("2026-01", "2026-05")
# Section 8.12 disregards: 50% in the first four months, then $100.
INITIAL_MONTHS = 4
INITIAL_RATE = 0.5
FLAT_DISREGARD = 100
MINIMUM_PAYMENT = 10
WAGES = "employment_income_before_lsr"
UNEARNED = ("alimony_income", "child_support_received", "social_security_survivors")


def previous_countable_income(group, month):
    """The countable income formula before these rules: every member's wages
    after the Section 8.12 disregard, plus gross unearned income."""
    total = 0
    for member in group:
        earned = member.get(WAGES, 0) / 12
        if int(month[-2:]) <= INITIAL_MONTHS:
            total += earned * (1 - INITIAL_RATE)
        else:
            total += max(earned - FLAT_DISREGARD, 0)
        total += sum(member.get(source, 0) for source in UNEARNED) / 12
    return total


def situation(groups):
    people, units, marital_units, households = {}, {}, {}, {}
    for i, group in enumerate(groups):
        members = []
        adults = sum(not m["child"] for m in group)
        for j, member in enumerate(group):
            name = f"p{i}_{j}"
            values = {
                "age": member["age"],
                "is_pregnant": member.get("pregnant", False),
                "is_in_secondary_school": member.get("in_school", False),
                "is_tax_unit_head": j == 0,
                "is_tax_unit_spouse": j == 1 and adults == 2,
                "is_tax_unit_dependent": member["child"],
                WAGES: member.get(WAGES, 0),
                "child_support_expense": member.get("support_paid", 0),
                **{source: member.get(source, 0) for source in UNEARNED},
            }
            people[name] = {k: {YEAR: v} for k, v in values.items()}
            members.append(name)
        adult_names = members[:adults]
        marital_units[f"m{i}"] = {"members": adult_names}
        for child in members[adults:]:
            marital_units[f"m{child}"] = {"members": [child]}
        units[f"u{i}"] = {"members": members}
        households[f"h{i}"] = {"members": members, "state_code": {YEAR: "SC"}}
    return {
        "people": people,
        "tax_units": units,
        "spm_units": {k: dict(v) for k, v in units.items()},
        "families": {k: dict(v) for k, v in units.items()},
        "marital_units": marital_units,
        "households": households,
    }


def calculate(groups, month):
    simulation = Simulation(situation=situation(groups))
    return {
        name: np.asarray(simulation.calculate(name, month))
        for name in (
            "sc_tanf",
            "sc_tanf_gross_income",
            "sc_tanf_countable_income",
            "sc_tanf_child_support_deduction",
        )
    }


def variants(group, support_raise, child_wages, wage_raise):
    """The group as drawn, with the head's support paid raised, with every
    dependent child's wages replaced, and with the head's wages raised."""
    more_support = [dict(m) for m in group]
    more_support[0]["support_paid"] = (
        more_support[0].get("support_paid", 0) + support_raise
    )
    other_child_wages = [
        {**m, WAGES: child_wages} if m["child"] else dict(m) for m in group
    ]
    more_wages = [dict(m) for m in group]
    more_wages[0][WAGES] = more_wages[0].get(WAGES, 0) + wage_raise
    return [group, more_support, other_child_wages, more_wages]


def check(cases, month):
    groups = [g for group, *changes in cases for g in variants(group, *changes)]
    out = {k: v.reshape(-1, 4) for k, v in calculate(groups, month).items()}
    benefit = out["sc_tanf"]
    countable = out["sc_tanf_countable_income"]
    gross = out["sc_tanf_gross_income"]
    for k, (group, support_raise, _, _) in enumerate(cases):
        context = {"group": group, "month": month}
        # (a) Whole dollars, and nothing paid under the minimum.
        assert np.all(benefit[k] == np.floor(benefit[k])), context
        assert np.all((benefit[k] == 0) | (benefit[k] >= MINIMUM_PAYMENT)), context
        # (b) Nonnegative, nonincreasing in support paid, at most $1 per $1.
        assert np.all(countable[k] >= 0), context
        drop = countable[k, 0] - countable[k, 1]
        assert -0.01 <= drop <= support_raise / 12 + 0.01, context
        # (c) A dependent child's earnings change nothing.
        for values in (gross, countable, benefit):
            assert values[k, 2] == pytest.approx(values[k, 0], abs=0.01), context
        # (d) More adult wages never raise the benefit.
        assert benefit[k, 3] <= benefit[k, 0], context
        # (e) Support paid never changes gross income.
        assert gross[k, 1] == pytest.approx(gross[k, 0], abs=0.01), context


def money(high):
    return st.one_of(st.just(0), st.integers(1, high))


@st.composite
def adult(draw):
    return {
        "child": False,
        "age": draw(st.integers(19, 60)),
        "pregnant": draw(st.booleans()),
        WAGES: draw(money(30_000)),
        "support_paid": draw(money(9_000)),
        "alimony_income": draw(money(4_000)),
        "child_support_received": draw(money(4_000)),
    }


@st.composite
def child(draw):
    age = draw(st.integers(0, 18))
    return {
        "child": True,
        "age": age,
        # An 18-year-old is a dependent child only in secondary school.
        "in_school": age >= 14 if age < 18 else True,
        WAGES: draw(money(12_000)),
        "social_security_survivors": draw(money(3_000)),
    }


@st.composite
def case(draw):
    adults = draw(st.lists(adult(), min_size=1, max_size=2))
    children = draw(st.lists(child(), min_size=1, max_size=3))
    return (
        adults + children,
        draw(st.integers(1, 6_000)),
        draw(money(12_000)),
        draw(st.integers(1, 12_000)),
    )


SETTINGS = dict(
    max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow]
)


@settings(**SETTINGS)
@example(
    cases=[
        (
            [
                {"child": False, "age": 40, WAGES: 7_200, "support_paid": 2_400},
                {"child": True, "age": 16, WAGES: 6_000},
            ],
            1,
            0,
            1,
        )
    ],
    month="2026-05",
)
# A payer whose support exceeds the payer's own income. The stored float32
# deduction exceeds the float64 sum of that income by about 3e-5, and the
# floor in sc_tanf_countable_income keeps countable income at 0.
@example(
    cases=[
        (
            [
                {
                    "child": False,
                    "age": 40,
                    WAGES: 9_005,
                    "alimony_income": 2_298,
                    "support_paid": 9_000,
                },
                {"child": True, "age": 5},
            ],
            1,
            0,
            1,
        )
    ],
    month="2026-01",
)
@given(
    cases=st.lists(case(), min_size=1, max_size=6),
    month=st.sampled_from(MONTHS),
)
def test_invariants(cases, month):
    check(cases, month)


def without_child_earnings_or_support(group):
    return [{**m, WAGES: 0} if m["child"] else {**m, "support_paid": 0} for m in group]


def differential(groups, month):
    groups = [without_child_earnings_or_support(g) for g in groups]
    countable = calculate(groups, month)["sc_tanf_countable_income"]
    expected = [previous_countable_income(g, month) for g in groups]
    np.testing.assert_allclose(countable, expected, atol=0.01)


@settings(**SETTINGS)
@given(
    groups=st.lists(case().map(lambda c: c[0]), min_size=1, max_size=8),
    month=st.sampled_from(MONTHS),
)
def test_matches_previous_formula_without_child_earnings_or_support(groups, month):
    # (f) The differential on generated groups.
    differential(groups, month)


@pytest.mark.parametrize("month", MONTHS)
def test_200_seeded_households_match_previous_formula(month):
    # (f) The differential on 200 seeded South Carolina households.
    rng = np.random.default_rng(10497)
    groups = []
    for _ in range(200):
        group = []
        for _ in range(rng.integers(1, 3)):
            group.append(
                {
                    "child": False,
                    "age": int(rng.integers(19, 61)),
                    "pregnant": bool(rng.integers(0, 2)),
                    WAGES: int(rng.integers(0, 3) * rng.integers(0, 30_001)),
                    "alimony_income": int(rng.integers(0, 2) * rng.integers(0, 4_001)),
                    "child_support_received": int(
                        rng.integers(0, 2) * rng.integers(0, 4_001)
                    ),
                }
            )
        for _ in range(rng.integers(0, 4)):
            group.append(
                {
                    "child": True,
                    "age": int(rng.integers(0, 18)),
                    "social_security_survivors": int(
                        rng.integers(0, 2) * rng.integers(0, 3_001)
                    ),
                }
            )
        groups.append(group)
    differential(groups, month)
