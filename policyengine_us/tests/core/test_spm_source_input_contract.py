"""A household fallback formula must not hide an observed population role."""

from policyengine_core.periods import ETERNITY
import pytest

from policyengine_us import Simulation
from policyengine_us.spm import DATASET_FORMULA_OWNED_INPUTS, DATASET_SOURCE_INPUTS
from policyengine_us.system import system


def test_source_contract_is_disjoint_and_matches_registered_role():
    assert DATASET_SOURCE_INPUTS == {"is_spm_independent_minor_role"}
    assert not DATASET_SOURCE_INPUTS & DATASET_FORMULA_OWNED_INPUTS
    variable = system.variables["is_spm_independent_minor_role"]
    assert variable.entity.key == "person"
    assert variable.value_type is bool
    assert variable.definition_period == ETERNITY
    assert variable.formulas  # Household fallback remains available.


@pytest.mark.parametrize("source_role,adults", [(None, 1), (False, 1), (True, 2)])
def test_observed_role_can_override_household_fallback(source_role, adults):
    head = {"age": {2024: 40}, "is_household_head": True}
    minor = {"age": {2024: 17}}
    if source_role is not None:
        head["is_spm_independent_minor_role"] = True
        minor["is_spm_independent_minor_role"] = source_role
    simulation = Simulation(
        situation={
            "people": {
                "head": head,
                "minor": minor,
            },
            "households": {"household": {"members": ["head", "minor"]}},
            "spm_units": {"unit": {"members": ["head", "minor"]}},
        }
    )
    assert simulation.calculate("spm_measurement_adults", 2024).tolist() == [adults]
    assert simulation.calculate("is_spm_independent_minor_role", ETERNITY).tolist() == [
        True,
        bool(source_role),
    ]
