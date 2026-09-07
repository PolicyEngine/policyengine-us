"""Regression test for the `md_ccs_service_unit` select default.

Follow-up to PolicyEngine/policyengine-us#9400, which fixed the same bug
class in `ccdf_age_group`: a `select(conditions, [Enum items])` with no
`default` fills unmatched rows with numpy's integer 0, and
policyengine-core's `Enum.encode` rejects an object array that mixes
Enum members with that 0 (`AttributeError: 'int' object has no attribute
'index'` when an Enum member comes first, `ValueError: Invalid value(s)
['0', ...]` otherwise).

`md_ccs_service_unit` hit the unmatched case for negative or NaN
`childcare_hours_per_day`, which its `unit_hours` bracket maps to 0 units.
The full simulation happened not to crash because the variable's
`defined_for` path in core turns a bare integer into an Enum index before
encoding, and index 0 is UNIT_1. That is a coincidence of member order,
not a rule, so these tests encode the raw formula output directly, which
is the path a variable without `defined_for` takes.

The Enum class is taken from the loaded variable rather than imported by
package path: the tax-benefit system loads variable modules by file, so
the package-path import is a distinct class object and `isinstance`
against it is always False.
"""

import numpy as np
from policyengine_core.periods import period as make_period

from policyengine_us import Simulation

PERIOD = "2025-01"


def _simulation(hours_by_person: dict) -> Simulation:
    people = {
        name: {"age": {2025: 4}, "childcare_hours_per_day": {2025: hours}}
        for name, hours in hours_by_person.items()
    }
    return Simulation(
        situation={
            "people": people,
            "households": {
                "household": {
                    "members": list(people),
                    "state_code": {2025: "MD"},
                }
            },
        }
    )


def _raw_formula_output(sim: Simulation) -> np.ndarray:
    variable = sim.tax_benefit_system.variables["md_ccs_service_unit"]
    period = make_period(PERIOD)
    formula = variable.get_formula(period)
    return formula(sim.persons, period, sim.tax_benefit_system.parameters)


def _encode(sim: Simulation, raw: np.ndarray) -> list:
    enum_class = sim.tax_benefit_system.variables["md_ccs_service_unit"].possible_values
    assert all(isinstance(item, enum_class) for item in raw), raw
    return list(enum_class.encode(raw).decode_to_str())


def test_negative_hours_encode_as_unit_1_regardless_of_row_order():
    # Enum member first, then the unmatched row (the AttributeError shape).
    sim = _simulation({"zero": 0.0, "negative": -1.0})
    assert _encode(sim, _raw_formula_output(sim)) == ["UNIT_1", "UNIT_1"]

    # Unmatched row first (the ValueError shape).
    sim = _simulation({"negative": -1.0, "full_time": 8.0})
    assert _encode(sim, _raw_formula_output(sim)) == ["UNIT_1", "UNIT_3"]


def test_nan_hours_encode_as_unit_1():
    # Core rejects NaN as a direct input, so drive the formula with a NaN
    # array to cover the other value the bracket maps to 0 units.
    sim = _simulation({"child": 0.0})
    holder = sim.persons.get_holder("childcare_hours_per_day")
    holder.put_in_cache(np.array([np.nan]), make_period(2025), sim.branch_name)
    assert _encode(sim, _raw_formula_output(sim)) == ["UNIT_1"]


def test_full_simulation_matches_zero_hours_treatment():
    sim = _simulation({"negative": -1.0, "zero": 0.0, "full_time": 8.0})
    units = sim.calculate("md_ccs_service_unit", PERIOD).decode_to_str()
    assert list(units) == ["UNIT_1", "UNIT_1", "UNIT_3"]
