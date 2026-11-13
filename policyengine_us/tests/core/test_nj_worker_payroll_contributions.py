"""Vectorized and reform invariants for NJ employee UI/workforce contributions.

YAML covers the individual policy examples. This test checks the simulation's
mixed-state masking, per-person caps within a shared tax unit, and the change
in aggregated employee payroll tax under a two-rate parameter reform.
"""

import numpy as np

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM

PERIOD = "2026"
# NJDOL's 2026 worker contribution table, independent of the model parameters.
WAGE_BASE = 44_800
UI_RATE = 0.003825
WORKFORCE_RATE = 0.000425
TOLERANCE = 0.01

NJ_WAGES = [-500, 0, 1, WAGE_BASE - 1, WAGE_BASE, WAGE_BASE + 1, 2 * WAGE_BASE]


def make_situation():
    workers = [
        {"wages": wages, "state": "NJ", "unit": f"nj_{i}"}
        for i, wages in enumerate(NJ_WAGES)
    ] + [
        {"wages": WAGE_BASE - 1, "state": "NY", "unit": "ny"},
        {"wages": 2 * WAGE_BASE, "state": "PA", "unit": "pa"},
        {"wages": 2 * WAGE_BASE, "state": "NJ", "unit": "couple"},
        {"wages": 2 * WAGE_BASE, "state": "NJ", "unit": "couple"},
        {"wages": 30_000, "state": "NJ", "unit": "without_premiums"},
        {
            "wages": 30_000,
            "state": "NJ",
            "unit": "with_premiums",
            "premiums": 5_000,
        },
    ]
    situation = {
        entity: {}
        for entity in (
            "people",
            "households",
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
        )
    }
    unit_indices = []
    for i, worker in enumerate(workers):
        person = f"person_{i}"
        unit = worker["unit"]
        new_unit = unit not in situation["tax_units"]
        situation["people"][person] = {
            "age": {PERIOD: 40},
            "employment_income": {PERIOD: worker["wages"]},
            "pre_tax_health_insurance_premiums": {PERIOD: worker.get("premiums", 0)},
            "is_tax_unit_head": {PERIOD: new_unit},
            "is_tax_unit_spouse": {PERIOD: not new_unit},
        }
        for entity in situation:
            if entity == "people":
                continue
            if new_unit:
                situation[entity][unit] = {"members": []}
            situation[entity][unit]["members"].append(person)
        situation["households"][unit]["state_code"] = {PERIOD: worker["state"]}
        unit_indices.append(list(situation["tax_units"]).index(unit))
    return situation, workers, np.asarray(unit_indices)


def test_nj_worker_contributions_caps_state_masking_and_payroll_reform():
    situation, workers, unit_indices = make_situation()
    baseline = Simulation(tax_benefit_system=SYSTEM, situation=situation)
    without_contributions = Simulation(
        tax_benefit_system=SYSTEM,
        situation=situation,
        reform={
            "gov.states.nj.tax.payroll.unemployment.employee_rate": {PERIOD: 0},
            "gov.states.nj.tax.payroll.workforce_development.employee_rate": {
                PERIOD: 0
            },
        },
    )
    wages = np.array([worker["wages"] for worker in workers])
    in_nj = np.array([worker["state"] == "NJ" for worker in workers])
    expected_base = np.where(in_nj, np.clip(wages, 0, WAGE_BASE), 0)
    expected_ui = expected_base * UI_RATE
    expected_workforce = expected_base * WORKFORCE_RATE
    expected_total = expected_ui + expected_workforce

    def calculate(simulation, variable):
        return np.asarray(simulation.calculate(variable, PERIOD))

    covered_wages = calculate(baseline, "nj_employee_unemployment_taxable_wages")
    ui = calculate(baseline, "nj_employee_unemployment_insurance_contribution")
    workforce = calculate(baseline, "nj_employee_workforce_fund_contribution")
    for actual, expected in (
        (covered_wages, expected_base),
        (ui, expected_ui),
        (workforce, expected_workforce),
    ):
        np.testing.assert_allclose(actual, expected, atol=TOLERANCE, rtol=0)

    # Raising one worker's wages cannot lower either contribution, and wages
    # above that worker's cap cannot increase the contribution.
    for values in (covered_wages, ui, workforce):
        assert (np.diff(values[: len(NJ_WAGES)]) >= 0).all()
        np.testing.assert_allclose(values[4:7], values[4], atol=TOLERANCE, rtol=0)

    # Both members of one tax unit retain their own wage cap.
    np.testing.assert_allclose(covered_wages[9:11], WAGE_BASE, atol=TOLERANCE, rtol=0)
    assert unit_indices[9] == unit_indices[10]

    # A federal FICA exclusion must not reduce NJ's covered employee wages.
    federal_wages = calculate(baseline, "payroll_tax_gross_wages")
    np.testing.assert_allclose(
        federal_wages[-2:], [30_000, 25_000], atol=TOLERANCE, rtol=0
    )
    for values in (covered_wages, ui, workforce):
        np.testing.assert_allclose(values[-2], values[-1], atol=TOLERANCE, rtol=0)

    # A true rate reform isolates the new contributions from TDI/FLI and
    # federal payroll taxes without replacing those variables with inputs.
    for variable in (
        "nj_employee_unemployment_insurance_contribution",
        "nj_employee_workforce_fund_contribution",
    ):
        np.testing.assert_allclose(
            calculate(without_contributions, variable), 0, atol=TOLERANCE, rtol=0
        )
    np.testing.assert_allclose(
        calculate(baseline, "nj_employee_state_payroll_tax")
        - calculate(without_contributions, "nj_employee_state_payroll_tax"),
        expected_total,
        atol=TOLERANCE,
        rtol=0,
    )
    expected_tax_unit_total = np.bincount(unit_indices, weights=expected_total)
    for variable in ("employee_state_payroll_tax", "employee_payroll_tax"):
        np.testing.assert_allclose(
            calculate(baseline, variable) - calculate(without_contributions, variable),
            expected_tax_unit_total,
            atol=TOLERANCE,
            rtol=0,
        )
