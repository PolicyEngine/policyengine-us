"""Construction/data contracts that the policy YAML runner cannot assert.

Policy outcomes live in is_tax_unit_spouse.yaml and
ssi_marital_earned_income.yaml. These tests use one six-person dataset and
one small household to check identifiers, year extension, caller isolation,
and clone provenance. Input-validation tests call the preprocessing helper
directly, without constructing simulations.
"""

from copy import deepcopy

import numpy as np
import pandas as pd
import pytest

from policyengine_us import Microsimulation, Simulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.tools.marital_units import infer_missing_marital_units


def _explicit_pair():
    return {
        "people": {
            "head": {"is_tax_unit_head": {"2024": True}},
            "spouse": {"is_tax_unit_spouse": {"2024": True}},
            "child": {"age": {"2024": 10}},
        },
        "tax_units": {"tax_unit": {"members": ["head", "spouse", "child"]}},
    }


def test_household_construction_does_not_mutate_input_and_expands_axes():
    situation = _explicit_pair()
    situation["axes"] = [
        [
            {
                "name": "employment_income",
                "period": "2024",
                "min": 0,
                "max": 10_000,
                "count": 2,
            }
        ]
    ]
    before = deepcopy(situation)
    sim = Simulation(situation=situation)
    assert situation == before
    assert sim.marital_unit.members_entity_id.tolist() == [0, 0, 1, 2, 2, 3]
    assert "marital_unit" not in sim.input_group_entities
    clone = sim.get_branch("copy")
    assert clone.input_group_entities == sim.input_group_entities
    np.testing.assert_array_equal(
        clone.marital_unit.members_entity_id, sim.marital_unit.members_entity_id
    )


def test_dataset_marital_ids_survive_loading_and_year_extension():
    memberships = np.array([0, 17, 42, 42, 99, 99])
    tax_memberships = np.array([10, 10, 20, 20, 30, 40])
    person = pd.DataFrame(
        {
            "person_id": [101, 102, 201, 202, 301, 302],
            "age": [45, 18, 60, 40, 65, 63],
            "person_marital_unit_id": memberships,
            "person_tax_unit_id": tax_memberships,
            "person_household_id": [1] * 6,
            "person_family_id": [1] * 6,
            "person_spm_unit_id": [1] * 6,
        }
    )
    dataset = USSingleYearDataset(
        time_period=2024,
        person=person,
        household=pd.DataFrame({"household_id": [1], "household_weight": [1.0]}),
        family=pd.DataFrame({"family_id": [1]}),
        spm_unit=pd.DataFrame({"spm_unit_id": [1]}),
        tax_unit=pd.DataFrame({"tax_unit_id": [10, 20, 30, 40]}),
        marital_unit=pd.DataFrame({"marital_unit_id": [0, 17, 42, 99]}),
    )
    original_person = person.copy(deep=True)
    sim = Microsimulation(dataset=dataset, dataset_end_year=2025)
    assert "marital_unit" in sim.input_group_entities
    np.testing.assert_array_equal(
        np.asarray(sim.marital_unit.ids)[sim.marital_unit.members_entity_id],
        memberships,
    )
    for year in (2024, 2025):
        np.testing.assert_array_equal(
            sim.calculate("person_marital_unit_id", year), memberships
        )
        np.testing.assert_array_equal(
            sim.calculate("is_tax_unit_spouse", year),
            [False, False, False, True, False, False],
        )
    pd.testing.assert_frame_equal(person, original_person)


@pytest.mark.parametrize(
    "marital_units",
    [
        {},
        {"reported": {"members": ["head", "child"]}},
    ],
)
def test_explicit_marital_mapping_is_left_untouched(marital_units):
    situation = _explicit_pair()
    situation["marital_units"] = marital_units
    original = deepcopy(situation)
    assert infer_missing_marital_units(situation) == original
    assert situation["marital_units"] is marital_units


def test_no_pairing_across_households_or_disjoint_role_periods():
    situation = _explicit_pair()
    situation["households"] = {
        "first": {"members": ["head", "child"]},
        "second": {"members": ["spouse"]},
    }
    inferred = infer_missing_marital_units(situation)
    assert all(len(unit["members"]) == 1 for unit in inferred["marital_units"].values())
    situation = _explicit_pair()
    situation["people"]["spouse"]["is_tax_unit_spouse"] = {"2025": True}
    inferred = infer_missing_marital_units(situation)
    assert all(len(unit["members"]) == 1 for unit in inferred["marital_units"].values())


@pytest.mark.parametrize(
    "extra_inputs",
    [
        {"is_tax_unit_spouse": {"2024": True, "2025": False}},
        {"is_tax_unit_head": {"2024": True}},
        {"is_tax_unit_dependent": {"2024": True}},
    ],
)
def test_ambiguous_or_changing_roles_require_explicit_membership(extra_inputs):
    situation = _explicit_pair()
    situation["people"]["spouse"].update(extra_inputs)
    with pytest.raises(ValueError, match="Supply marital_units explicitly"):
        infer_missing_marital_units(situation)


def test_separated_pair_and_partial_tax_units_stay_singletons():
    separated = _explicit_pair()
    separated["people"]["spouse"]["is_separated"] = {"2024": True}
    partial = _explicit_pair()
    partial["tax_units"]["tax_unit"]["members"] = ["head", "child"]
    for situation in (separated, partial):
        inferred = infer_missing_marital_units(situation)
        assert all(
            len(unit["members"]) == 1 for unit in inferred["marital_units"].values()
        )
