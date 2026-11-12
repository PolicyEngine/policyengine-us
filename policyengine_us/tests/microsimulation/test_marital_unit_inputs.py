"""Construction/data contracts that the policy YAML runner cannot assert.

Policy outcomes live in is_tax_unit_spouse.yaml and ssi_claim_is_joint.yaml.
These tests use one six-person dataset and small households to check
identifiers, year extension, caller isolation, clones and source-snapshot
round trips. The pairing tests call the preprocessing helper directly, with
the shared country system for the age-order fallback, without constructing
simulations.
"""

from copy import deepcopy

import numpy as np
import pandas as pd
import pytest

from policyengine_us import Microsimulation, Simulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.system import system
from policyengine_us.tools.marital_units import infer_missing_marital_units
from policyengine_us.tools.social_security_inputs import (
    export_source_inputs,
    reload_source_inputs,
)


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
    clone = sim.get_branch("copy")
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


def test_source_snapshot_round_trip_keeps_the_inferred_tax_spouse():
    # The snapshot writes the inferred marital units out as members, and the
    # reloaded simulation reads them as supplied; they agree with the tax
    # roles, so the second adult stays the tax spouse.
    sim = Simulation(situation={"people": {"first": {}, "second": {}}})
    reloaded = reload_source_inputs(export_source_inputs(sim))
    np.testing.assert_array_equal(
        reloaded.marital_unit.members_entity_id, sim.marital_unit.members_entity_id
    )
    assert sim.calculate("is_tax_unit_spouse", 2024).tolist() == [False, True]
    np.testing.assert_array_equal(
        reloaded.calculate("is_tax_unit_spouse", 2024),
        sim.calculate("is_tax_unit_spouse", 2024),
    )


def _married_family(**people):
    people = {
        "first": {"age": {"2024": 40}},
        "second": {"age": {"2024": 38}},
        "child": {"age": {"2024": 10}},
        **people,
    }
    return {
        "people": people,
        "tax_units": {"tax_unit": {"members": list(people)}},
        "families": {"family": {"members": list(people), "is_married": {"2024": True}}},
    }


def _pairs(situation):
    units = infer_missing_marital_units(situation)["marital_units"].values()
    return sorted(sorted(unit["members"]) for unit in units if len(unit["members"]) > 1)


def test_a_married_family_pairs_its_two_adults_but_not_its_children():
    assert _pairs(_married_family()) == [["first", "second"]]


@pytest.mark.parametrize(
    "people",
    [
        # A third adult leaves the married couple ambiguous.
        {"adult_child": {"age": {"2024": 21}}},
        {"second": {"age": {"2024": 38}, "is_separated": {"2024": True}}},
        {"second": {"age": {"2024": 38}, "is_tax_unit_dependent": {"2024": True}}},
    ],
)
def test_a_married_family_stays_unpaired_when_ambiguous(people):
    assert _pairs(_married_family(**people)) == []


@pytest.mark.parametrize(
    "head, spouse",
    [
        ({"2024": np.True_}, {"2024": 1}),
        # Overlapping year and month inputs both apply to 2024.
        ({"2024": True}, {"2024-01": True}),
    ],
)
def test_true_role_inputs_pair_in_any_form_and_overlapping_period(head, spouse):
    situation = _explicit_pair()
    situation["people"]["head"]["is_tax_unit_head"] = head
    situation["people"]["spouse"]["is_tax_unit_spouse"] = spouse
    assert _pairs(situation) == [["head", "spouse"]]


def test_malformed_input_is_left_to_core_validation():
    bad_period = _explicit_pair()
    bad_period["people"]["head"]["is_tax_unit_head"] = {"not a period": True}
    listed_twice = _explicit_pair()
    listed_twice["tax_units"]["other"] = {"members": ["child"]}
    for situation in (bad_period, listed_twice):
        assert "marital_units" not in infer_missing_marital_units(situation)


def _fallback_pairs(people, **groups):
    situation = {
        "people": people,
        "tax_units": {"tax_unit": {"members": list(people)}},
        **groups,
    }
    units = infer_missing_marital_units(situation, "2024", system)["marital_units"]
    return sorted(
        sorted(unit["members"]) for unit in units.values() if len(unit["members"]) > 1
    )


@pytest.mark.parametrize(
    "people, pairs",
    [
        # The oldest adult and the next-oldest who fails the age test.
        (
            {"older": {"age": 45}, "younger": {"age": 20}, "child": {"age": 10}},
            [["older", "younger"]],
        ),
        # The qualifying child age test keeps an adult child out: under 19,
        ({"parent": {"age": 45}, "child": {"age": 18}}, []),
        # under 24 and a full-time student,
        (
            {
                "parent": {"age": 50},
                "child": {"age": 21, "is_full_time_college_student": True},
            },
            [],
        ),
        # or permanently and totally disabled.
        (
            {
                "parent": {"age": 70},
                "child": {"age": 40, "is_permanently_and_totally_disabled": True},
            },
            [],
        ),
        # A separated member leaves the unit without a spouse.
        ({"first": {"age": 45}, "second": {"age": 40, "is_separated": True}}, []),
        # A pairing that changes between years pairs no one.
        ({"parent": {"age": 45}, "child": {"age": {"2024": 18, "2025": 19}}}, []),
    ],
)
def test_fallback_pairs_the_inferred_tax_head_and_spouse(people, pairs):
    assert _fallback_pairs(people) == pairs


@pytest.mark.parametrize(
    "roles, pairs",
    [
        # Supplied roles pair an 18-year-old spouse the age test would not.
        ({"first": "HEAD", "second": "SPOUSE"}, [["first", "second"]]),
        # And they keep a dependent adult out of a couple.
        ({"first": "HEAD", "second": "DEPENDENT"}, []),
    ],
)
def test_supplied_tax_roles_decide_the_couple(roles, pairs):
    people = {
        "first": {"age": 45, "tax_unit_role_input": roles["first"]},
        "second": {"age": 18 if roles["second"] == "SPOUSE" else 30},
    }
    people["second"]["tax_unit_role_input"] = roles["second"]
    assert _fallback_pairs(people) == pairs


def test_fallback_stops_at_a_false_is_married_or_another_household():
    adults = {"first": {"age": 45}, "second": {"age": 40}}
    unmarried = {"family": {"members": list(adults), "is_married": False}}
    assert _fallback_pairs(adults, families=unmarried) == []
    apart = {
        "one": {"members": ["first"]},
        "two": {"members": ["second"]},
    }
    assert _fallback_pairs(adults, households=apart) == []
