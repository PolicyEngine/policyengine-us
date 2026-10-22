"""Invariants of SNAP's treatment of rental and farm rental income.

snap_rental_income and snap_farm_rent_income count rental_income and
farm_rent_income as unearned income under 7 CFR 273.9(b)(2)(ii), each with a
loss floored at zero, because 7 U.S.C. 2014(d)(9) and 7 CFR 273.11(a)(2)(ii)
let only self-employed farmers' losses offset other household income.

Over an exhaustive grid of annual rent R, farm rent F, wages and other
unearned income, the tests check:

1. snap_rental_income == max(R, 0) / 12 and
   snap_farm_rent_income == max(F, 0) / 12, so neither is negative.
2. Rent and farm rent are interchangeable: swapping R and F leaves
   snap_gross_income, snap_net_income and snap unchanged. This is a
   differential check of the two paths into SNAP unearned income.
3. Losses are inert: whenever R <= 0 and F <= 0, SNAP unearned, gross and net
   income and the benefit equal those of the same household with R = F = 0.
4. Counted rent reaches gross income exactly once:
   snap_gross_income(R, F) - snap_gross_income(0, 0) ==
   snap_rental_income + snap_farm_rent_income.
5. Monotonicity: holding everything else fixed, more rent or farm rent never
   lowers SNAP gross income and never raises the SNAP benefit.

These are properties of SNAP's own computation. Another program whose output
SNAP counts as income can break 2, 3 and 5 when it reads these inputs: SSI
counts rental_income without a floor and ignores farm_rent_income, and a TANF
benefit that ends at an income threshold can lower SNAP income as rent rises.
The grid therefore uses a one-person Texas household aged 31, who receives
neither SSI nor TANF.
"""

from itertools import product

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2026
MONTH = f"{YEAR}-01"

# Annual amounts. Multiples of 12 keep monthly values exact in float32.
RENT_VALUES = (-60_000, -1_920, -12, 0, 12, 1_920, 12_000, 240_000)
WAGE_VALUES = (0, 5_923)
FINANCIAL_ASSISTANCE_VALUES = (0, 13_000)

GRID = list(product(RENT_VALUES, RENT_VALUES, WAGE_VALUES, FINANCIAL_ASSISTANCE_VALUES))

OUTPUTS = (
    "snap_rental_income",
    "snap_farm_rent_income",
    "snap_unearned_income",
    "snap_gross_income",
    "snap_net_income",
    "snap",
)


def _simulate(cases):
    """Run one simulation with a separate one-person household per case."""
    people, households, spm_units = {}, {}, {}
    tax_units, families, marital_units = {}, {}, {}
    for i, (rent, farm_rent, wages, assistance) in enumerate(cases):
        person = f"p{i}"
        people[person] = {
            "age": {YEAR: 31},
            # Clears the SNAP work requirement for an adult without
            # dependents, so the member's income counts in full.
            "weekly_hours_worked_before_lsr": {YEAR: 40},
            "rental_income": {YEAR: rent},
            "farm_rent_income": {YEAR: farm_rent},
            "employment_income": {YEAR: wages},
            "financial_assistance": {YEAR: assistance},
        }
        households[f"h{i}"] = {"members": [person], "state_code": {YEAR: "TX"}}
        spm_units[f"s{i}"] = {"members": [person]}
        tax_units[f"t{i}"] = {"members": [person]}
        families[f"f{i}"] = {"members": [person]}
        marital_units[f"m{i}"] = {"members": [person]}
    simulation = Simulation(
        situation={
            "people": people,
            "households": households,
            "spm_units": spm_units,
            "tax_units": tax_units,
            "families": families,
            "marital_units": marital_units,
        }
    )
    results = {
        variable: np.asarray(simulation.calculate(variable, MONTH), dtype=float)
        for variable in OUTPUTS
    }
    return {
        case: {variable: results[variable][i] for variable in OUTPUTS}
        for i, case in enumerate(cases)
    }


@pytest.fixture(scope="module")
def grid_results():
    return _simulate(GRID)


def test_rent_and_farm_rent_are_floored_and_never_negative(grid_results):
    for (rent, farm_rent, _, _), result in grid_results.items():
        assert result["snap_rental_income"] == pytest.approx(
            max(rent, 0) / 12, abs=0.01
        )
        assert result["snap_farm_rent_income"] == pytest.approx(
            max(farm_rent, 0) / 12, abs=0.01
        )
        assert result["snap_rental_income"] >= 0
        assert result["snap_farm_rent_income"] >= 0


def test_rent_and_farm_rent_are_interchangeable(grid_results):
    for (rent, farm_rent, wages, assistance), result in grid_results.items():
        swapped = grid_results[(farm_rent, rent, wages, assistance)]
        for variable in ("snap_gross_income", "snap_net_income", "snap"):
            assert result[variable] == pytest.approx(swapped[variable], abs=0.01)


def test_rental_losses_do_not_change_snap(grid_results):
    # Each loss is inert whatever the sign of the other: a household equals
    # the same household with every loss replaced by zero.
    for (rent, farm_rent, wages, assistance), result in grid_results.items():
        losses_zeroed = grid_results[
            (max(rent, 0), max(farm_rent, 0), wages, assistance)
        ]
        for variable in (
            "snap_unearned_income",
            "snap_gross_income",
            "snap_net_income",
            "snap",
        ):
            assert result[variable] == pytest.approx(losses_zeroed[variable], abs=0.01)


def test_counted_rent_reaches_gross_income_once(grid_results):
    for (rent, farm_rent, wages, assistance), result in grid_results.items():
        no_rent = grid_results[(0, 0, wages, assistance)]
        counted = result["snap_rental_income"] + result["snap_farm_rent_income"]
        assert result["snap_gross_income"] - no_rent[
            "snap_gross_income"
        ] == pytest.approx(counted, abs=0.02)


def test_more_rent_never_lowers_gross_income_or_raises_benefit(grid_results):
    ascending = sorted(RENT_VALUES)
    for other, wages, assistance in product(
        RENT_VALUES, WAGE_VALUES, FINANCIAL_ASSISTANCE_VALUES
    ):
        for results in (
            [grid_results[(r, other, wages, assistance)] for r in ascending],
            [grid_results[(other, f, wages, assistance)] for f in ascending],
        ):
            for lower, higher in zip(results, results[1:]):
                assert higher["snap_gross_income"] >= lower["snap_gross_income"] - 0.01
                assert higher["snap"] <= lower["snap"] + 0.01
