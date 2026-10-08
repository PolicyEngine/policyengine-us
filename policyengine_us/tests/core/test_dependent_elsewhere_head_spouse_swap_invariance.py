"""Rules for a filer claimed as a dependent elsewhere do not depend on which
spouse is labelled head.

A married couple may list either spouse first, so exchanging the two adults'
`is_tax_unit_head` and `is_tax_unit_spouse` labels, with every other input
kept, must not change their taxes. On main, the federal standard deduction and
seventeen state formulas read only `head_is_dependent_elsewhere`, so a joint
return where one spouse can be claimed on another return (a joint return filed
only to recover withholding can meet the federal exception, IRS Publication
501) was taxed differently depending on which spouse was labelled head. Each
formula now applies its jurisdiction's rule for that case:

- Either spouse limits the return (the IRC 63(c)(5) worksheet): the federal
  standard deduction, Oregon's and Hawaii's standard deductions, and
  Virginia's credit for low-income individuals.
- Only single filers: New York's dependent standard deduction.
- Each spouse separately: Michigan's exemptions and Hawaii's food/excise,
  renters and Act 115 credits count only the filers who cannot be claimed.
- Only when every filer is a dependent: New Mexico's rebates, credits and
  dependents deduction, and Maine's sales tax fairness credit.
- Never on a joint return: Missouri's working family credit, since such a
  couple files as married filing combined.

Hypothesis draws batches of married couples, with and without dependents, in
the eight states with such a rule and one without, for 2021-2026, with either,
both or neither spouse claimed elsewhere. A seeded population and crafted
cases add breadth in every year, and two seeded couples plus the review case
in every state guard 2026. Each batch is one vectorized simulation. For each couple:

1. Swap invariance: federal income tax, state income tax before and after
   refundable credits, and each of the eighteen formulas are the same to the
   cent (or the same boolean) under either labelling.
2. Monotonicity: marking another filer as claimed elsewhere never raises any
   of the eighteen amounts or turns an eligibility on.
3. The helper identities: `head_or_spouse_is_dependent_elsewhere` equals
   `head_is_dependent_elsewhere | spouse_is_dependent_elsewhere`, and
   `head_spouse_count_not_dependent_elsewhere` plus the claimed filers equals
   the number of filers.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.model_api import STATES

TOLERANCE = 0.01  # dollars: the same to the cent
YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
AFFECTED = ["HI", "ME", "MI", "MO", "NM", "NY", "OR", "VA", "CA"]
ALL_STATES = [s for s in STATES if s not in ("PR", "VI")]
TAX_UNIT_OUTPUTS = [
    "income_tax",
    "state_income_tax",
    "state_income_tax_before_refundable_credits",
]
# The formulas that read whether a filer is claimed elsewhere.
CONSUMERS = [
    "basic_standard_deduction",
    "ny_standard_deduction",
    "mi_exemptions",
    "or_standard_deduction",
    "va_low_income_tax_credit_eligible",
    "mo_wftc_eligible",
    "nm_2021_income_rebate",
    "nm_additional_2021_income_rebate",
    "nm_supplemental_2021_income_rebate",
    "nm_deduction_for_certain_dependents_eligible",
    "nm_medical_expense_credit",
    "nm_cdcc_eligible",
    "me_sales_tax_fairness_credit_eligible",
    "hi_deductions",
    "hi_act_115_rebate",
    "hi_food_excise_credit",
    "hi_tax_credit_for_low_income_household_renters_eligible",
    "hi_tax_credit_for_low_income_household_renters",
]
CLAIM_PATTERNS = [(True, False), (False, True), (True, True), (False, False)]


def money(high):
    return st.one_of(st.just(0.0), st.integers(1, high).map(float))


@st.composite
def adults(draw):
    # Low incomes reach the credits' limits; ages reach the 65+ rules.
    return {
        "age": draw(st.integers(18, 90)),
        "is_blind": draw(st.booleans()),
        "is_disabled": draw(st.booleans()),
        "employment_income": draw(money(60_000)),
        "self_employment_income": draw(money(20_000)),
        "taxable_interest_income": draw(money(3_000)),
        "social_security_retirement": draw(money(25_000)),
        "real_estate_taxes": draw(money(6_000)),
        "rent": draw(money(18_000)),
        "charitable_cash_donations": draw(money(6_000)),
        "other_medical_expenses": draw(money(40_000)),
    }


@st.composite
def dependents(draw):
    age = draw(st.integers(0, 23))
    return {
        "age": age,
        "is_full_time_student": age >= 18,
        "employment_income": draw(money(10_000)),
        "pre_subsidy_childcare_expenses": draw(money(8_000)),
    }


@st.composite
def couples(draw):
    return {
        "state": draw(st.sampled_from(AFFECTED)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": draw(st.sampled_from(CLAIM_PATTERNS)),
    }


SEED = 20261008


def _seeded_adult(rng):
    def some(high, p):
        return float(round(rng.uniform(1, high))) if rng.random() < p else 0.0

    age = int(rng.integers(18, 91))
    return {
        "age": age,
        "is_blind": bool(rng.random() < 0.1),
        "is_disabled": bool(rng.random() < 0.1),
        "employment_income": some(60_000, 0.7),
        "self_employment_income": some(20_000, 0.15),
        "taxable_interest_income": some(3_000, 0.3),
        "social_security_retirement": some(25_000, 0.5 if age >= 62 else 0.03),
        "real_estate_taxes": some(6_000, 0.3),
        "rent": some(18_000, 0.5),
        "charitable_cash_donations": some(6_000, 0.3),
        "other_medical_expenses": some(40_000, 0.15),
    }


def _seeded_couples(states, per_state):
    rng = np.random.default_rng(SEED)
    return [
        {
            "state": state,
            "adults": [_seeded_adult(rng), _seeded_adult(rng)],
            "dependents": [
                {"age": int(rng.integers(0, 18))}
                for _ in range(int(rng.choice([0, 0, 1, 2])))
            ],
            "claimed": CLAIM_PATTERNS[int(rng.integers(0, 3))],
        }
        for state in states
        for _ in range(per_state)
    ]


def _crafted_cases(states, review_case_only=False):
    # The review case (married adults aged 20 earning $8,000 each, one
    # claimed by a parent), with and without a child, and older couples who
    # reach the 65+ and renter rules.
    young = {"age": 20, "employment_income": 8_000.0, "rent": 6_000.0}
    old = {
        "age": 70,
        "social_security_retirement": 12_000.0,
        "rent": 9_000.0,
        "other_medical_expenses": 30_000.0,
    }
    cases = []
    for state in states:
        for claimed in CLAIM_PATTERNS[:3]:
            cases += [
                {
                    "state": state,
                    "adults": [young, young],
                    "dependents": [],
                    "claimed": claimed,
                },
            ]
            if review_case_only:
                continue
            cases += [
                {
                    "state": state,
                    "adults": [young, {"age": 22, "employment_income": 3_000.0}],
                    "dependents": [{"age": 2}],
                    "claimed": claimed,
                },
                {
                    "state": state,
                    "adults": [old, {**old, "age": 66}],
                    "dependents": [],
                    "claimed": claimed,
                },
            ]
    return cases


def _situation(units, year, variants):
    # Each unit appears once per variant: (head is the first adult, first
    # adult claimed, second adult claimed). People keep their order and every
    # other input in every copy.
    people = {}
    groups = {
        "tax_units": {},
        "spm_units": {},
        "families": {},
        "marital_units": {},
        "households": {},
    }
    for i, unit in enumerate(units):
        for copy, (first_is_head, claim_a, claim_b) in enumerate(variants(unit)):
            a, b = f"a_{i}_{copy}", f"b_{i}_{copy}"
            for name, amounts, is_head, claimed in (
                (a, unit["adults"][0], first_is_head, claim_a),
                (b, unit["adults"][1], not first_is_head, claim_b),
            ):
                people[name] = {
                    **amounts,
                    "is_tax_unit_head": is_head,
                    "is_tax_unit_spouse": not is_head,
                    "is_tax_unit_dependent": False,
                    "claimed_as_dependent_on_another_return": claimed,
                }
            members = [a, b]
            groups["marital_units"][f"couple_{i}_{copy}"] = {"members": [a, b]}
            for j, amounts in enumerate(unit["dependents"]):
                child = f"dependent_{i}_{copy}_{j}"
                people[child] = {
                    **amounts,
                    "is_tax_unit_head": False,
                    "is_tax_unit_spouse": False,
                    "is_tax_unit_dependent": True,
                }
                members.append(child)
                groups["marital_units"][f"single_{i}_{copy}_{j}"] = {"members": [child]}
            for group, prefix in (
                ("tax_units", "tax_unit"),
                ("spm_units", "spm_unit"),
                ("families", "family"),
            ):
                groups[group][f"{prefix}_{i}_{copy}"] = {"members": members}
            groups["households"][f"household_{i}_{copy}"] = {
                "members": members,
                "state_code": {year: unit["state"]},
            }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _swap_variants(unit):
    claim_a, claim_b = unit["claimed"]
    return [(True, claim_a, claim_b), (False, claim_a, claim_b)]


def _calc(sim, name, year):
    return np.asarray(sim.calculate(name, year), dtype=float)


def _check_swap(units, year, outputs):
    sim = Simulation(situation=_situation(units, year, _swap_variants))
    states = np.array([u["state"] for u in units])
    for name in outputs:
        values = _calc(sim, name, year)
        assert np.isfinite(values).all(), f"{name} in {year} is not finite"
        drawn, swapped = values[0::2], values[1::2]
        differs = ~(np.abs(swapped - drawn) <= TOLERANCE)
        assert not differs.any(), (
            f"{name} in {year} changes when the head and spouse labels are "
            f"exchanged: "
            + ", ".join(
                f"{states[i]} claimed={units[i]['claimed']} "
                f"{drawn[i]:.2f} -> {swapped[i]:.2f}"
                for i in np.flatnonzero(differs)[:10]
            )
        )
    # 3. The helper identities.
    either = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year)
    head = _calc(sim, "head_is_dependent_elsewhere", year)
    spouse = _calc(sim, "spouse_is_dependent_elsewhere", year)
    np.testing.assert_array_equal(either, np.maximum(head, spouse))
    independent = _calc(sim, "head_spouse_count_not_dependent_elsewhere", year)
    np.testing.assert_array_equal(independent + head + spouse, 2)


def _monotone_variants(unit):
    # Nobody, either adult, then both adults claimed; labels fixed.
    return [
        (True, False, False),
        (True, True, False),
        (True, False, True),
        (True, True, True),
    ]


def _check_monotone(units, year):
    sim = Simulation(situation=_situation(units, year, _monotone_variants))
    states = np.array([u["state"] for u in units])
    for name in CONSUMERS:
        values = _calc(sim, name, year).reshape(-1, 4)
        nobody, first, second, both = values.T
        for more, fewer, label in (
            (first, nobody, "first adult"),
            (second, nobody, "second adult"),
            (both, first, "both after first"),
            (both, second, "both after second"),
        ):
            rises = more > fewer + TOLERANCE
            assert not rises.any(), (
                f"{name} in {year} rises when the {label} is claimed "
                f"elsewhere: "
                + ", ".join(
                    f"{states[i]} {fewer[i]:.2f} -> {more[i]:.2f}"
                    for i in np.flatnonzero(rises)[:10]
                )
            )


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=8, max_size=20))
def test_claimed_spouse_does_not_depend_on_head_label(year, units):
    _check_swap(units, year, TAX_UNIT_OUTPUTS + CONSUMERS)


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    units = _seeded_couples(AFFECTED, per_state=4) + _crafted_cases(AFFECTED)
    _check_swap(units, year, TAX_UNIT_OUTPUTS + CONSUMERS)
    _check_monotone(units, year)


def test_every_state_with_a_claimed_spouse():
    # Other states' rules for a claimed filer read both spouses already;
    # this guards their state income tax in one year.
    units = _seeded_couples(ALL_STATES, per_state=2) + _crafted_cases(
        ALL_STATES, review_case_only=True
    )
    _check_swap(units, 2026, TAX_UNIT_OUTPUTS)
