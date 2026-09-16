"""Above-the-line deductions must have stable float32 accumulation order."""

import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import numpy as np
import pytest


AGI_MODULE = (
    "policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income"
)
FORMULAS = {
    "adjusted_gross_income_person": f"{AGI_MODULE}.adjusted_gross_income_person",
    "student_loan_interest_ald_magi": (
        f"{AGI_MODULE}.above_the_line_deductions.student_loan_interest."
        "student_loan_interest_ald_magi"
    ),
}
PERSON_ALDS = [
    "self_employment_tax_ald",
    "self_employed_health_insurance_ald",
    "self_employed_pension_contribution_ald",
]


@pytest.mark.parametrize("variable_name", FORMULAS)
@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("empty", [False, True])
def test_tax_unit_deductions_are_ordered_unique_and_exclude_person_alds(
    monkeypatch, variable_name, reverse, empty
):
    module = importlib.import_module(FORMULAS[variable_name])
    deductions = (
        []
        if empty
        else [
            "loss_ald",
            "educator_expense",
            "alimony_expense_ald",
            "loss_ald",
            *PERSON_ALDS,
            "student_loan_interest_ald",
            "puerto_rico_income",
            "educator_expense",
        ]
    )
    if reverse:
        deductions.reverse()
    magi = SimpleNamespace(
        person_alds=PERSON_ALDS,
        excluded_alds=["student_loan_interest_ald", "puerto_rico_income"],
        excluded_gross_income_sources=[],
    )
    parameters = SimpleNamespace(
        gov=SimpleNamespace(
            irs=SimpleNamespace(
                gross_income=SimpleNamespace(sources=[]),
                ald=SimpleNamespace(
                    deductions=deductions,
                    student_loan_interest=SimpleNamespace(magi=magi),
                ),
            )
        )
    )

    class Person:
        tax_unit = object()

        def __call__(self, name, period):
            if name == "is_tax_unit_dependent":
                return np.array([False])
            assert name == "irs_gross_income"
            return np.array([0], dtype=np.float32)

    class ReachedTaxUnitSum(Exception):
        pass

    captured = []
    person = Person()

    def capture_add(entity, period, variables):
        if entity is person.tax_unit:
            captured.extend(variables)
            raise ReachedTaxUnitSum
        assert variables == [f"{name}_person" for name in PERSON_ALDS]
        return np.array([0], dtype=np.float32)

    monkeypatch.setattr(module, "add", capture_add)
    with pytest.raises(ReachedTaxUnitSum):
        getattr(module, variable_name).formula(person, 2026, lambda period: parameters)

    if empty:
        expected = []
    elif variable_name == "student_loan_interest_ald_magi":
        expected = ["alimony_expense_ald", "educator_expense", "loss_ald"]
    else:
        expected = [
            "alimony_expense_ald",
            "educator_expense",
            "loss_ald",
            "puerto_rico_income",
            "student_loan_interest_ald",
        ]
    assert captured == expected


def _household_results():
    """Run real formulas at a float32 rounding boundary, with no dataset."""
    from policyengine_us import Simulation

    simulation = Simulation(
        situation={
            "people": {"person": {"age": {2026: 40}}},
            "households": {
                "household": {
                    "members": ["person"],
                    "state_code": {2026: "MT"},
                    "county_fips": {2026: "30031"},
                }
            },
        }
    )
    irs = simulation.tax_benefit_system.parameters("2026-01-01").gov.irs
    # Explicit inputs isolate summation from deduction eligibility and phaseouts.
    for name in irs.gross_income.sources:
        simulation.set_input(name, 2026, [0])
    for name in irs.ald.deductions:
        simulation.set_input(name, 2026, [0])
    for name in PERSON_ALDS:
        simulation.set_input(f"{name}_person", 2026, [0])
    inputs = {
        "irs_employment_income": 2**25,
        "irs_gross_income": 2**25,
        "loss_ald": 2**24,
        "alimony_expense_ald": 1,
        "health_savings_account_ald": 1,
        "student_loan_interest_ald_eligible": True,
        "is_tax_unit_dependent": False,
        "is_tax_unit_head": True,
        "is_tax_unit_spouse": False,
        "filing_status": "SINGLE",
    }
    for name, value in inputs.items():
        simulation.set_input(name, 2026, [value])
    results = {}
    for name in FORMULAS:
        values = simulation.calculate(name, 2026)
        results[name] = {
            "values": values.tolist(),
            "dtype": str(values.dtype),
            "bytes": values.tobytes().hex(),
        }
    return results


def test_household_float32_deductions_are_identical_across_hash_seeds():
    results = {}
    for seed in (0, 20, 32, 34, 42, 123):
        completed = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--household-probe"],
            env={**os.environ, "PYTHONHASHSEED": str(seed)},
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )
        results[seed] = json.loads(completed.stdout)
    assert all(result == results[0] for result in results.values()), json.dumps(results)
    # Both $1 deductions precede the large deduction in the canonical order;
    # their sum and the resulting income are exactly representable in float32.
    for result in results[0].values():
        assert result["dtype"] == "float32"
        assert result["values"] == [16_777_214.0]


if __name__ == "__main__" and sys.argv[1:] == ["--household-probe"]:
    print(json.dumps(_household_results()))
