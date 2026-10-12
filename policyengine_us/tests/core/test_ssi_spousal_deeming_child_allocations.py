"""Invariants of the SSI ineligible-child allocation in spousal deeming.

20 CFR 416.1163(b) deducts an allocation from an ineligible spouse's income
for each ineligible child: 'your natural child or adopted child, or the
natural or adopted child of your spouse ... who lives in the same household
with you, and is not eligible for SSI benefits' (416.1160(d)). Each
Hypothesis example builds a batch of random households (a married couple,
their children, step-children, grandchildren, unrelated children and other
adults, some living elsewhere, filed in assorted tax units, with parent ids
on everyone, no one or some people) and checks:

1. Differential: every person's ssi_spousal_deeming_child_allocations
   equals an oracle written here from the regulation and the parent-link
   contract in household/demographic/person/_parent_links.py, without the
   model. The oracle knows each person's true parents, so with ids it is
   the regulation itself. Without ids it is the documented proxy: the
   co-resident members of the person's or the spouse's tax unit, and in a
   household with links only for an unlinked parent.
2. Spouses see the same total: a child of either spouse is a child of 'you
   or your spouse' for both.
3. Order: listing each household's people in reverse gives the same totals.
4. Monotonicity: raising every child's unearned income never raises a
   total (416.1163(b)(2)).
5. Deemed unearned income is the spouse's unearned income less the total,
   floored at zero (416.1163(b)(3)).

YAML covers the worked cases. This file routes to the Rest/core group.
"""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
# 416.1163(b)(1): the couple rate ($1,491) less the individual rate ($994).
MONTHLY_ALLOCATION = 1_491 - 994
CHILD_AGE = 18  # 416.1856(a)(1)
STUDENT_AGE = 22  # 416.1856(a)(2)
ABSENT_PARENT_ID = 999_999
HOUSEHOLDS_PER_EXAMPLE = 30

CHILD_KINDS = ("claimant", "spouse", "both", "grandchild", "unrelated")
OTHER = st.fixed_dictionaries(
    {
        "kind": st.sampled_from(CHILD_KINDS + ("adult",)),
        "age": st.integers(0, 23),
        "student": st.booleans(),
        "monthly_unearned": st.sampled_from((0, 150, 600)),
        # About one in four lives in another household.
        "away": st.sampled_from((False, False, False, True)),
        "tax_unit": st.sampled_from(("couple", "spouse", "own", "adult")),
        "has_ids": st.booleans(),
    }
)
HOUSEHOLD = st.fixed_dictionaries(
    {
        "aged_claimant": st.booleans(),
        "spouse_unearned": st.sampled_from((0, 300, 600, 1_200)),
        "spouse_files_separately": st.booleans(),
        "ids": st.sampled_from(("none", "all", "some")),
        "report_own_children": st.booleans(),
        "others": st.lists(OTHER, min_size=0, max_size=5),
    }
)
BATCH = st.lists(
    HOUSEHOLD, min_size=HOUSEHOLDS_PER_EXAMPLE, max_size=HOUSEHOLDS_PER_EXAMPLE
)


