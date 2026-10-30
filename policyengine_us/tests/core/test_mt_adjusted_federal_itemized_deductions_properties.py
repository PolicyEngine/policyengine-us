"""Montana's deduction from 2024 is the federal one, less state income tax.

From 2024 Montana taxable income starts from federal taxable income (MCA
15-30-2120(1)), so the return uses the federal deduction type. A federal
itemizer deducts the federal itemized deductions (Form 1040, line 12) less the
state income tax deducted on Schedule A, but MCA 15-30-2120(2)(j) adds the tax
back only down to the federal standard deduction. A federal non-itemizer
deducts the federal standard deduction and, from 2026, the section 170(p)
charitable deduction (26 U.S.C. 63(b)(4)).

The model computes the add-back in statutory form, itemized - min(tax,
max(itemized - standard, 0)). This test restates it independently in the form
of the 2024 Form 2 Worksheet A, the greater of itemized - tax and the standard
deduction (for a total at or above the standard deduction), with the state
income tax found as the 2025 Schedule I Worksheet B does: the capped SALT
deduction less local income and real estate taxes, and nothing for a filer who
deducts sales tax. Generated returns vary the filing status, dependents,
wages, real estate taxes per spouse, mortgage interest, cash gifts, medical
expenses, casualty losses and the state income and sales taxes.

Invariants, for every generated return and year:
1. The model equals the Worksheet A restatement (a differential check).
2. min(itemized, standard) <= Montana amount <= itemized.
3. The amount removed is at most the state income tax and the SALT deduction.
4. Only the head carries the joint amount, once per return, whatever the
   number of members.
5. Montana taxable income uses the federal deduction type.
6. More cash gifts never lower the Montana amount.
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEARS = [2024, 2025, 2026]
# Values are float32; sums near $1,000,000 can differ by a few cents.
TOLERANCE = 0.1

dollars = lambda high: st.integers(min_value=0, max_value=high)  # noqa: E731

returns = st.fixed_dictionaries(
    {
        "joint": st.booleans(),
        "dependents": st.integers(min_value=0, max_value=2),
        "head_wages": st.sampled_from([0, 40_000, 120_000, 650_000, 1_200_000])
        | dollars(400_000),
        "spouse_wages": dollars(200_000),
        "head_real_estate_taxes": dollars(25_000),
        "spouse_real_estate_taxes": dollars(25_000),
        "mortgage_interest": dollars(60_000),
        "cash_gifts": dollars(30_000),
        "medical_expenses": dollars(40_000),
        "casualty_loss_deduction": st.sampled_from([0, 0, 15_000]),
        # None leaves the model's own estimate of state income tax.
        "state_income_tax": st.none() | dollars(40_000),
        "sales_tax": st.none() | dollars(10_000),
        "extra_cash_gifts": st.integers(min_value=1, max_value=20_000),
    }
)


def _situation(year, specs):
    """Two copies of each return; the second gives more cash gifts."""
    people, tax_units, households, marital_units = {}, {}, {}, {}
    for i, spec in enumerate(specs):
        for copy, extra_gifts in (("base", 0), ("more", spec["extra_cash_gifts"])):
            unit = f"u{i}_{copy}"
            head, spouse = f"{unit}_head", f"{unit}_spouse"
            people[head] = {
                "age": {year: 45},
                "employment_income": {year: spec["head_wages"]},
                "real_estate_taxes": {year: spec["head_real_estate_taxes"]},
                "deductible_mortgage_interest": {year: spec["mortgage_interest"]},
                "charitable_cash_donations": {year: spec["cash_gifts"] + extra_gifts},
                "other_medical_expenses": {year: spec["medical_expenses"]},
            }
            couple = [head]
            if spec["joint"]:
                people[spouse] = {
                    "age": {year: 43},
                    "employment_income": {year: spec["spouse_wages"]},
                    "real_estate_taxes": {year: spec["spouse_real_estate_taxes"]},
                }
                couple.append(spouse)
            members = list(couple)
            for d in range(spec["dependents"]):
                child = f"{unit}_child{d}"
                people[child] = {
                    "age": {year: 10},
                    "is_tax_unit_dependent": {year: True},
                }
                members.append(child)
                marital_units[child] = {"members": [child]}
            tax_unit = {
                "members": members,
                "casualty_loss_deduction": {year: spec["casualty_loss_deduction"]},
            }
            if spec["state_income_tax"] is not None:
                tax_unit["state_withheld_income_tax"] = {year: spec["state_income_tax"]}
            if spec["sales_tax"] is not None:
                tax_unit["state_sales_tax"] = {year: spec["sales_tax"]}
                tax_unit["local_sales_tax"] = {year: 0}
            tax_units[unit] = tax_unit
            households[unit] = {"members": members, "state_code": {year: "MT"}}
            marital_units[unit] = {"members": couple}
    return {
        "people": people,
        "tax_units": tax_units,
        "households": households,
        "marital_units": marital_units,
    }


def _real_estate_taxes(specs):
    """Each return's real estate taxes, from the inputs."""
    return np.repeat(
        [
            s["head_real_estate_taxes"] + s["joint"] * s["spouse_real_estate_taxes"]
            for s in specs
        ],
        2,
    )


