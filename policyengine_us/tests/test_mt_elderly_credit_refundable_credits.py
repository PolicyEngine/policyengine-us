"""Worked example: federal refundable credits received in the Montana elderly
homeowner/renter credit's gross household income.

MCA 15-30-2337(4) defines gross household income as "all income received by
all individuals of a household", ARM 42.4.301(2)(b) counts "federal
refundable tax credits received", and the 2024 Schedule 2EC line 8 combines
"all the refundable credits received by all household members". The credits
claimed on a return are paid after its year ends, so the model counts the
federal refundable credits each person received during the year
(mt_elderly_homeowner_or_renter_credit_federal_refundable_credits): the 2020
and 2021 Economic Impact Payments by default, which are zero in 2024, plus
other receipts supplied through
mt_elderly_homeowner_or_renter_credit_other_federal_refundable_credits, not
the current return's entitlement.

YAML cases cannot compare two simulations, so this file does. It runs one
household, a claimant aged 70 and a daughter who files her own return with
one child, twice: with the federal refundable credits each person received
(W) and with none received (Z). It checks, against the 2024 Schedule 2EC:

1. An entitlement is not a receipt: in Z the receipt is zero, though the
   daughter's return has 4,525 of federal refundable credits.
2. Accounting: gross household income in W exceeds Z by exactly the credits
   received, counted once.
3. More income never raises the credit: the credit in W is at most Z's.
4. The credit is between zero and the cap.
5. Montana tax changes only through the credit: Montana refundable credits
   other than this one are the same in W and Z, and the household's Montana
   income tax rises by exactly the fall in its credit.

The model computes in single precision, so comparisons allow one cent or
eight float32 spacings at the amount compared, whichever is larger.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2024
CAP = 1_150
TOLERANCE = 0.01
FEDERAL = "mt_elderly_homeowner_or_renter_credit_federal_refundable_credits"
OTHER = "mt_elderly_homeowner_or_renter_credit_other_federal_refundable_credits"
GROSS = "mt_elderly_homeowner_or_renter_credit_gross_household_income"
CREDIT = "mt_elderly_homeowner_or_renter_credit"


def build_situation(cases, received):
    """One Montana household per case: the claimant files alone; the member
    files with their children. With `received`, each adult received the
    case's federal refundable credits during the year. Also returns each
    person's and tax unit's case index."""
    people, tax_units, households, case_of = {}, {}, {}, {}
    for i, c in enumerate(cases):
        claimant, member = f"claimant_{i}", f"member_{i}"
        children = [f"child_{i}_{j}" for j in range(len(c["child_ages"]))]
        people[claimant] = {
            "age": {YEAR: c["claimant_age"]},
            "taxable_pension_income": {YEAR: c["pension"]},
            "real_estate_taxes": {YEAR: c["property_tax"]},
            "rent": {YEAR: c["rent"]},
            OTHER: {YEAR: c["claimant_received"] if received else 0},
        }
        people[member] = {
            "age": {YEAR: c["member_age"]},
            "employment_income": {YEAR: c["wages"]},
            OTHER: {YEAR: c["member_received"] if received else 0},
        }
        for child, age in zip(children, c["child_ages"]):
            people[child] = {"age": {YEAR: age}}
        tax_units[f"claimant_unit_{i}"] = {"members": [claimant]}
        tax_units[f"member_unit_{i}"] = {"members": [member, *children]}
        for name in [claimant, member, *children, *list(tax_units)[-2:]]:
            case_of[name] = i
        households[f"household_{i}"] = {
            "members": [claimant, member, *children],
            "state_code": {YEAR: "MT"},
        }
    situation = {"people": people, "tax_units": tax_units, "households": households}
    return situation, case_of


def calculate(cases, received):
    """Household totals of person- and tax-unit-level variables, summed by
    entity id rather than array position."""
    situation, case_of = build_situation(cases, received)
    simulation = Simulation(situation=situation)

    def by_household(variable, entity):
        values = np.asarray(simulation.calculate(variable, YEAR), dtype=float)
        totals = np.zeros(len(cases))
        for name, value in zip(simulation.populations[entity].ids, values):
            totals[case_of[name]] += value
        return totals

    return {
        "federal_person": by_household(FEDERAL, "person"),
        "federal_tax_unit": by_household("income_tax_refundable_credits", "tax_unit"),
        "gross": by_household(GROSS, "person"),
        "credit": by_household(CREDIT, "person"),
        "mt_other_credits": by_household(
            "mt_refundable_credits_before_renter_credit", "person"
        ),
        "mt_income_tax": by_household("mt_income_tax", "tax_unit"),
    }


def tolerance(amount):
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(abs(amount)))))


def assert_properties(cases):
    w = calculate(cases, received=True)
    z = calculate(cases, received=False)
    for i, c in enumerate(cases):
        tol = tolerance(w["gross"][i])
        received = c["claimant_received"] + c["member_received"]
        # 1. This year's federal refundable credits are not a receipt, and
        # no Economic Impact Payment was made in 2024.
        assert z["federal_person"][i] == 0, c
        assert w["federal_person"][i] == pytest.approx(received, abs=tol), c
        # 2. The credits received are the whole difference in gross
        # household income, counted once.
        assert w["gross"][i] - z["gross"][i] == pytest.approx(received, abs=tol), c
        # 3. More income never raises the credit.
        assert w["credit"][i] <= z["credit"][i] + tol, c
        for result in (w, z):
            # 4. Bounds.
            assert -tol <= result["credit"][i] <= CAP + tol, c
        # 5. Montana tax moves only through this credit.
        assert w["mt_other_credits"][i] == pytest.approx(
            z["mt_other_credits"][i], abs=TOLERANCE
        ), c
        assert w["mt_income_tax"][i] - z["mt_income_tax"][i] == pytest.approx(
            z["credit"][i] - w["credit"][i], abs=tolerance(z["credit"][i])
        ), c


def test_worked_example():
    """2024 Schedule 2EC: the claimant's line 5 pension 20,000; the
    daughter's wages 10,000 (line 17). Her 2024 return has a federal EITC of
    34% x 10,000 = 3,400, a refundable child tax credit of min(1,700, 15% x
    7,500) = 1,125 and a Montana EITC of 340, all paid in 2025, so none is
    received in 2024. Line 8 counts the federal credits she received during
    2024, a supplied receipt of 4,525. Line 18 = 34,525; line 22 =
    (34,525 - 12,600) x
    0.05 = 1,096.25; line 27 = 2,000 - 1,096.25 = 903.75; line 30 = 903.75.
    With nothing received, line 18 = 30,000, line 22 = 870 and line 30 =
    1,130."""
    case = {
        "claimant_age": 70,
        "pension": 20_000,
        "property_tax": 2_000,
        "rent": 0,
        "claimant_received": 0,
        "member_age": 30,
        "wages": 10_000,
        "child_ages": [5],
        "member_received": 4_525,
    }
    w = calculate([case], received=True)
    z = calculate([case], received=False)
    assert z["federal_tax_unit"][0] == pytest.approx(4_525, abs=TOLERANCE)
    assert z["federal_person"][0] == 0
    assert w["gross"][0] == pytest.approx(34_525, abs=TOLERANCE)
    assert w["credit"][0] == pytest.approx(903.75, abs=TOLERANCE)
    assert z["gross"][0] == pytest.approx(30_000, abs=TOLERANCE)
    assert z["credit"][0] == pytest.approx(1_130, abs=TOLERANCE)
    assert_properties([case])
