"""Dependents' own itemized expenses stay off the filers' return.

A tax unit's dependents file their own returns, so the head's and spouse's
Schedule A counts only their own expenses:

- taxes "imposed on you" (26 CFR 1.164-1(a); Pub. 17 (2025) p. 98);
- mortgage "interest you pay" on a home "in which you have an ownership
  interest" (Pub. 936 (2025) p. 2), and investment interest up to "the net
  investment income of the taxpayer" (26 U.S.C. 163(d)(1));
- "contributions of money or property you make" (Pub. 526 (2025) p. 4);
- gambling losses up to the winnings on the filer's own Schedule 1 (2025
  Instructions for Schedule A, p. 11);
- before 2018, expenses of "your job" and fees for "your tax return" (2017
  Instructions for Schedule A, p. 12);
- Puerto Rico mortgage interest on "a qualified residence of the taxpayer"
  (Codigo de Rentas Internas sec. 1033.15(a)(1)(A)).

Medical expenses are left out on purpose: section 213(a) lets the filers
deduct what they pay for a dependent's care. Casualty losses are left out
because PolicyEngine/policyengine-us#9912 makes them filer-only with the
Form 4684 $100 rule.

State and local income or sales tax is an input here, the same for both
twins. A dependent's real estate taxes are a household housing cost for
some state TANF programs (e.g. ny_tanf_shelter_allowance), and TANF is part
of the income that picks the IRS optional sales tax table row
(state_sales_tax_income_bracket), so the sales tax half of SALT can rightly
move with them. Fixing it isolates the filer-only property.

Each drawn tax unit appears twice in one simulation. The twins share every
input except the dependents' itemized expenses, which are zero in the first
twin and drawn in the second. The checks are:

1. Differential: every listed deduction, and the federal income tax, is the
   same for both twins, so a dependent-only payer adds nothing and the
   filers' own amounts are unchanged by a dependent's.
2. Restatement: the person-level sums equal an independent numpy sum of the
   head's and spouse's inputs (interest, the real estate part of SALT,
   miscellaneous expenses, gambling losses up to winnings).
"""

import numpy as np
import pytest

from policyengine_us import Simulation

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

# Person-level itemized inputs whose dependent amounts belong on the
# dependent's own return.
EXPENSES = (
    "real_estate_taxes",
    "deductible_mortgage_interest",
    "investment_interest_expense",
    "charitable_cash_donations",
    "charitable_non_cash_donations",
    "gambling_losses",
    "gambling_winnings",
    "unreimbursed_business_employee_expenses",
    "tax_preparation_fees",
)

INVARIANT_OUTPUTS = (
    "capped_property_taxes",
    "salt",
    "salt_deduction",
    "interest_deduction",
    "charitable_deduction",
    "charitable_deduction_for_non_itemizers",
    "wagering_losses_deduction",
    "total_misc_deductions",
    "misc_deduction",
    "total_itemized_taxable_income_deductions",
    "itemized_taxable_income_deductions_reduction",
    "itemized_taxable_income_deductions",
    "taxable_income",
    "income_tax",
    "pr_mortgage_deduction",
)

# 2017: section 68 and miscellaneous deductions in force. 2021:
# non-itemizer charity. 2024: TCJA. 2026: P.L. 119-21 (SALT phase-down,
# charity floor, section 68 rewrite).
YEARS = (2017, 2021, 2024, 2026)
STATES = ("TX", "CA", "NY", "PR")

amount = st.one_of(st.just(0), st.integers(1, 60_000))
expenses = st.fixed_dictionaries({name: amount for name in EXPENSES})
dependent = st.fixed_dictionaries(
    {
        # An elderly parent claimed as a dependent, or a child.
        "adult": st.booleans(),
        "age": st.integers(0, 17),
        "expenses": expenses,
    }
)
tax_unit = st.fixed_dictionaries(
    {
        "married": st.booleans(),
        "state": st.sampled_from(STATES),
        "wages": st.integers(0, 900_000),
        "sales_or_income_tax": st.integers(0, 40_000),
        "head": expenses,
        "spouse": expenses,
        "dependents": st.lists(dependent, min_size=1, max_size=3),
    }
)


def _person(year, age, inputs, wages=0, dependent=False):
    values = {"age": age, "employment_income": wages, **inputs}
    if dependent:
        values["is_tax_unit_dependent"] = True
    return {name: {year: value} for name, value in values.items()}