@pytest.mark.parametrize("year", YEARS)
@settings(max_examples=6, deadline=None, derandomize=True)
@given(specs=st.lists(returns, min_size=3, max_size=6))
def test_montana_deduction_follows_the_federal_return(year, specs):
    sim = Simulation(tax_benefit_system=system, situation=_situation(year, specs))

    def unit(variable):
        return np.asarray(sim.calculate(variable, year), dtype=float)

    itemized = unit("itemized_taxable_income_deductions")
    standard = unit("standard_deduction")
    salt = unit("salt_deduction")
    income_tax = unit("state_withheld_income_tax")
    local_income_tax = unit("local_income_tax")
    sales_tax = unit("state_sales_tax") + unit("local_sales_tax")
    montana = unit("mt_adjusted_federal_itemized_deductions")

    # 1. Worksheet B lines 1-5 and Worksheet A lines 1-5.
    deducts_sales_tax = sales_tax > income_tax + local_income_tax
    state_income_tax_deducted = np.where(
        deducts_sales_tax,
        0,
        np.maximum(salt - local_income_tax - _real_estate_taxes(specs), 0),
    )
    worksheet_a = np.where(
        itemized >= standard,
        np.maximum(itemized - state_income_tax_deducted, standard),
        itemized,
    )
    np.testing.assert_allclose(montana, worksheet_a, rtol=0, atol=TOLERANCE)

    # 2. Bounds.
    assert np.all(montana <= itemized + TOLERANCE)
    assert np.all(montana >= np.minimum(itemized, standard) - TOLERANCE)

    # 3. Only state income tax inside the SALT deduction is removed.
    removed = itemized - montana
    assert np.all(removed <= income_tax + TOLERANCE)
    assert np.all(removed <= salt + TOLERANCE)

    # 4. The head carries the return's amount, once.
    joint = np.asarray(sim.calculate("mt_itemized_deductions_joint", year))
    head = np.asarray(sim.calculate("is_tax_unit_head", year))
    assert np.all(joint[~head] == 0)
    for variable in (
        "mt_itemized_deductions_joint",
        "mt_itemized_deductions_for_federal_itemization_joint",
    ):
        np.testing.assert_allclose(
            np.asarray(sim.calculate(variable, year, map_to="tax_unit")),
            montana,
            rtol=0,
            atol=TOLERANCE,
            err_msg=variable,
        )

    # 5. The federal deduction type.
    itemizes = unit("tax_unit_itemizes").astype(bool)
    non_itemizer_charity = unit("charitable_deduction_for_non_itemizers")
    deduction = np.where(itemizes, montana, standard + non_itemizer_charity)
    p = system.parameters(year).gov.states.mt.tax.income.exemptions
    assert not p.applies
    np.testing.assert_allclose(
        unit("mt_taxable_income"),
        np.maximum(unit("mt_agi") - deduction, 0),
        rtol=0,
        atol=TOLERANCE,
    )

    # 6. More cash gifts never lower the Montana amount.
    base, more = montana[0::2], montana[1::2]
    assert np.all(more >= base - TOLERANCE)
