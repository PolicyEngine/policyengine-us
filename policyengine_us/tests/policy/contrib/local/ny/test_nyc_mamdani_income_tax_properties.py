"""Properties of the Mamdani NYC income tax contributed reform.

The surtax is levied once per return on the tax unit's NYC taxable income. An
earlier version computed it for every person from the tax unit's income and
then summed over the unit, so a four-person household paid four times the
surtax. Each test evaluates a grid of tax units in one vectorized simulation,
switching the reform on through ``gov.local.ny.mamdani_income_tax.in_effect``
(the path the app uses, which also exercises the registration in
``reforms.py``), and checks that:

- the change in ``nyc_income_tax_before_credits`` equals a closed-form reference,
  2% of NYC taxable income above $1 million, for every filing status (so the
  reform's copy of the regular rate schedule agrees with the baseline formula);
- that change does not depend on how many people are in the tax unit;
- it equals the reform's ``nyc_mamdani_income_tax`` output, is non-negative, is
  zero at or below the threshold and rises with taxable income;
- it is zero outside NYC; and
- it is zero in years before ``in_effect`` turns on, even though the factory
  installs the reform for the whole simulation from the first of the next five
  years in which it is in effect.
"""

import itertools

import numpy as np
from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation

# Mamdani Revenue Proposal, as encoded in
# parameters/gov/local/ny/mamdani_income_tax/rate.yaml: 2% of NYC taxable
# income above $1 million.
THRESHOLD = 1_000_000
RATE = 0.02

TAXABLE_INCOMES = [
    -50_000,
    0,
    1,
    500_000,
    999_999,
    1_000_000,
    1_000_001,
    1_500_000,
    2_000_000,
    10_000_000,
]
FILING_STATUSES = [
    "SINGLE",
    "JOINT",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
    "SEPARATE",
]
MAX_MEMBERS = 6
# Tax variables are float32; the defect this guards against is a multiple of
# the surtax, so a sub-dollar tolerance only absorbs rounding.
TOLERANCE = 0.5


def member_counts(filing_status):
    # A joint return always has a head and a spouse.
    return range(2 if filing_status == "JOINT" else 1, MAX_MEMBERS + 1)


GRID = [
    (income, filing_status, members)
    for income, filing_status in itertools.product(TAXABLE_INCOMES, FILING_STATUSES)
    for members in member_counts(filing_status)
]


def reference_surtax(taxable_income):
    return RATE * np.maximum(taxable_income - THRESHOLD, 0)


def activate_from(start):
    """A user reform that turns the Mamdani tax on from ``start`` onward."""

    class ActivateMamdaniTax(Reform):
        def apply(self):
            def modify(parameters):
                parameters.gov.local.ny.mamdani_income_tax.in_effect.update(
                    start=instant(start),
                    stop=instant("2100-12-31"),
                    value=True,
                )
                return parameters

            self.modify_parameters(modify)

    return ActivateMamdaniTax


def grid_situation(years, in_nyc=True):
    """One tax unit and household per grid point: a head, a spouse on joint
    returns, and dependents making up the rest of the members."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i, (income, filing_status, members) in enumerate(GRID):
        names = [f"g{i}_m{j}" for j in range(members)]
        for j, name in enumerate(names):
            is_adult = j == 0 or (j == 1 and filing_status == "JOINT")
            situation["people"][name] = {
                "age": {year: 45 if is_adult else 10 for year in years}
            }
        situation["tax_units"][f"tu{i}"] = {
            "members": names,
            "filing_status": {year: filing_status for year in years},
            "nyc_taxable_income": {year: income for year in years},
        }
        situation["households"][f"hh{i}"] = {
            "members": names,
            "state_code": {year: "NY" for year in years},
            "in_nyc": {year: in_nyc for year in years},
        }
    return situation


def grid_columns():
    income = np.array([g[0] for g in GRID], dtype=float)
    filing_status = np.array([g[1] for g in GRID])
    members = np.array([g[2] for g in GRID])
    return income, filing_status, members


def tax_change(year, reform, in_nyc=True, years=None):
    situation = grid_situation(years or [str(year)], in_nyc)
    baseline = Simulation(situation=situation)
    reformed = Simulation(situation=situation, reform=reform)
    variable = "nyc_income_tax_before_credits"
    change = reformed.calculate(variable, year) - baseline.calculate(variable, year)
    return change, reformed.calculate("nyc_mamdani_income_tax", year)


def test_tax_change_matches_reference_for_every_household_size():
    income, _, _ = grid_columns()
    change, surtax = tax_change(2026, activate_from("2026-01-01"))
    np.testing.assert_allclose(change, reference_surtax(income), atol=TOLERANCE)
    np.testing.assert_allclose(surtax, change, atol=TOLERANCE)


def test_tax_change_is_invariant_to_number_of_members():
    income, filing_status, members = grid_columns()
    change, _ = tax_change(2026, activate_from("2026-01-01"))
    for value, status in itertools.product(TAXABLE_INCOMES, FILING_STATUSES):
        cell = (income == value) & (filing_status == status)
        assert len(set(members[cell])) > 1
        np.testing.assert_allclose(
            change[cell],
            np.full(cell.sum(), change[cell][0]),
            atol=TOLERANCE,
            err_msg=f"{status} at {value} varies with household size",
        )


def test_tax_change_bounds_and_monotonicity():
    income, filing_status, members = grid_columns()
    change, _ = tax_change(2026, activate_from("2026-01-01"))
    assert np.all(change >= -TOLERANCE)
    assert np.all(np.abs(change[income <= THRESHOLD]) <= TOLERANCE)
    for status, count in {(g[1], g[2]) for g in GRID}:
        cell = (filing_status == status) & (members == count)
        by_income = change[cell][np.argsort(income[cell])]
        assert np.all(np.diff(by_income) >= -TOLERANCE)


def test_no_tax_change_outside_nyc():
    change, surtax = tax_change(2026, activate_from("2026-01-01"), in_nyc=False)
    np.testing.assert_allclose(change, 0, atol=TOLERANCE)
    np.testing.assert_allclose(surtax, 0, atol=TOLERANCE)


def test_no_tax_change_before_delayed_activation():
    income, _, _ = grid_columns()
    years = ["2026", "2028"]
    reform = activate_from("2028-01-01")
    change_2026, surtax_2026 = tax_change(2026, reform, years=years)
    np.testing.assert_allclose(change_2026, 0, atol=TOLERANCE)
    np.testing.assert_allclose(surtax_2026, 0, atol=TOLERANCE)
    change_2028, _ = tax_change(2028, reform, years=years)
    np.testing.assert_allclose(change_2028, reference_surtax(income), atol=TOLERANCE)
