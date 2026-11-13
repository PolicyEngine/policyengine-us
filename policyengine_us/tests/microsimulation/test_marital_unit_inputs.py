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
def test_ambiguous_or_changing_roles_give_everyone_their_own_unit(extra_inputs):
    # These computed on main, so the hook pairs no one rather than raising.
    situation = _explicit_pair()
    situation["people"]["spouse"].update(extra_inputs)
    assert _pairs(situation) == []


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


def test_a_changing_is_married_input_pairs_no_one():
    situation = _married_family()
    situation["families"]["family"]["is_married"] = {"2024": True, "2025": False}
    assert _pairs(situation) == []


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
        # The role formulas take adults from is_child, which can be an input.
        ({"parent": {"age": 45}, "child": {"age": 30, "is_child": True}}, []),
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


@pytest.mark.parametrize(
    "order",
    [
        ["grandchild", "husband", "wife"],
        ["husband", "grandchild", "wife"],
    ],
)
def test_inputs_dated_after_the_default_input_year_keep_the_couple(order):
    # Simulation's default input year is 2024; a payload dated 2026 must
    # still pair its couple wherever they are listed.
    people = {
        "grandchild": {"age": {"2026": 10}},
        "husband": {"age": {"2026": 70}},
        "wife": {"age": {"2026": 68}},
    }
    sim = Simulation(situation={"people": {name: people[name] for name in order}})
    units = sim.marital_unit.members_entity_id.tolist()
    index = {name: position for position, name in enumerate(order)}
    assert units[index["husband"]] == units[index["wife"]]
    assert units[index["grandchild"]] != units[index["husband"]]


def test_two_tax_units_each_pair_their_own_couple():
    people = {
        "first_head": {"age": 45},
        "first_spouse": {"age": 43},
        "second_head": {"age": 40},
        "second_spouse": {"age": 38},
        "child": {"age": 5},
    }
    situation = {
        "people": people,
        "tax_units": {
            "first": {"members": ["first_head", "first_spouse", "child"]},
            "second": {"members": ["second_head", "second_spouse"]},
        },
    }
    units = infer_missing_marital_units(situation, "2024", system)["marital_units"]
    pairs = sorted(
        sorted(unit["members"]) for unit in units.values() if len(unit["members"]) > 1
    )
    assert pairs == [["first_head", "first_spouse"], ["second_head", "second_spouse"]]


def test_two_couples_in_one_tax_unit_pair_only_the_role_couple():
    # A known limitation: the role formulas pick one head and one spouse.
    people = {
        "older_husband": {"age": 70},
        "older_wife": {"age": 68},
        "younger_husband": {"age": 45},
        "younger_wife": {"age": 43},
    }
    assert _fallback_pairs(people) == [["older_husband", "older_wife"]]


def test_integer_person_ids_pair():
    people = {1: {"age": 45}, 2: {"age": 43}, 3: {"age": 10}}
    assert _fallback_pairs(people) == [["1", "2"]]


def test_a_false_spouse_input_leaves_the_roles_without_a_couple():
    people = {"first": {"age": 45}, "second": {"age": 43, "is_tax_unit_spouse": False}}
    assert _fallback_pairs(people) == []


@pytest.mark.parametrize(
    "filing_status, pairs",
    [
        (None, []),
        # Only a married couple files jointly (26 USC 6013(a)).
        ("JOINT", [["head", "spouse"]]),
    ],
)
def test_a_joint_return_pairs_a_spouse_the_age_test_would_not(filing_status, pairs):
    people = {
        "head": {"age": 22},
        "spouse": {"age": 20, "is_full_time_college_student": True},
    }
    tax_units = {"tax_unit": {"members": list(people)}}
    if filing_status is not None:
        tax_units["tax_unit"]["filing_status"] = filing_status
    assert _fallback_pairs(people, tax_units=tax_units) == pairs


