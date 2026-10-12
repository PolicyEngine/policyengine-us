"""Invariants for Ohio's unreimbursed medical care deduction, R.C. 5747.01(A)(10).

The Unreimbursed Medical Care Expenses Worksheet (2025 IT 1040 instructions,
p. 41) computes line 8 once for the return: line 5 expenses less 7.5% of
federal AGI, with AGI entered as zero if less than zero (line 6). Lines 1 and 2
(premiums with no Medicare or employer plan, and long-term care premiums) are
deducted in full. Each person carries their own lines 1 and 2 and a share of
line 8 in proportion to their line 5 expenses, and Ohio AGI is the sum over
the members. Premiums go on line 1 if the person is eligible for neither
Medicare nor a subsidized plan of the taxpayer's or spouse's employer
(R.C. 5747.01(A)(10)(a)), and on line 3, part of line 5, otherwise.

Hypothesis draws batches of tax units (single, joint, head of household or
joint with dependents), each person with wages, medical expenses, health
insurance premiums, long-term care premiums, Medicare eligibility, employer
coverage, an employer coverage offer and an employer contribution category,
and some heads with a business loss that makes federal AGI negative. A seeded
population of 200 units adds breadth. Each batch runs as one vectorized
simulation, and again with every medical amount set to zero. For every tax
unit:

1. Conservation: the members' line 8 shares sum to the return's line 8.
2. Differential: line 8 and each share equal an independent numpy worksheet,
   with the 7.5% rate taken from the instructions rather than the parameters.
3. Bounds: 0 <= line 8 <= line 5, and 0 <= each share <= the person's own
   line 5 expenses.
4. Accounting: the tax unit deduction is line 8 plus lines 1 and 2, counted
   once. Removing the medical amounts raises Ohio AGI by exactly that
   deduction, and raises each person's Ohio AGI (and joint filing credit
   qualifying income) by exactly their own share, so a spouse never loses
   qualifying income for the other spouse's expenses.
5. Partition: each person's premiums are on exactly one of lines 1 and 3, so
   line 1 plus the premiums on line 3 equals the premiums paid. Line 1 is
   zero for everyone on a return where the head or spouse has employer
   coverage, an offer of it, or an employer paying some or all of their
   premiums, and for every Medicare-eligible person.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# Worksheet line 7 multiplies line 6 by 7.5% in every year's instructions
# (2022 p. 27, 2023 p. 40, 2024 p. 41, 2025 p. 41).
PUBLISHED_RATE = 0.075
# Nothing here varies by year, so a few years suffice: each simulation costs
# far more than the checks on it.
YEARS = [2022, 2025]
SEEDED_YEAR = 2024

MEDICAL = [
    "other_medical_expenses",
    "health_insurance_premiums",
    "long_term_health_insurance_premiums",
]
COVERAGE = [
    "is_medicare_eligible",
    "has_esi",
    "offered_aca_disqualifying_esi",
    "employer_contribution_to_health_insurance_premiums_category",
]

amounts = st.one_of(
    st.just(0.0),
    st.integers(1, 3_000).map(float),
    st.integers(3_000, 40_000).map(float),
)
wages = st.one_of(st.just(0.0), st.integers(1, 200_000).map(float))
losses = st.one_of(st.just(0.0), st.integers(-100_000, -1).map(float))
# Weighted toward the defaults: no Medicare, no employer coverage and the NONE
# category, which says nothing about whether an employer plan exists.
CATEGORIES = ["NONE", "NONE", "NONE", "SOME", "ALL", "NA"]
rare = st.sampled_from([False, False, False, True])


@st.composite
def people(draw):
    return {
        "employment_income": draw(wages),
        "other_medical_expenses": draw(amounts),
        "health_insurance_premiums": draw(amounts),
        "long_term_health_insurance_premiums": draw(amounts),
        "is_medicare_eligible": draw(rare),
        "has_esi": draw(rare),
        "offered_aca_disqualifying_esi": draw(rare),
        "employer_contribution_to_health_insurance_premiums_category": draw(
            st.sampled_from(CATEGORIES)
        ),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "joint", "hoh", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
    return {
        "head": draw(people()),
        "loss": draw(losses),
        "spouse": draw(people()) if kind.startswith("joint") else None,
        "dependents": [draw(people()) for _ in range(n_dependents)],
    }


SEED = 20261006


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)

    def amount():
        return float(
            [0, rng.integers(1, 3_001), rng.integers(3_000, 40_001)][rng.choice(3)]
        )

    def person():
        return {
            "employment_income": float(rng.integers(0, 200_001)),
            "other_medical_expenses": amount(),
            "health_insurance_premiums": amount(),
            "long_term_health_insurance_premiums": amount(),
            "is_medicare_eligible": bool(rng.random() < 0.25),
            "has_esi": bool(rng.random() < 0.25),
            "offered_aca_disqualifying_esi": bool(rng.random() < 0.25),
            "employer_contribution_to_health_insurance_premiums_category": str(
                rng.choice(CATEGORIES)
            ),
        }

    units = []
    for _ in range(n):
        kind = rng.choice(["single", "joint", "hoh", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 4)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "head": person(),
                "loss": float(-rng.integers(1, 100_001)) if rng.random() < 0.2 else 0.0,
                "spouse": person() if kind.startswith("joint") else None,
                "dependents": [person() for _ in range(n_dependents)],
            }
        )
    return units


def _situation(units, year, *, medical):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}

    def add(name, values, role):
        people[name] = {
            "age": {"head": 45, "spouse": 43, "dependent": 10}[role],
            "is_tax_unit_head": role == "head",
            "is_tax_unit_spouse": role == "spouse",
            "is_tax_unit_dependent": role == "dependent",
            "employment_income": values["employment_income"],
            **{name: values[name] for name in COVERAGE},
            # No modeled Medicare Part B premium, so the premiums are only
            # the drawn ones and zeroing them removes every medical amount.
            "takes_up_medicare_if_eligible": False,
            **{name: values[name] * medical for name in MEDICAL},
        }

    for i, unit in enumerate(units):
        head = f"head_{i}"
        add(head, unit["head"], "head")
        people[head]["self_employment_income"] = unit["loss"]
        members, couple = [head], [head]
        if unit["spouse"] is not None:
            spouse = f"spouse_{i}"
            add(spouse, unit["spouse"], "spouse")
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, dependent in enumerate(unit["dependents"]):
            name = f"dependent_{i}_{j}"
            add(name, dependent, "dependent")
            members.append(name)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [name]}
        groups["tax_units"][f"tax_unit_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "OH"},
        }
    people = {
        name: {key: {year: value} for key, value in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


PERSON = [
    "other_medical_expenses",
    "health_insurance_premiums",
    "oh_medical_care_insurance_premiums",
    "is_medicare_eligible",
    "has_esi",
    "offered_aca_disqualifying_esi",
    "oh_insured_unreimbursed_medical_care_expense_amount",
    "oh_insured_unreimbursed_medical_care_expenses_person",
    "oh_uninsured_unreimbursed_medical_care_expenses",
    "long_term_health_insurance_premiums",
    "oh_unreimbursed_medical_care_expense_deduction_person",
    "oh_agi_person",
    "oh_joint_filing_credit_qualifying_income",
]
TAX_UNIT = [
    "adjusted_gross_income",
    "oh_employer_subsidized_health_plan_eligible",
    "oh_insured_unreimbursed_medical_care_expenses",
    "oh_unreimbursed_medical_care_expense_deduction",
    "oh_agi",
]


def _run(units, year, *, medical=True):
    sim = Simulation(situation=_situation(units, year, medical=medical))
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in PERSON + TAX_UNIT
    }
    out["filer"] = np.asarray(sim.calculate("is_tax_unit_head_or_spouse", year))
    out["category"] = sim.calculate(
        "employer_contribution_to_health_insurance_premiums_category", year
    ).decode_to_str()
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_sum(run, values):
    return np.bincount(run["unit"], weights=values, minlength=len(run["oh_agi"]))


def _check(units, year):
    base = _run(units, year)
    unit = base["unit"]
    line_5_person = base["oh_insured_unreimbursed_medical_care_expense_amount"]
    line_8 = base["oh_insured_unreimbursed_medical_care_expenses"]
    share = base["oh_insured_unreimbursed_medical_care_expenses_person"]
    line_1 = base["oh_uninsured_unreimbursed_medical_care_expenses"]

    # 5. Partition, against an independent reading of the worksheet. No one
    # is self-employed, so the premiums are the drawn ones.
    premiums = base["health_insurance_premiums"]
    np.testing.assert_allclose(
        base["oh_medical_care_insurance_premiums"], premiums, atol=TOLERANCE
    )
    employer_plan = (
        (base["has_esi"] > 0)
        | (base["offered_aca_disqualifying_esi"] > 0)
        | np.isin(base["category"], ["SOME", "ALL"])
    )
    return_eligible = _unit_sum(base, base["filer"] * employer_plan) > 0
    np.testing.assert_array_equal(
        base["oh_employer_subsidized_health_plan_eligible"] > 0, return_eligible
    )
    on_line_3 = (base["is_medicare_eligible"] > 0) | return_eligible[unit]
    line_3 = line_5_person - base["other_medical_expenses"]
    np.testing.assert_allclose(line_1, np.where(on_line_3, 0, premiums), atol=TOLERANCE)
    np.testing.assert_allclose(line_3, np.where(on_line_3, premiums, 0), atol=TOLERANCE)
    np.testing.assert_allclose(line_1 + line_3, premiums, atol=TOLERANCE)
    line_5 = _unit_sum(base, line_5_person)

    # 1. Conservation.
    np.testing.assert_allclose(_unit_sum(base, share), line_8, atol=TOLERANCE)

    # 2. Differential against an independent worksheet.
    line_6 = np.maximum(base["adjusted_gross_income"], 0)
    expected_line_8 = np.maximum(line_5 - PUBLISHED_RATE * line_6, 0)
    np.testing.assert_allclose(line_8, expected_line_8, atol=TOLERANCE)
    expected_share = np.divide(
        line_5_person * expected_line_8[unit],
        line_5[unit],
        out=np.zeros_like(line_5_person),
        where=line_5[unit] > 0,
    )
    np.testing.assert_allclose(share, expected_share, atol=TOLERANCE)

    # 3. Bounds.
    assert (line_8 >= 0).all()
    assert (line_8 <= line_5 + TOLERANCE).all()
    assert (share >= 0).all()
    assert (share <= line_5_person + TOLERANCE).all()

    # 4. Accounting: each amount counted once, and only for its own person.
    person_deduction = base["oh_unreimbursed_medical_care_expense_deduction_person"]
    np.testing.assert_allclose(
        person_deduction,
        share
        + base["oh_uninsured_unreimbursed_medical_care_expenses"]
        + base["long_term_health_insurance_premiums"],
        atol=TOLERANCE,
    )
    deduction = base["oh_unreimbursed_medical_care_expense_deduction"]
    np.testing.assert_allclose(
        deduction, _unit_sum(base, person_deduction), atol=TOLERANCE
    )

    without = _run(units, year, medical=False)
    np.testing.assert_allclose(
        without["adjusted_gross_income"],
        base["adjusted_gross_income"],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        without["oh_unreimbursed_medical_care_expense_deduction"], 0, atol=TOLERANCE
    )
    _assert_difference(without["oh_agi"], base["oh_agi"], deduction, "oh_agi")
    for name in ["oh_agi_person", "oh_joint_filing_credit_qualifying_income"]:
        _assert_difference(without[name], base[name], person_deduction, name)


def _assert_difference(minuend, subtrahend, expected, name):
    # Incomes are float32, so above 131,072 the spacing between values is
    # 0.016 or more, and a difference of two incomes is only exact to about
    # one spacing of the larger.
    spacing = np.spacing(
        np.maximum(np.abs(minuend), np.abs(subtrahend)).astype(np.float32)
    )
    error = np.abs(minuend - subtrahend - expected)
    assert (error <= TOLERANCE + 2 * spacing).all(), name


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.sampled_from(YEARS), st.lists(tax_units(), min_size=5, max_size=30))
def test_oh_unreimbursed_medical_deduction_invariants(year, units):
    _check(units, year)


def test_seeded_population():
    _check(_seeded_units(), SEEDED_YEAR)