def _people(index, household):
    """Return each person's facts, with true parents and tax unit."""
    claimant, spouse = f"h{index}_claimant", f"h{index}_spouse"
    people = [
        dict(
            name=claimant,
            age=70 if household["aged_claimant"] else 45,
            disabled=not household["aged_claimant"],
            unearned=0,
            student=False,
            parents=(),
            away=False,
            tax_unit="couple",
            role="head",
        ),
        dict(
            name=spouse,
            age=50,
            disabled=False,
            unearned=household["spouse_unearned"],
            student=False,
            parents=(),
            away=False,
            tax_unit="spouse" if household["spouse_files_separately"] else "couple",
            role="head" if household["spouse_files_separately"] else "spouse",
        ),
    ]
    # The first other adult can parent grandchildren and head a tax unit.
    adult_position = next(
        (p for p, o in enumerate(household["others"]) if o["kind"] == "adult"),
        None,
    )
    adult = None if adult_position is None else f"h{index}_o{adult_position}"
    for position, other in enumerate(household["others"]):
        name = f"h{index}_o{position}"
        kind = other["kind"]
        parents = {
            "claimant": (claimant,),
            "spouse": (spouse, None),
            "both": (claimant, spouse),
            "grandchild": (adult,) if adult else (None,),
            "unrelated": (None,),
            "adult": (),
        }[kind]
        tax_unit = other["tax_unit"]
        if tax_unit == "spouse" and not household["spouse_files_separately"]:
            tax_unit = "couple"
        if tax_unit == "adult" and adult is None:
            tax_unit = "own"
        if kind == "adult":
            tax_unit = "adult" if name == adult else "own"
        people.append(
            dict(
                name=name,
                age=other["age"] + (30 if kind == "adult" else 0),
                disabled=False,
                unearned=other["monthly_unearned"],
                student=other["student"],
                # None is a parent who lives outside the simulation.
                parents=parents,
                away=other["away"] and kind != "adult",
                tax_unit=tax_unit,
                role="head" if tax_unit == "own" or name == adult else "dependent",
                has_ids=other["has_ids"],
            )
        )
    ids_mode = household["ids"]
    for person in people:
        person["has_ids"] = bool(person["parents"]) and (
            ids_mode == "all" or (ids_mode == "some" and person.get("has_ids"))
        )
    return people


def _tax_unit_key(index, person):
    if person["tax_unit"] == "own":
        return f"{person['name']}_tu"
    return f"h{index}_{person['tax_unit']}_tu"


def _situation(households, reverse=False, income_rise=0):
    situation = {
        plural: {}
        for plural in (
            "people",
            "tax_units",
            "households",
            "marital_units",
            "families",
            "spm_units",
        )
    }
    facts = {}
    person_ids = {}
    for index, household in enumerate(households):
        people = _people(index, household)
        if reverse:
            people = people[::-1]
        for number, person in enumerate(people):
            person_ids[person["name"]] = 1_000 * (index + 1) + number + 1
        # Each spouse reports their co-resident children when asked.
        own_children = {}
        for person in people:
            if not person["away"]:
                for parent in person["parents"]:
                    own_children[parent] = own_children.get(parent, 0) + 1
        for person in people:
            facts[person["name"]] = dict(person, household=index)
            child = person["age"] < CHILD_AGE
            parent_ids = [
                (
                    person_ids.get(parent, ABSENT_PARENT_ID)
                    if parent
                    else ABSENT_PARENT_ID
                )
                for parent in person["parents"]
            ]
            parent_ids = (parent_ids + [0, 0])[:2] if person["has_ids"] else [0, 0]
            reports = household["report_own_children"] and person["name"].endswith(
                ("_claimant", "_spouse")
            )
            situation["people"][person["name"]] = {
                "age": {YEAR: person["age"]},
                "is_ssi_disabled": {YEAR: person["disabled"]},
                "ssi_unearned_income": {
                    YEAR: 12 * (person["unearned"] + (income_rise if child else 0))
                },
                "is_full_time_college_student": {YEAR: person["student"]},
                "is_in_k12_school": {YEAR: False},
                "person_id": {YEAR: person_ids[person["name"]]},
                "parent_1_id": {YEAR: parent_ids[0]},
                "parent_2_id": {YEAR: parent_ids[1]},
                "own_children_in_household": {
                    YEAR: own_children.get(person["name"], 0) if reports else 0
                },
                "is_tax_unit_head": {YEAR: person["role"] == "head"},
                "is_tax_unit_spouse": {YEAR: person["role"] == "spouse"},
                "is_tax_unit_dependent": {YEAR: person["role"] == "dependent"},
            }
            units = {
                "tax_units": _tax_unit_key(index, person),
                "households": (
                    f"{person['name']}_away" if person["away"] else f"h{index}_home"
                ),
                "marital_units": (
                    f"h{index}_couple"
                    if person["name"].endswith(("_claimant", "_spouse"))
                    else f"{person['name']}_mu"
                ),
            }
            units["families"] = units["households"]
            units["spm_units"] = units["households"]
            for plural, key in units.items():
                group = situation[plural].setdefault(key, {"members": []})
                group["members"].append(person["name"])
                if plural == "households":
                    group["state_code"] = {YEAR: "TX"}
    return situation, facts