@pytest.mark.parametrize(
    "households, pairs",
    [
        # Only married people file separately (26 USC 1(d)).
        ({"home": {"members": ["first", "second"]}}, [["first", "second"]]),
        # Three separate filers don't say who is married to whom.
        ({"home": {"members": ["first", "second", "third"]}}, []),
        # A marital unit is a married, co-habiting couple.
        ({"one": {"members": ["first"]}, "two": {"members": ["second"]}}, []),
    ],
)
def test_the_two_separate_filers_of_a_household_pair(households, pairs):
    names = [name for home in households.values() for name in home["members"]]
    people = {name: {"age": 45} for name in names}
    tax_units = {
        name: {"members": [name], "filing_status": "SEPARATE"} for name in names
    }
    assert _fallback_pairs(people, tax_units=tax_units, households=households) == pairs


@pytest.mark.parametrize(
    "roles, status",
    [
        # Explicit roles settle the couple whatever the status says.
        (
            {
                "husband": {"is_tax_unit_head": True},
                "wife": {"is_tax_unit_spouse": True},
            },
            {"2025": "JOINT", "2026": "SEPARATE"},
        ),
        # Without roles, step 4 pairs them as it would with no status.
        ({}, {"2025": "SINGLE", "2026": "HEAD_OF_HOUSEHOLD"}),
    ],
)
def test_a_changing_filing_status_counts_as_no_status(roles, status):
    people = {
        "husband": {"age": 70, **roles.get("husband", {})},
        "wife": {"age": 68, **roles.get("wife", {})},
    }
    tax_units = {"tax_unit": {"members": list(people), "filing_status": status}}
    assert _fallback_pairs(people, tax_units=tax_units) == [["husband", "wife"]]


def _separate_return_pairs(tax_units, people, **groups):
    # Every tax unit files separately, all in one household.
    situation = {
        "people": people,
        "tax_units": {
            name: {"members": members, "filing_status": "SEPARATE"}
            for name, members in tax_units.items()
        },
        "households": {"home": {"members": list(people)}},
        **groups,
    }
    units = infer_missing_marital_units(situation, "2024", system)["marital_units"]
    return sorted(
        sorted(unit["members"]) for unit in units.values() if len(unit["members"]) > 1
    )


@pytest.mark.parametrize(
    "tax_units, people, groups, pairs",
    [
        # A separated filer pairs no one.
        (
            {"one": ["first"], "two": ["second"]},
            {"first": {"age": 45}, "second": {"age": 45, "is_separated": True}},
            {},
            [],
        ),
        # Nor does a family that says the two aren't married.
        (
            {"one": ["first"], "two": ["second"]},
            {"first": {"age": 45}, "second": {"age": 45}},
            {
                "families": {
                    "family": {"members": ["first", "second"], "is_married": False}
                }
            },
            [],
        ),
        # A separate return with no clear filer (two adults, neither a head
        # input nor a dependent) still counts, so three returns pair no one.
        (
            {"one": ["first"], "two": ["second"], "three": ["third", "fourth"]},
            {
                "first": {"age": 45},
                "second": {"age": 45},
                "third": {"age": 45},
                "fourth": {"age": 45, "is_tax_unit_spouse": False},
            },
            {},
            [],
        ),
        # A true is_tax_unit_head input names the filer of a two-adult unit.
        (
            {"one": ["first", "roommate"], "two": ["second"]},
            {
                "first": {"age": 45, "is_tax_unit_head": True},
                "roommate": {"age": 30, "is_tax_unit_spouse": False},
                "second": {"age": 45},
            },
            {},
            [["first", "second"]],
        ),
        # An adult input as a dependent isn't the filer.
        (
            {"one": ["first", "parent"], "two": ["second"]},
            {
                "first": {"age": 45},
                "parent": {"age": 70, "is_tax_unit_dependent": True},
                "second": {"age": 45},
            },
            {},
            [["first", "second"]],
        ),
        # Nor is a person input as a child, whatever their age.
        (
            {"one": ["first", "kid"], "two": ["second"]},
            {
                "first": {"age": 45},
                "kid": {"age": 30, "is_child": True},
                "second": {"age": 45},
            },
            {},
            [["first", "second"]],
        ),
        # A filer already in a couple from the earlier steps stays in it.
        (
            {"one": ["first", "partner"], "two": ["second"]},
            {
                "first": {"age": 45, "is_tax_unit_head": True},
                "partner": {"age": 43, "is_tax_unit_spouse": True},
                "second": {"age": 45},
            },
            {},
            [["first", "partner"]],
        ),
    ],
)
def test_the_separate_filer_rules(tax_units, people, groups, pairs):
    assert _separate_return_pairs(tax_units, people, **groups) == pairs


