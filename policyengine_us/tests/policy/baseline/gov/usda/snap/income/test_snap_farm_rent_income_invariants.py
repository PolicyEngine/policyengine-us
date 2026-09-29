"""Invariants of SNAP's treatment of farm rental income.

snap_farm_rent_income counts farm_rent_income as unearned income under
7 CFR 273.9(b)(2)(ii) and floors a loss at zero, because 7 U.S.C. 2014(d)(9)
and 7 CFR 273.11(a)(2)(ii) let only self-employed farmers' losses offset other
household income.

Over an exhaustive grid of annual farm rent F, rent R >= 0, wages and other
unearned income, the tests check:

1. snap_farm_rent_income == max(F, 0) / 12, so it is never negative.
2. For F >= 0, farm rent and rent are interchangeable: swapping F and R
   leaves snap_gross_income, snap_net_income and snap unchanged. This is a
   differential check of the two paths into SNAP unearned income.
3. Farm rent losses are inert: whenever F <= 0, SNAP unearned, gross and net
   income and the benefit equal those of the same household with F = 0.
4. Counted farm rent reaches gross income exactly once:
   snap_gross_income(F) - snap_gross_income(0) == snap_farm_rent_income.
5. Monotonicity: holding everything else fixed, more farm rent never lowers
   SNAP gross income and never raises the SNAP benefit.

These are properties of SNAP's own computation. Another program whose output
SNAP counts as income can break 2, 3 and 5 when it reads these inputs: SSI
counts rental_income but not farm_rent_income, and a TANF benefit that ends at
an income threshold can lower SNAP income as farm rent rises. The grid
therefore uses a one-person Texas household aged 31, who receives neither
SSI nor TANF.
"""

from itertools import product

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2026
MONTH = f"{YEAR}-01"

# Annual amounts. Multiples of 12 keep monthly values exact in float32.
FARM_RENT_VALUES = (-60_000, -1_920, -12, 0, 12, 1_920, 12_000, 240_000)
RENT_VALUES = (0, 1_920, 12_000)
WAGE_VALUES = (0, 5_923)
FINANCIAL_ASSISTANCE_VALUES = (0, 13_000)

GRID = list(
    product(
        FARM_RENT_VALUES,
        RENT_VALUES,
        WAGE_VALUES,
        FINANCIAL_ASSISTANCE_VALUES,
    )
)
# Swapped cases for the interchangeability check, which are not all in GRID.
SWAPPED = [
    (rent, farm_rent, wages, assistance)
    for farm_rent, rent, wages, assistance in GRID
    if farm_rent >= 0
]

OUTPUTS = (
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
    for i, (farm_rent, rent, wages, assistance) in enumerate(cases):
        person = f"p{i}"
        people[person] = {
            "age": {YEAR: 31},
            # Clears the SNAP work requirement for an adult without
            # dependents, so the member's income counts in full.
            "weekly_hours_worked_before_lsr": {YEAR: 40},
            "farm_rent_income": {YEAR: farm_rent},
            "rental_income": {YEAR: rent},
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
    return _simulate(list(dict.fromkeys(GRID + SWAPPED)))


def test_farm_rent_is_floored_and_never_negative(grid_results):
    for (farm_rent, _, _, _), result in grid_results.items():
        expected = max(farm_rent, 0) / 12
        assert result["snap_farm_rent_income"] == pytest.approx(expected, abs=0.01)
        assert result["snap_farm_rent_income"] >= 0


def test_farm_rent_and_rent_are_interchangeable(grid_results):
    for farm_rent, rent, wages, assistance in GRID:
        if farm_rent < 0:
            continue
        result = grid_results[(farm_rent, rent, wages, assistance)]
        swapped = grid_results[(rent, farm_rent, wages, assistance)]
        for variable in ("snap_gross_income", "snap_net_income", "snap"):
            assert result[variable] == pytest.approx(swapped[variable], abs=0.01)


def test_farm_rent_losses_do_not_change_snap(grid_results):
    for farm_rent, rent, wages, assistance in GRID:
        if farm_rent > 0:
            continue
        result = grid_results[(farm_rent, rent, wages, assistance)]
        no_farm_rent = grid_results[(0, rent, wages, assistance)]
        for variable in (
            "snap_unearned_income",
            "snap_gross_income",
            "snap_net_income",
            "snap",
        ):
            assert result[variable] == pytest.approx(no_farm_rent[variable], abs=0.01)


def test_counted_farm_rent_reaches_gross_income_once(grid_results):
    for farm_rent, rent, wages, assistance in GRID:
        result = grid_results[(farm_rent, rent, wages, assistance)]
        no_farm_rent = grid_results[(0, rent, wages, assistance)]
        assert result["snap_gross_income"] - no_farm_rent[
            "snap_gross_income"
        ] == pytest.approx(result["snap_farm_rent_income"], abs=0.02)


def test_more_farm_rent_never_lowers_gross_income_or_raises_benefit(
    grid_results,
):
    ascending = sorted(FARM_RENT_VALUES)
    for rent, wages, assistance in product(
        RENT_VALUES, WAGE_VALUES, FINANCIAL_ASSISTANCE_VALUES
    ):
        results = [
            grid_results[(farm_rent, rent, wages, assistance)]
            for farm_rent in ascending
        ]
        for lower, higher in zip(results, results[1:]):
            assert higher["snap_gross_income"] >= lower["snap_gross_income"] - 0.01
            assert higher["snap"] <= lower["snap"] + 0.01
