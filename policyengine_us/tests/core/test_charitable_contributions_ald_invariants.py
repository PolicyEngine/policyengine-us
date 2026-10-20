"""Invariants for the 2020 above-the-line charitable deduction.

26 U.S.C. 62(a)(22) (CARES Act sec. 2204) lets an individual who does not
itemize deduct up to $300 of cash charitable contributions in arriving at
adjusted gross income for taxable years beginning in 2020 only. The statute
caps it at $300 for every return; the 2020 Instructions for Form 1040, line
10b, also give $300 for a joint return, and their $150 for married filing
separately has no basis in the statute, which governs. Because adjusted gross
income then depends on the itemization choice, tax_unit_itemizes compares the
deductions of the branches that itemize and that do not.

Invariants, for every household, written from the statute and the form rather
than read from the model's parameters:

1. Bounds and eligibility: the deduction is min(the head's and spouse's cash
   gifts, $300) for a unit that does not itemize and zero for one that does,
   and zero in 2021. A dependent's gifts are on the dependent's own return.
2. Adjusted gross income is gross income less the above-the-line deductions,
   which include the charitable deduction (2020 Form 1040 lines 9, 10c, 11).
3. No gift is deducted twice: itemized deductions are exactly the Schedule A
   components, in 2020 and 2021.
4. Consistency of the choice: the income tax of the simulation equals the tax
   of the branch for the choice it makes, which is the lower of the two
   (differential: main simulation against the branch that recomputes it).
5. Decoupled states add it back (California; New York's recomputed federal
   AGI, IT-201 line 19a) and Massachusetts Part B income leaves it in (TIR
   20-9, B(6)).
6. Without branching (as CI runs YAML tests), the choice still leaves the
   lower taxable income of the two branches: in 2020 the comparison counts
   what not itemizing takes off adjusted gross income.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# 26 U.S.C. 62(a)(22): "not to exceed $300", for every return.
CAP_2020 = 300
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
        "child_cash": draw(money(1_000)),
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
            "child_cash": some(1_000, 0.3),
        }
        for _ in range(n)
    ] + [
        # Single New Hampshire filers (no state or local tax deduction) whose
        # Schedule A is the $12,400 standard deduction plus k, with $300 of
        # gifts: itemizing pays only when k > 300.
        {
            "filing": "single",
            "state": "NH",
            "wages": 60_000.0,
            "cash": 300.0,
            "noncash": 0.0,
            "mortgage": 12_400.0 - 300 + k,
            "medical": 0.0,
            "child_cash": 0.0,
        }
        for k in [-400, -200, -100, 0, 100, 299, 301, 400]
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
            people[f"child_{i}"] = {
                "age": {year: 15},
                "charitable_cash_donations": {year: u["child_cash"]},
            }
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


def _no_branching(parameters):
    parameters.gov.simulation.branch_to_determine_itemization.update(
        start=instant("2000-01-01"), stop=instant("2039-12-31"), value=False
    )
    return parameters


class NoBranching(Reform):
    def apply(self):
        self.modify_parameters(_no_branching)


def _check(units, year, without_branching=False):
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
        expected = np.where(itemizes, 0, np.minimum(cash, CAP_2020))
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
    ny = in_state("NY")
    np.testing.assert_allclose(
        calc("ny_recomputed_federal_agi")[ny], (agi + ald)[ny], atol=1
    )
    # Massachusetts does not adopt 62(a)(22) (TIR 20-9, B(6)): Part B AGI is
    # the wages.
    ma = in_state("MA")
    np.testing.assert_allclose(calc("ma_part_b_agi")[ma], wages[ma], atol=1)

    # 6. Without branching, the choice leaves the lower taxable income.
    if without_branching:
        plain = Simulation(situation=_situation(units, year), reform=NoBranching)
        taxable_income = np.asarray(plain.calculate("taxable_income", year))
        branch_incomes = [
            np.asarray(plain.branches[name].calculate("taxable_income", year))
            for name in ("itemizing", "not_itemizing")
        ]
        assert (taxable_income <= np.minimum(*branch_incomes) + 1).all()


def test_seeded_population_2020():
    # The seeded population includes households at the itemization margin.
    _check(_seeded_units(), 2020, without_branching=True)


def test_seeded_population_2021():
    _check(_seeded_units(), 2021)


@settings(
    max_examples=10,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(tax_units(), min_size=5, max_size=20))
def test_random_households_2020(units):
    _check(units, 2020)