def test_a_married_family_skips_a_person_input_as_a_child():
    # The role formulas take adults from is_child, so a 21-year-old input as
    # a child doesn't make the married family ambiguous.
    situation = _married_family(
        adult_child={"age": {"2024": 21}, "is_child": {"2024": True}}
    )
    assert _pairs(situation) == [["first", "second"]]


def test_the_adult_age_matches_is_child():
    from policyengine_us.tools import marital_units

    sim = Simulation(
        situation={
            "people": {"minor": {"age": {"2024": 17}}, "adult": {"age": {"2024": 18}}}
        }
    )
    assert sim.calculate("is_child", 2024).tolist() == [
        age < marital_units._ADULT_AGE for age in (17, 18)
    ]


@pytest.mark.parametrize("variable", ["is_tax_unit_spouse", "is_tax_unit_head"])
def test_a_role_input_on_anyone_fills_false_for_the_rest(variable):
    # Core fills the role for everyone once a grandchild supplies it, so the
    # roles have no couple, and neither do the marital units.
    people = {
        "husband": {"age": {"2026": 70}},
        "wife": {"age": {"2026": 68}},
        "grandchild": {"age": {"2026": 10}, variable: {"2026": False}},
    }
    sim = Simulation(situation={"people": people})
    assert len(set(sim.marital_unit.members_entity_id.tolist())) == 3


def test_a_student_input_on_anyone_fills_false_for_the_rest():
    # Another person's is_full_time_student input gives the college student
    # the default false, so the role formulas pair them with their parent.
    people = {
        "parent": {"age": 45},
        "student": {"age": 22, "is_full_time_college_student": True},
        "child": {"age": 10, "is_full_time_student": False},
    }
    assert _fallback_pairs(people) == [["parent", "student"]]


def test_a_reform_to_the_age_limit_changes_the_couple():
    from policyengine_core.reforms import Reform

    people = {"parent": {"age": {"2026": 45}}, "child": {"age": {"2026": 25}}}
    reform = Reform.from_dict(
        {"gov.irs.dependent.ineligible_age.non_student": {"2026-01-01.2100-12-31": 30}},
        country_id="us",
    )
    baseline = Simulation(situation={"people": deepcopy(people)})
    reformed = Simulation(situation={"people": deepcopy(people)}, reform=reform)
    # A 25-year-old fails the baseline age test (under 19) and passes the
    # reformed one (under 30), so only the baseline pairs them.
    assert len(set(baseline.marital_unit.members_entity_id.tolist())) == 1
    assert len(set(reformed.marital_unit.members_entity_id.tolist())) == 2


def test_undated_role_inputs_set_units_for_the_default_input_year():
    # A known limitation: the undated inputs land in 2024, where the
    # grandchild's false spouse input leaves the roles without a couple, so
    # the grandparents get their own units. In 2026, with no role input, the
    # role formulas run again and pair them, which the units don't follow.
    people = {
        "husband": {"age": 70},
        "wife": {"age": 68},
        "grandchild": {"age": 10, "is_tax_unit_spouse": False},
    }
    sim = Simulation(situation={"people": people})
    assert len(set(sim.marital_unit.members_entity_id.tolist())) == 3
    assert sim.calculate("is_tax_unit_spouse", 2026).tolist() == [False, True, False]
