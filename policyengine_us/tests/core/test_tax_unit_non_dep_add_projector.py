"""Core projectors must preserve the shape of tax-unit helper results.

Use one small simulation for mixed-entity sums, empty sums and the student
loan MAGI formula that calls the helper through a person.tax_unit projector.
"""

import numpy as np
import pytest

from policyengine_core.periods import period as make_period
from policyengine_us import Simulation
from policyengine_us.model_api import tax_unit_non_dep_add


@pytest.fixture(scope="module")
def simulation():
    year = 2025
    names = ["head", "spouse", "child", "single", "dependent"]
    sim = Simulation(
        situation={
            "people": {
                name: {
                    "age": {year: age},
                    "is_tax_unit_dependent": {year: dependent},
                }
                for name, age, dependent in zip(
                    names,
                    [50, 48, 10, 40, 8],
                    [False, False, True, False, True],
                )
            },
            "tax_units": {
                "joint": {"members": names[:3], "filing_status": {year: "JOINT"}},
                "single": {"members": names[3:], "filing_status": {year: "SINGLE"}},
            },
            "marital_units": {
                "couple": {"members": names[:2]},
                "child": {"members": [names[2]]},
                "single": {"members": [names[3]]},
                "dependent": {"members": [names[4]]},
            },
            "families": {
                "joint": {"members": names[:3]},
                "single": {"members": names[3:]},
            },
            "spm_units": {
                "joint": {"members": names[:3]},
                "single": {"members": names[3:]},
            },
            "households": {
                "joint": {"members": names[:3]},
                "single": {"members": names[3:]},
            },
        }
    )
    # Isolate the consumer formula from eligibility and deduction formulas.
    irs = sim.tax_benefit_system.parameters(f"{year}-01-01").gov.irs
    person_alds = irs.ald.student_loan_interest.magi.person_alds
    for name in (
        set(irs.gross_income.sources)
        | set(irs.ald.deductions)
        | {f"{ald}_person" for ald in person_alds}
    ):
        variable = sim.tax_benefit_system.variables[name]
        sim.set_input(name, year, np.zeros(sim.populations[variable.entity.key].count))
    sim.set_input("irs_employment_income", year, [1_000, 500, 0, 1_500, 0])
    sim.set_input("loss_ald", year, [10, 20])
    sim.set_input("traditional_ira_deduction", year, [1, 2, 900, 3, 800])
    sim.set_input("student_loan_interest_ald_eligible", year, [True] * len(names))
    sim.set_input("taxable_public_pension_income", year, [100, 20, 900, 200, 800])
    sim.set_input("tax_unit_social_security", year, [5, 10])
    return sim


def test_tax_unit_helper_preserves_projected_shapes_and_consumer_results(simulation):
    period = make_period(2025)
    tax_unit = simulation.populations["tax_unit"]
    projected_tax_unit = simulation.populations["person"].tax_unit
    assert tax_unit.count == 2
    assert simulation.populations["person"].count == 5
    variables = ["taxable_public_pension_income", "tax_unit_social_security"]

    for entity, expected, all_members in [
        (tax_unit, [125, 210], [1_025, 1_010]),
        (projected_tax_unit, [125, 125, 125, 210, 210], [1_025] * 3 + [1_010] * 2),
    ]:
        result = tax_unit_non_dep_add(entity, period, variables)
        np.testing.assert_array_equal(result, expected)
        np.testing.assert_array_equal(
            tax_unit_non_dep_add(
                entity,
                period,
                variables,
                include_dependents=["taxable_public_pension_income"],
            ),
            all_members,
        )
        empty = tax_unit_non_dep_add(entity, period, [])
        np.testing.assert_array_equal(empty, np.zeros(len(expected), dtype=np.float32))
        assert empty.dtype == np.float32

    np.testing.assert_array_equal(
        simulation.calculate("student_loan_interest_ald_magi", 2025),
        [993.5, 493.5, 0, 1_477, 0],
    )
