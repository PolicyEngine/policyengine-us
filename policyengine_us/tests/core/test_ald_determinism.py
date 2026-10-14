"""Above-the-line deductions must have stable float32 accumulation order."""

import importlib
import importlib.machinery
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace

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


ROUNDING_PERIOD = 2026
ROUNDING_INPUTS = {
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
PROBE_FORMULAS = {
    "above_the_line_deductions": (
        f"{AGI_MODULE}.above_the_line_deductions.above_the_line_deductions"
    ),
    "above_the_line_deductions_person": (
        f"{AGI_MODULE}.above_the_line_deductions.above_the_line_deductions_person"
    ),
    "loss_ald_person": f"{AGI_MODULE}.above_the_line_deductions.loss_ald_person",
    **FORMULAS,
}


def _deductions(reverse, empty):
    deductions = (
        []
        if empty
        else [
            "loss_ald",
            "educator_expense_ald",
            "alimony_expense_ald",
            "loss_ald",
            *PERSON_ALDS,
            "student_loan_interest_ald",
            "puerto_rico_income",
            "educator_expense_ald",
        ]
    )
    if reverse:
        deductions.reverse()
    return deductions


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("empty", [False, True])
def test_tax_unit_deductions_are_ordered_unique_and_exclude_person_alds(
    monkeypatch, reverse, empty
):
    variable_name = "student_loan_interest_ald_magi"
    module = importlib.import_module(FORMULAS[variable_name])
    deductions = _deductions(reverse, empty)
    magi = SimpleNamespace(
        person_alds=PERSON_ALDS,
        excluded_alds=["student_loan_interest_ald", "puerto_rico_income"],
    )
    parameters = SimpleNamespace(
        gov=SimpleNamespace(
            irs=SimpleNamespace(
                gross_income=SimpleNamespace(sources=[]),
                ald=SimpleNamespace(
                    deductions=deductions,
                    filer_amounts_recorded_on_dependents=[],
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
        # Tax-unit deductions must be summed over non-dependents only, through
        # tax_unit_non_dep_add, never with a plain add over every member.
        assert entity is person
        assert variables == [f"{name}_person" for name in PERSON_ALDS]
        return np.array([0], dtype=np.float32)

    def capture_tax_unit_add(entity, period, variables, include_dependents=()):
        assert entity is person.tax_unit
        captured.extend(variables)
        raise ReachedTaxUnitSum

    monkeypatch.setattr(module, "add", capture_add)
    monkeypatch.setattr(module, "tax_unit_non_dep_add", capture_tax_unit_add)
    with pytest.raises(ReachedTaxUnitSum):
        getattr(module, variable_name).formula(person, 2026, lambda period: parameters)

    expected = (
        [] if empty else ["alimony_expense_ald", "educator_expense_ald", "loss_ald"]
    )
    assert captured == expected


PERSON_LEVEL = {"student_loan_interest_ald"}
WITH_PERSON_AMOUNTS = {
    "loss_ald",
    "alimony_expense_ald",
    "educator_expense_ald",
    *PERSON_ALDS,
}


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("empty", [False, True])
def test_person_deductions_are_summed_in_sorted_unique_order(reverse, empty):
    module = importlib.import_module(
        f"{AGI_MODULE}.above_the_line_deductions.above_the_line_deductions_person"
    )
    deductions = _deductions(reverse, empty)
    parameters = SimpleNamespace(
        gov=SimpleNamespace(
            irs=SimpleNamespace(
                ald=SimpleNamespace(
                    deductions=deductions,
                    filer_amounts_recorded_on_dependents=[],
                )
            )
        )
    )
    order = []

    class Variable:
        def __init__(self, is_person):
            self.entity = SimpleNamespace(is_person=is_person)

    class Entity:
        def get_variable(self, name, check_existence=False):
            if name.endswith("_person"):
                if name[: -len("_person")] in WITH_PERSON_AMOUNTS:
                    return Variable(True)
                return None
            order.append(name)
            return Variable(name in PERSON_LEVEL)

    class TaxUnit:
        def __call__(self, name, period):
            return np.array([0], dtype=np.float32)

        def sum(self, values):
            return np.asarray(values, dtype=np.float32)

    class Person:
        entity = Entity()
        tax_unit = TaxUnit()

        def __call__(self, name, period):
            if name == "is_tax_unit_dependent":
                return np.array([False])
            return np.array([0], dtype=np.float32)

    module.above_the_line_deductions_person.formula(
        Person(), 2026, lambda period: parameters
    )
    expected = [] if empty else sorted(set(deductions))
    assert order == expected


def _set_rounding_inputs(simulation, irs):
    # Share the explicit boundary inputs between the full and small systems.
    for name in irs.gross_income.sources:
        simulation.set_input(name, ROUNDING_PERIOD, [0])
    for name in irs.ald.deductions:
        simulation.set_input(name, ROUNDING_PERIOD, [0])
    for name in PERSON_ALDS:
        simulation.set_input(f"{name}_person", ROUNDING_PERIOD, [0])
    for name, value in ROUNDING_INPUTS.items():
        simulation.set_input(name, ROUNDING_PERIOD, [value])


def _serialized_results(simulation):
    results = {}
    for name in FORMULAS:
        values = simulation.calculate(name, ROUNDING_PERIOD)
        results[name] = {
            "values": values.tolist(),
            "dtype": str(values.dtype),
            "bytes": values.tobytes().hex(),
        }
    return results


def _probe_fixture(simulation):
    """Capture the real parameter lists and explicit dependency inputs."""
    from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.loss_ald_person import (
        BUSINESS_INCOME_SOURCES,
    )

    system = simulation.tax_benefit_system
    parameters = system.parameters(f"{ROUNDING_PERIOD}-01-01")
    irs = parameters.gov.irs
    magi = irs.ald.student_loan_interest.magi
    lists = {
        "deductions": list(irs.ald.deductions),
        "gross_income_sources": list(irs.gross_income.sources),
        "filer_amounts_recorded_on_dependents": list(
            irs.ald.filer_amounts_recorded_on_dependents
        ),
        "person_alds": list(magi.person_alds),
        "excluded_alds": list(magi.excluded_alds),
    }
    names = set(lists["deductions"]) | set(lists["gross_income_sources"])
    for deduction in lists["deductions"]:
        candidate = f"{deduction}_person"
        if candidate in system.variables:
            names.add(candidate)
    names.update(f"{name}_person" for name in lists["person_alds"])
    names.update(BUSINESS_INCOME_SOURCES)
    names.update(ROUNDING_INPUTS)
    names.update(
        (
            "section_911_excluded_income",
            "other_net_gain",
            "limited_business_loss",
            "capital_losses",
            # MAGI reads all unemployment compensation, even when only its
            # taxable portion is in the gross-income parameter list.
            "unemployment_compensation",
            "total_unemployment_compensation",
            "basic_income",
        )
    )
    # These classes remain real production formulas in every child.
    names.difference_update(PROBE_FORMULAS)
    variables = {}
    for name in sorted(names):
        variable = system.variables[name]
        values = simulation.calculate(name, ROUNDING_PERIOD)
        if name == "filing_status":
            value_type = "filing_status"
            default_value = variable.default_value.name
            input_values = values.decode_to_str().tolist()
        elif variable.value_type in (float, bool, int):
            value_type = variable.value_type.__name__
            default_value = variable.value_type(variable.default_value)
            input_values = values.tolist()
        else:
            raise TypeError(f"Unsupported probe input {name}: {variable.value_type}")
        variables[name] = {
            "entity": variable.entity.key,
            "value_type": value_type,
            "default_value": default_value,
            "definition_period": variable.definition_period,
            "input_values": input_values,
        }
    return {
        "parameters": lists,
        "basic_income_taxable": bool(
            parameters.gov.contrib.ubi_center.basic_income.taxable
        ),
        "variables": variables,
    }


def _household_results(fixture_path=None):
    """Run real formulas at a float32 rounding boundary, with no dataset."""
    from policyengine_us import Simulation

    simulation = Simulation(
        situation={
            "people": {"person": {"age": {ROUNDING_PERIOD: 40}}},
            "households": {
                "household": {
                    "members": ["person"],
                    "state_code": {ROUNDING_PERIOD: "MT"},
                    "county_fips": {ROUNDING_PERIOD: "30031"},
                }
            },
        }
    )
    irs = simulation.tax_benefit_system.parameters(f"{ROUNDING_PERIOD}-01-01").gov.irs
    # Explicit inputs isolate summation from deduction eligibility and phaseouts.
    _set_rounding_inputs(simulation, irs)
    results = _serialized_results(simulation)
    if fixture_path is not None:
        fixture_path.write_text(json.dumps(_probe_fixture(simulation)))
    return results


def _install_probe_package():
    """Avoid country startup only in a fresh hash-seed child process."""
    if "policyengine_us" in sys.modules:
        raise RuntimeError("The hash-seed probe must precede country imports")
    package_dir = Path(__file__).resolve().parents[2]
    package = ModuleType("policyengine_us")
    package.__path__ = [str(package_dir)]
    package.__package__ = "policyengine_us"
    package.__file__ = str(package_dir / "__init__.py")
    package.__spec__ = importlib.machinery.ModuleSpec(
        "policyengine_us", loader=None, is_package=True
    )
    package.__spec__.submodule_search_locations = package.__path__
    sys.modules["policyengine_us"] = package


def _hash_seed_results(fixture_path):
    """Run production formulas and actual core float32 holders under a seed."""
    _install_probe_package()
    from policyengine_core.model_api import Enum, Variable
    from policyengine_core.parameters import ParameterNode
    from policyengine_core.simulations import Simulation as CoreSimulation
    from policyengine_core.taxbenefitsystems import TaxBenefitSystem
    from policyengine_us.entities import entities
    from policyengine_us.variables.household.demographic.tax_unit.filing_status import (
        FilingStatus,
    )

    fixture = json.loads(fixture_path.read_text())
    system = TaxBenefitSystem(entities)
    entity_by_key = {entity.key: entity for entity in system.entities}
    for name, attributes in fixture["variables"].items():
        assert name not in PROBE_FORMULAS
        if attributes["value_type"] == "filing_status":
            value_type = Enum
            default_value = FilingStatus[attributes["default_value"]]
            extra = {"possible_values": FilingStatus}
        else:
            value_type = {"float": float, "bool": bool, "int": int}[
                attributes["value_type"]
            ]
            default_value = attributes["default_value"]
            extra = {}
        system.add_variable(
            type(
                name,
                (Variable,),
                {
                    "entity": entity_by_key[attributes["entity"]],
                    "value_type": value_type,
                    "default_value": default_value,
                    "definition_period": attributes["definition_period"],
                    "label": f"Explicit rounding-boundary fixture input: {name}",
                    **extra,
                },
            )
        )
    for name, module_path in PROBE_FORMULAS.items():
        system.add_variable(getattr(importlib.import_module(module_path), name))

    p = fixture["parameters"]

    def leaf(value):
        return {"values": {f"{ROUNDING_PERIOD}-01-01": value}}

    system.parameters = ParameterNode(
        "",
        data={
            "gov": {
                "irs": {
                    "gross_income": {"sources": leaf(p["gross_income_sources"])},
                    "ald": {
                        "deductions": leaf(p["deductions"]),
                        "filer_amounts_recorded_on_dependents": leaf(
                            p["filer_amounts_recorded_on_dependents"]
                        ),
                        "student_loan_interest": {
                            "magi": {
                                "person_alds": leaf(p["person_alds"]),
                                "excluded_alds": leaf(p["excluded_alds"]),
                            }
                        },
                    },
                },
                "contrib": {
                    "ubi_center": {
                        "basic_income": {
                            "taxable": leaf(fixture["basic_income_taxable"])
                        }
                    }
                },
            }
        },
    )
    simulation = CoreSimulation(
        tax_benefit_system=system,
        situation={
            "people": {"person": {}},
            "tax_units": {"unit": {"members": ["person"]}},
        },
        default_input_period=ROUNDING_PERIOD,
        default_calculation_period=ROUNDING_PERIOD,
    )
    for name, attributes in fixture["variables"].items():
        simulation.set_input(name, ROUNDING_PERIOD, attributes["input_values"])
    _set_rounding_inputs(
        simulation, system.parameters(f"{ROUNDING_PERIOD}-01-01").gov.irs
    )
    results = _serialized_results(simulation)
    if "policyengine_us.system" in sys.modules:
        raise RuntimeError("The hash-seed probe imported the full country system")
    return results


def test_household_float32_deductions_are_identical_across_hash_seeds(tmp_path):
    fixture_path = tmp_path / "rounding-boundary.json"
    # Keep one complete US integration as the oracle. Only the child processes
    # replace unrelated formula dependencies with its captured boundary inputs.
    reference = _household_results(fixture_path=fixture_path)
    results = {}
    for seed in (0, 20, 32, 34, 42, 123):
        completed = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--hash-seed-probe",
                str(fixture_path),
            ],
            env={**os.environ, "PYTHONHASHSEED": str(seed)},
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )
        results[seed] = json.loads(completed.stdout)
    assert all(result == results[0] for result in results.values()), json.dumps(results)
    assert results[0] == reference, json.dumps(
        {"full_household": reference, "hash_seeds": results}
    )
    # The boundary combines 2**25 of income with 2**24 and two $1 deductions.
    # Keep its expected float32 result alongside the exact byte comparisons.
    for result in reference.values():
        assert result["dtype"] == "float32"
        assert result["values"] == [16_777_214.0]


if __name__ == "__main__":
    if sys.argv[1:] == ["--household-probe"]:
        print(json.dumps(_household_results()))
    elif len(sys.argv) == 3 and sys.argv[1] == "--hash-seed-probe":
        print(json.dumps(_hash_seed_results(Path(sys.argv[2]))))