def _allocation(person):
    """416.1163(b)(1)-(2) for the oracle's people, who have no earnings."""
    child = person["age"] < CHILD_AGE or (
        person["age"] < STUDENT_AGE and person["student"]
    )
    if not child or person["disabled"]:
        return 0
    return max(0, 12 * (MONTHLY_ALLOCATION - person["unearned"]))


def _oracle(facts):
    """Each person's total, from true relationships and the id contract."""
    names = list(facts)
    spouse_of = {}
    for name in names:
        if name.endswith("_claimant"):
            spouse_of[name] = name.replace("_claimant", "_spouse")
        elif name.endswith("_spouse"):
            spouse_of[name] = name.replace("_spouse", "_claimant")

    def home(name):
        person = facts[name]
        return (person["household"], person["away"] and name)

    def tax_unit(name):
        return _tax_unit_key(facts[name]["household"], facts[name])

    def co_resident_named_parents(name):
        if not facts[name]["has_ids"]:
            return set()
        return {
            parent
            for parent in facts[name]["parents"]
            if parent and home(parent) == home(name)
        }

    def linked_count(name):
        return sum(name in co_resident_named_parents(other) for other in names)

    def household_linked(name):
        return any(
            facts[other]["has_ids"] for other in names if home(other) == home(name)
        )

    def unlinked_parent(name):
        own = facts[name].get("reported_children", 0)
        linked = linked_count(name)
        return (own > 0 or linked > 0) and (linked == 0 or own > linked)

    totals = {}
    for name in names:
        selves = {name} | ({spouse_of[name]} if name in spouse_of else set())
        presume = not household_linked(name) or any(
            unlinked_parent(member) for member in selves
        )
        units = {tax_unit(member) for member in selves}
        total = 0
        for other in names:
            if other in selves or home(other) != home(name):
                continue
            if facts[other]["has_ids"]:
                counts = bool(co_resident_named_parents(other) & selves)
            else:
                counts = presume and tax_unit(other) in units
            total += counts * _allocation(facts[other])
        totals[name] = total
    return totals


def _record_reported_children(situation, facts):
    for name, person in facts.items():
        person["reported_children"] = situation["people"][name][
            "own_children_in_household"
        ][YEAR]


def _calculate(situation, variables):
    simulation = Simulation(situation=situation)
    names = list(situation["people"])
    return {
        variable: dict(zip(names, simulation.calculate(variable, YEAR)))
        for variable in variables
    }


@settings(max_examples=3, derandomize=True, deadline=None)
@given(BATCH)
def test_allocations_match_oracle_and_invariants(households):
    variables = (
        "ssi_spousal_deeming_child_allocations",
        "ssi_unearned_income_deemed_from_ineligible_spouse",
        "is_ssi_ineligible_spouse",
    )
    situation, facts = _situation(households)
    _record_reported_children(situation, facts)
    results = _calculate(situation, variables)
    totals = results["ssi_spousal_deeming_child_allocations"]
    oracle = _oracle(facts)

    # 1. Differential against the oracle.
    for name in facts:
        assert totals[name] == oracle[name], name

    for index in range(len(households)):
        claimant, spouse = f"h{index}_claimant", f"h{index}_spouse"
        # 2. Both spouses see the same children.
        assert totals[claimant] == totals[spouse]
        # 5. Deemed unearned income, 416.1163(b)(3).
        assert results["is_ssi_ineligible_spouse"][spouse]
        spouse_unearned = 12 * facts[spouse]["unearned"]
        assert results["ssi_unearned_income_deemed_from_ineligible_spouse"][
            claimant
        ] == max(0, spouse_unearned - totals[claimant])

    # 3. Order of people.
    reversed_situation, _ = _situation(households, reverse=True)
    reversed_totals = _calculate(
        reversed_situation, ("ssi_spousal_deeming_child_allocations",)
    )["ssi_spousal_deeming_child_allocations"]
    assert reversed_totals == totals

    # 4. Children's income never raises a total.
    richer_situation, _ = _situation(households, income_rise=100)
    richer_totals = _calculate(
        richer_situation, ("ssi_spousal_deeming_child_allocations",)
    )["ssi_spousal_deeming_child_allocations"]
    assert all(richer_totals[name] <= totals[name] for name in totals)
