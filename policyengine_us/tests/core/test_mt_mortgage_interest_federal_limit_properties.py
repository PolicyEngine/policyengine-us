"""Montana's itemized mortgage interest is the amount federal law allows.

Former MCA 15-30-2131(1)(a) allowed the items in 26 U.S.C. 161 (which
includes section 163 interest), and MCA 15-30-2101 reads "Internal Revenue
Code" as the Code as amended. The Form 2 instructions for itemized deductions
line 9 (2018-2023) say to enter the home mortgage interest "allowed by federal
law" and that interest on acquisition debt incurred after Dec. 15, 2017 "is
limited to the first $750,000". From 2024 Montana starts from the federal
itemized deductions. So interest on acquisition debt above the 26 U.S.C.
163(h)(3) caps is never a Montana deduction.

A grid of couples with one acquisition mortgage (balance, origination year,
interest) shares one simulation per year. The other Montana itemized
components are set to zero so each variable is its mortgage interest line,
and the federal limit is restated here independently of the parameter files:
$1,000,000 of debt incurred before the TCJA date ($750,000 after), with
interest prorated by the share of the balance under the cap. PolicyEngine
approximates the Dec. 15, 2017 date by origination year 2017, and treats a
mortgage with no reported balance as fully deductible; the restatement uses
the same input conventions.

1. Joint returns (every year): the Montana joint itemized deductions, and the
   variant used for the federal itemization choice, equal the allowed amount.
2. Spouses filing separately on the same form (through 2023): each spouse's
   deduction is the allowed amount times the share of the interest that
   spouse reported, and the two sum to the allowed amount.
"""

from itertools import product

import numpy as np
import pytest

from policyengine_us import Simulation

YEARS = range(2021, 2027)
BALANCES = (0, 300_000, 750_000, 1_000_000, 2_500_000)
ORIGINATION_YEARS = (2005, 2017, 2018, 2024)
INTERESTS = (0, 15_000, 40_000)
SPOUSE_SHARES = (0.0, 0.25)  # share of the interest the spouse reported
UNITS = tuple(product(BALANCES, ORIGINATION_YEARS, INTERESTS, SPOUSE_SHARES))

ZERO_PERSON_COMPONENTS = (
    "mt_misc_deductions",
    "mt_medical_expense_deduction_joint",
    "mt_medical_expense_deduction_indiv",
    "mt_salt_deduction",
    "mt_federal_income_tax_deduction_indiv",
    "mt_federal_income_tax_deduction_for_federal_itemization_indiv",
)
ZERO_TAX_UNIT_COMPONENTS = (
    "charitable_deduction",
    "mt_federal_income_tax_deduction_unit",
    "mt_federal_income_tax_deduction_for_federal_itemization",
)


def allowed_interest(interest, balance, origination_year):
    """Home mortgage interest allowed under 26 U.S.C. 163(h)(3)."""
    if balance == 0:
        return interest
    cap = 1_000_000 if origination_year <= 2017 else 750_000
    return interest * min(1, cap / balance)


def _situation(year):
    period = str(year)
    people, tax_units, households, marital_units = {}, {}, {}, {}
    for i, (balance, origination, interest, spouse_share) in enumerate(UNITS):
        head, spouse = f"u{i}_head", f"u{i}_spouse"
        for name, role, share in (
            (head, "is_tax_unit_head", 1 - spouse_share),
            (spouse, "is_tax_unit_spouse", spouse_share),
        ):
            people[name] = {
                "age": {period: 50},
                role: {period: True},
                "home_mortgage_interest": {period: interest * share},
                **{v: {period: 0} for v in ZERO_PERSON_COMPONENTS},
            }
        members = [head, spouse]
        tax_units[f"u{i}"] = {
            "members": members,
            "first_home_mortgage_balance": {period: balance},
            "first_home_mortgage_origination_year": {period: origination},
            **{v: {period: 0} for v in ZERO_TAX_UNIT_COMPONENTS},
        }
        households[f"u{i}"] = {"members": members, "state_code": {period: "MT"}}
        marital_units[f"u{i}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "households": households,
        "marital_units": marital_units,
    }


@pytest.mark.parametrize("year", YEARS)
def test_montana_mortgage_interest_is_the_federally_allowed_amount(year):
    sim = Simulation(situation=_situation(year))

    def per_person(variable):
        return np.asarray(sim.calculate(variable, year), dtype=float).reshape(-1, 2)

    allowed = np.array(
        [
            allowed_interest(interest, balance, origination)
            for balance, origination, interest, _ in UNITS
        ]
    )
    spouse_share = np.array([unit[3] for unit in UNITS])

    # 1. Joint returns. The head-only units (spouse share 0) keep this check
    # independent of how the joint formula splits interest between spouses.
    head_only = spouse_share == 0
    for variable in (
        "mt_itemized_deductions_joint",
        "mt_itemized_deductions_for_federal_itemization_joint",
    ):
        np.testing.assert_allclose(
            per_person(variable).sum(axis=1)[head_only],
            allowed[head_only],
            atol=0.01,
            err_msg=f"{variable} in {year}",
        )

    # 2. Spouses filing separately on the same form.
    p = sim.tax_benefit_system.parameters(year).gov.states.mt.tax.income
    if not p.married_filing_separately_on_same_return_allowed:
        return
    expected = np.stack([allowed * (1 - spouse_share), allowed * spouse_share], 1)
    for variable in (
        "mt_itemized_deductions_indiv",
        "mt_itemized_deductions_for_federal_itemization_indiv",
    ):
        np.testing.assert_allclose(
            per_person(variable),
            expected,
            atol=0.01,
            err_msg=f"{variable} in {year}",
        )
