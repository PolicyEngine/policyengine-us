"""Alabama and North Carolina deduct only the mortgage interest federal law allows.

Code of Alabama 40-18-15(a)(2) limits the interest deduction to "the amount
allowable as an interest deduction for federal income tax purposes in the
corresponding tax year". N.C. Gen. Stat. 105-153.5(a)(2)b allows "the amount
allowed as a deduction for interest paid or accrued during the taxable year
under section 163(h) of the Code with respect to any qualified residence".
So interest on acquisition debt above the 26 U.S.C. 163(h)(3) limits is never
an Alabama or North Carolina deduction.

A grid of couples with one acquisition mortgage (balance, origination year,
interest) in each state shares one simulation per year. The federal limit is
restated here independently of the parameter files: $1,000,000 of debt
incurred before the TCJA date ($750,000 after), with interest prorated by the
share of the balance under the limit. PolicyEngine approximates the Dec. 15,
2017 date by origination year 2017, and treats a mortgage with no reported
balance as fully deductible; the restatement uses the same input conventions.

1. Alabama's interest deduction equals the allowed interest.
2. North Carolina's itemized deductions equal the allowed interest, capped at
   $20,000 (the other components are zero).
3. Interest above the limits does not change either state's income tax: each
   couple pays the same state tax as a twin couple with no reported balance
   whose interest is the allowed amount.
"""

from itertools import product

import numpy as np
import pytest

from policyengine_us import Simulation

YEARS = range(2021, 2027)
TAX_CHECK_YEARS = (2021, 2026)
STATES = ("AL", "NC")
# Balances below, at and above each limit, on either side of the TCJA date.
BALANCES = (0, 750_000, 1_000_000, 2_500_000)
ORIGINATION_YEARS = (2017, 2018)
INTERESTS = (15_000, 40_000)
MORTGAGES = tuple(product(BALANCES, ORIGINATION_YEARS, INTERESTS))
NC_MORTGAGE_AND_PROPERTY_TAX_CAP = 20_000


def allowed_interest(interest, balance, origination_year):
    """Home mortgage interest allowed under 26 U.S.C. 163(h)(3)."""
    if balance == 0:
        return interest
    cap = 1_000_000 if origination_year <= 2017 else 750_000
    return interest * min(1, cap / balance)


ALLOWED = np.array([allowed_interest(i, b, o) for b, o, i in MORTGAGES])
# Twins report no balance, so all of their interest (the allowed amount) is
# deductible.
TWINS = tuple((0, 0, float(allowed)) for allowed in ALLOWED)
# Each state's units: the grid, then its twins.
UNITS = tuple((state, *m) for state in STATES for m in MORTGAGES + TWINS)
N = len(MORTGAGES)


def _situation(year):
    period = str(year)
    people, tax_units, households, marital_units = {}, {}, {}, {}
    for i, (state, balance, origination, interest) in enumerate(UNITS):
        head, spouse = f"u{i}_head", f"u{i}_spouse"
        people[head] = {
            "age": {period: 50},
            "employment_income": {period: 150_000},
            "home_mortgage_interest": {period: interest},
        }
        people[spouse] = {
            "age": {period: 50},
            "employment_income": {period: 50_000},
        }
        members = [head, spouse]
        tax_units[f"u{i}"] = {
            "members": members,
            "first_home_mortgage_balance": {period: balance},
            "first_home_mortgage_origination_year": {period: origination},
        }
        households[f"u{i}"] = {"members": members, "state_code": {period: state}}
        marital_units[f"u{i}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "households": households,
        "marital_units": marital_units,
    }


@pytest.mark.parametrize("year", YEARS)
def test_alabama_and_north_carolina_count_only_federally_allowed_interest(year):
    sim = Simulation(situation=_situation(year))

    def by_state(variable):
        values = np.asarray(sim.calculate(variable, year), dtype=float)
        return {
            state: values[2 * N * s : 2 * N * (s + 1)] for s, state in enumerate(STATES)
        }

    # 1. Alabama's interest deduction.
    al_interest = by_state("al_interest_deduction")["AL"]
    np.testing.assert_allclose(
        al_interest[:N], ALLOWED, atol=0.01, err_msg=f"AL interest in {year}"
    )

    # 2. North Carolina's itemized deductions. Charity, medical expenses and
    # property taxes are zero, so only the capped mortgage interest remains.
    nc_itemized = by_state("nc_itemized_deductions")["NC"]
    np.testing.assert_allclose(
        nc_itemized[:N],
        np.minimum(ALLOWED, NC_MORTGAGE_AND_PROPERTY_TAX_CAP),
        atol=0.01,
        err_msg=f"NC itemized deductions in {year}",
    )

    # 3. Each couple and its twin pay the same state income tax. The full tax
    # chain is the costly part, so it runs in one year before the TCJA limits
    # were made permanent and one after (TAX_CHECK_YEARS).
    if year not in TAX_CHECK_YEARS:
        return
    for state, variable in (("AL", "al_income_tax"), ("NC", "nc_income_tax")):
        tax = by_state(variable)[state]
        np.testing.assert_allclose(
            tax[:N], tax[N:], atol=0.01, err_msg=f"{variable} in {year}"
        )
