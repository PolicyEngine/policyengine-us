"""Invariants for the 2020 above-the-line charitable deduction.

26 U.S.C. 62(a)(22) (CARES Act sec. 2204) lets an individual who does not
itemize deduct up to $300 of cash charitable contributions in arriving at
adjusted gross income for taxable years beginning in 2020 only. The 2020
Instructions for Form 1040, line 10b, cap it at $300 for a joint return and
$150 for married filing separately. Because adjusted gross income then depends
on the itemization choice, tax_unit_itemizes compares the deductions of the
branches that itemize and that do not.

Invariants, for every household, written from the statute and the form rather
than read from the model's parameters:

1. Bounds and eligibility: the deduction is min(cash gifts, cap) for a unit
   that does not itemize and zero for one that does, and zero in 2021.
2. Adjusted gross income is gross income less the above-the-line deductions,
   which include the charitable deduction (2020 Form 1040 lines 9, 10c, 11).
3. No gift is deducted twice: itemized deductions are exactly the Schedule A
   components, in 2020 and 2021.
4. Consistency of the choice: the income tax of the simulation equals the tax
   of the branch for the choice it makes, which is the lower of the two
   (differential: main simulation against the branch that recomputes it).
5. Decoupled states add it back (California, New York) and Massachusetts
   Part B income leaves it in (TIR 20-9, B(6)).
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# 2020 Instructions for Form 1040, line 10b.
CAP_2020 = {
    "SINGLE": 300,
    "JOINT": 300,
    "SEPARATE": 150,
    "HEAD_OF_HOUSEHOLD": 300,
    "SURVIVING_SPOUSE": 300,
}
SCHEDULE_A = [
    "charitable_deduction",
    "interest_deduction",
    "salt_deduction",
    "medical_expense_deduction",
    "casualty_loss_deduction",
    "misc_deduction",
]
STATES = ["TX", "CA", "NY", "MA", "AZ", "MI", "KY"]


@st.composite
def tax_units(draw):
    money = lambda high: st.one_of(  # noqa: E731
        st.just(0.0), st.integers(1, high).map(float)
    )
    return {
        "filing": draw(st.sampled_from(["single", "joint", "separate", "hoh"])),
        "state": draw(st.sampled_from(STATES)),
        "wages": draw(money(250_000)),
        "cash": draw(money(5_000)),
        "noncash": draw(money(5_000)),
        "mortgage": draw(money(30_000)),
        "medical": draw(money(20_000)),
    }


def _seeded_units(n=60, seed=20261012):
    rng = np.random.default_rng(seed)

    def some(high, p=0.6):
        return float(round(rng.uniform(1, high))) if rng.random() < p else 0.0

    return [
        {
            "filing": str(rng.choice(["single", "joint", "separate", "hoh"])),
            "state": str(rng.choice(STATES)),
            "wages": some(250_000, 0.9),
            "cash": some(5_000, 0.8),
            "noncash": some(5_000, 0.3),
            "mortgage": some(30_000, 0.5),
            "medical": some(20_000, 0.3),
        }
        for _ in range(n)
    ]


def _situation(units, year):
    people = {}
    groups = {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {
            "age": {year: 45},
            "employment_income": {year: u["wages"]},
            "charitable_cash_donations": {year: u["cash"]},
            "charitable_non_cash_donations": {year: u["noncash"]},
            "deductible_mortgage_interest": {year: u["mortgage"]},
            "other_medical_expenses": {year: u["medical"]},
        }
        members = [head]
        if u["filing"] == "joint":
            people[f"spouse_{i}"] = {"age": {year: 43}}
            members.append(f"spouse_{i}")
        if u["filing"] == "hoh":
            people[f"child_{i}"] = {"age": {year: 8}}
            members.append(f"child_{i}")
        groups["marital_units"][f"couple_{i}"] = {
            "members": [m for m in members if not m.startswith("child")]
        }
        if u["filing"] == "hoh":
            groups["marital_units"][f"child_unit_{i}"] = {"members": [f"child_{i}"]}
        tax_unit = {"members": members}
        if u["filing"] == "separate":
            tax_unit["filing_status"] = {year: "SEPARATE"}
        groups["tax_units"][f"tax_unit_{i}"] = tax_unit
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: u["state"]},
        }
    return {"people": people, **groups}


def _check(units, year):
    sim = Simulation(situation=_situation(units, year))

    def calc(variable):
        return np.asarray(sim.calculate(variable, year), dtype=float)

    filing = sim.calculate("filing_status", year).decode_to_str()
    state = np.array([u["state"] for u in units])
    cash = np.array([u["cash"] for u in units])
    itemizes = calc("tax_unit_itemizes").astype(bool)
    ald = calc("charitable_contributions_ald")

    # 1. Bounds and eligibility.
    if year == 2020:
        cap = np.array([CAP_2020[f] for f in filing], dtype=float)
        expected = np.where(itemizes, 0, np.minimum(cash, cap))
    else:
        expected = np.zeros_like(cash)
    np.testing.assert_allclose(ald, expected, atol=TOLERANCE)

    # 2. AGI: line 11 = line 9 - line 10c. Wages are the only income and the
    # charitable deduction the only adjustment.
    wages = np.array([u["wages"] for u in units])
    agi = calc("adjusted_gross_income")
    np.testing.assert_allclose(calc("above_the_line_deductions"), ald, atol=TOLERANCE)
    np.testing.assert_allclose(agi, wages - ald, atol=1)

    # 3. No gift deducted twice.
    components = sum(calc(variable) for variable in SCHEDULE_A)
    np.testing.assert_allclose(
        calc("total_itemized_taxable_income_deductions"), components, atol=1
    )

    # 4. The simulation's tax is the tax of the branch it chooses, the lower.
    if_itemizing = calc("tax_liability_if_itemizing")
    if_not = calc("tax_liability_if_not_itemizing")
    income_tax = calc("income_tax")
    np.testing.assert_allclose(
        income_tax, np.where(itemizes, if_itemizing, if_not), atol=1
    )
    np.testing.assert_allclose(income_tax, np.minimum(if_itemizing, if_not), atol=1)

    # 5. Decoupled states.
    in_state = lambda code: state == code  # noqa: E731
    np.testing.assert_allclose(
        calc("ca_additions")[in_state("CA")], ald[in_state("CA")]
    )
    np.testing.assert_allclose(
        calc("ny_additions")[in_state("NY")], ald[in_state("NY")]
    )
    # Massachusetts does not adopt 62(a)(22) (TIR 20-9, B(6)): Part B AGI is
    # the wages.
    ma = in_state("MA")
    np.testing.assert_allclose(calc("ma_part_b_agi")[ma], wages[ma], atol=1)


@pytest.mark.parametrize("year", [2020, 2021])
def test_seeded_population(year):
    _check(_seeded_units(), year)


@settings(
    max_examples=10,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(tax_units(), min_size=5, max_size=20))
def test_random_households_2020(units):
    _check(units, 2020)