def build_situation(units, year):
    """Two twins per drawn unit: dependents' expenses zero, then as drawn."""
    situation = {
        group: {}
        for group in (
            "people",
            "tax_units",
            "marital_units",
            "households",
            "spm_units",
            "families",
        )
    }
    people = situation["people"]
    filers = []
    for i, unit in enumerate(units):
        for twin in (0, 1):
            name = f"unit_{i}_{twin}"
            head = f"{name}_head"
            people[head] = _person(year, 45, unit["head"], unit["wages"])
            members = [head]
            unit_filers = [head]
            if unit["married"]:
                spouse = f"{name}_spouse"
                people[spouse] = _person(year, 43, unit["spouse"])
                members.append(spouse)
                unit_filers.append(spouse)
            situation["marital_units"][name] = {"members": list(unit_filers)}
            for j, dep in enumerate(unit["dependents"]):
                person = f"{name}_dependent_{j}"
                inputs = dep["expenses"] if twin else {k: 0 for k in dep["expenses"]}
                age = 70 + j if dep["adult"] else dep["age"]
                people[person] = _person(year, age, inputs, dependent=True)
                members.append(person)
                situation["marital_units"][person] = {"members": [person]}
            situation["tax_units"][name] = {
                "members": members,
                "state_and_local_sales_or_income_tax": {
                    year: unit["sales_or_income_tax"]
                },
            }
            situation["households"][name] = {
                "members": members,
                "state_code": {year: unit["state"]},
            }
            situation["spm_units"][name] = {"members": members}
            situation["families"][name] = {"members": members}
            filers.append(unit_filers)
    return situation, filers


def check(units, year):
    situation, filers = build_situation(units, year)
    simulation = Simulation(situation=situation)
    outputs = {v: np.asarray(simulation.calculate(v, year)) for v in INVARIANT_OUTPUTS}

    # 1. The twins differ only in dependents' expenses, so every output
    # matches. float32 sums of the same filer amounts are bit-identical.
    for v, values in outputs.items():
        np.testing.assert_array_equal(values[1::2], values[0::2], err_msg=v)

    # 2. Person-level sums equal the head's and spouse's own inputs.
    people = situation["people"]
    filer_sums = {
        name: np.array(
            [
                sum(people[p].get(name, {}).get(year, 0) for p in unit_filers)
                for unit_filers in filers
            ],
            dtype=float,
        )
        for name in EXPENSES
    }
    tol = 0.01
    np.testing.assert_allclose(
        outputs["interest_deduction"],
        filer_sums["deductible_mortgage_interest"]
        + filer_sums["investment_interest_expense"],
        rtol=1e-6,
        atol=tol,
    )
    sales_or_income_tax = np.asarray(
        simulation.calculate("state_and_local_sales_or_income_tax", year)
    )
    np.testing.assert_allclose(
        outputs["salt"] - sales_or_income_tax,
        filer_sums["real_estate_taxes"],
        rtol=1e-6,
        atol=tol,
    )
    np.testing.assert_allclose(
        outputs["total_misc_deductions"],
        filer_sums["unreimbursed_business_employee_expenses"]
        + filer_sums["tax_preparation_fees"],
        rtol=1e-6,
        atol=tol,
    )
    np.testing.assert_allclose(
        outputs["wagering_losses_deduction"],
        np.minimum(filer_sums["gambling_losses"], filer_sums["gambling_winnings"]),
        rtol=1e-6,
        atol=tol,
    )
    # A unit with no filer payments has no deduction from these sources.
    no_filer_payments = (
        filer_sums["real_estate_taxes"]
        + filer_sums["deductible_mortgage_interest"]
        + filer_sums["investment_interest_expense"]
        + filer_sums["charitable_cash_donations"]
        + filer_sums["charitable_non_cash_donations"]
        == 0
    )
    for v in (
        "capped_property_taxes",
        "interest_deduction",
        "charitable_deduction",
        "pr_mortgage_deduction",
    ):
        assert (outputs[v][no_filer_payments] == 0).all(), v


@hypothesis.settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[
        hypothesis.HealthCheck.too_slow,
        hypothesis.HealthCheck.data_too_large,
    ],
)
@hypothesis.given(
    st.lists(tax_unit, min_size=1, max_size=8),
    st.sampled_from(YEARS),
)
def test_dependents_expenses_leave_filers_deductions_unchanged(units, year):
    check(units, year)
