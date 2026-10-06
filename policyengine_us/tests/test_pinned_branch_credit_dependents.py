"""Pinned-rule branches recompute credits that read the CTC.

New York (pre-TCJA CTC) and Alabama (2020 IRC) recompute the federal CTC on a
branch under pinned rules. The residential clean energy credit's limit
subtracts the non-refundable CTC (26 U.S.C. 25D(c)), so the branch must
recompute it rather than inherit the parent's value; otherwise the result
depends on which variables were calculated first.
"""

import pytest

from policyengine_us import Simulation

YEAR = 2021


def situation(state_code):
    members = ["head", "spouse", "child1", "child2"]
    return {
        "people": {
            "head": {
                "age": {YEAR: 40},
                "employment_income": {YEAR: 6_000},
                "taxable_interest_income": {YEAR: 40_000},
            },
            "spouse": {"age": {YEAR: 40}},
            "child1": {"age": {YEAR: 5}},
            "child2": {"age": {YEAR: 8}},
        },
        "tax_units": {
            "tax_unit": {
                "members": members,
                "solar_electric_property_expenditures": {YEAR: 10_000},
            }
        },
        "households": {
            "household": {"members": members, "state_code": {YEAR: state_code}}
        },
    }


@pytest.mark.parametrize(
    "state_code, variable",
    [("NY", "ny_ctc_pre_2024"), ("AL", "al_federal_income_tax_deduction")],
)
def test_pinned_branch_result_does_not_depend_on_calculation_order(
    state_code, variable
):
    results = []
    for first in (None, "residential_clean_energy_credit", "income_tax"):
        simulation = Simulation(situation=situation(state_code))
        if first is not None:
            simulation.calculate(first, YEAR)
        results.append(float(simulation.calculate(variable, YEAR)[0]))
    assert results[1] == pytest.approx(results[0])
    assert results[2] == pytest.approx(results[0])
