"""Properties of the parent-id path over seeded random households.

Each test draws households from a fixed seed, so a failure reproduces exactly.
"""

from copy import deepcopy

import numpy as np

from policyengine_us import Simulation

PERIOD = "2026"
N_HOUSEHOLDS = 30

MEDICAID_OUTPUTS = [
    "is_parent",
    "is_mother",
    "is_father",
    "medicaid_claimed_by_parent_in_tax_unit",
    "medicaid_tax_dependent_exception_living_with_both_parents",
    "medicaid_uses_non_filer_rules",
    "medicaid_household_size",
    "medicaid_household_income",
    "is_medicaid_eligible",
]


def random_households(seed):
    """Households of one to six people with random co-resident parent links.

    Each child names up to two distinct adults of the same household; ids are
    household-local and start at 1, since 0 means "unknown".
    """
    rng = np.random.default_rng(seed)
    households = []
    for h in range(N_HOUSEHOLDS):
        adults = int(rng.integers(1, 4))
        children = int(rng.integers(0, 4))
        people = []
        for a in range(adults):
            people.append(
                {
                    "name": f"h{h}_adult{a}",
                    "age": int(rng.integers(18, 70)),
                    "is_female": bool(rng.integers(0, 2)),
                    "employment_income": float(rng.integers(0, 60_000)) + 0.37,
                    "parents": [],
                }
            )
        for c in range(children):
            k = int(rng.integers(0, min(adults, 2) + 1))
            parents = list(rng.choice(adults, size=k, replace=False)) if k else []
            people.append(
                {
                    "name": f"h{h}_child{c}",
                    "age": int(rng.integers(0, 19)),
                    "is_female": bool(rng.integers(0, 2)),
                    "employment_income": float(rng.integers(0, 3_000)),
                    "parents": [int(p) for p in parents],
                }
            )
        households.append(people)
    return households


def situation(households, *, with_ids, explicit_zero=False, order=None):
    people, groups = {}, {}
    for h, members in enumerate(households):
        indices = list(range(len(members)))
        if order is not None:
            indices = [int(i) for i in order[h]]
        names = []
        for i in indices:
            person = members[i]
            inputs = {
                "age": {PERIOD: person["age"]},
                "is_female": {PERIOD: person["is_female"]},
                "employment_income": {PERIOD: person["employment_income"]},
                "person_id": {PERIOD: i + 1},
                # The legacy count the CPS carries, consistent with the links.
                "own_children_in_household": {
                    PERIOD: sum(i in other["parents"] for other in members)
                },
            }
            if with_ids:
                ids = [p + 1 for p in person["parents"]] + [0, 0]
                inputs["parent_1_id"] = {PERIOD: ids[0]}
                inputs["parent_2_id"] = {PERIOD: ids[1]}
            elif explicit_zero:
                inputs["parent_1_id"] = {PERIOD: 0}
                inputs["parent_2_id"] = {PERIOD: 0}
            people[person["name"]] = inputs
            names.append(person["name"])
        groups[f"h{h}"] = names
    return {
        "people": people,
        "tax_units": {k: {"members": v} for k, v in groups.items()},
        "spm_units": {k: {"members": v} for k, v in groups.items()},
        "families": {k: {"members": v} for k, v in groups.items()},
        "marital_units": {name: {"members": [name]} for name in people},
        "households": {
            k: {"members": v, "state_code": {PERIOD: "OH"}} for k, v in groups.items()
        },
    }


def by_name(simulation, variable):
    values = simulation.calculate(variable, PERIOD)
    names = simulation.persons.ids
    return dict(zip(names, values))


def test_explicit_zero_ids_match_omitted_ids_for_random_households():
    households = random_households(seed=9404)
    omitted = Simulation(situation=situation(households, with_ids=False))
    zeros = Simulation(
        situation=situation(households, with_ids=False, explicit_zero=True)
    )
    for variable in MEDICAID_OUTPUTS:
        np.testing.assert_array_equal(
            zeros.calculate(variable, PERIOD),
            omitted.calculate(variable, PERIOD),
            err_msg=variable,
        )


def test_is_parent_from_ids_agrees_with_the_consistent_child_count():
    # When own_children_in_household counts exactly the people whose ids name
    # a person, the id path and the count path must agree on who is a parent.
    households = random_households(seed=884)
    linked = Simulation(situation=situation(households, with_ids=True))
    counted = Simulation(situation=situation(households, with_ids=False))
    np.testing.assert_array_equal(
        linked.calculate("is_parent", PERIOD),
        counted.calculate("is_parent", PERIOD),
    )


def test_is_parent_is_invariant_to_member_order():
    households = random_households(seed=435603)
    rng = np.random.default_rng(1)
    order = [rng.permutation(len(members)) for members in households]
    forward = Simulation(situation=situation(households, with_ids=True))
    shuffled = Simulation(situation=situation(households, with_ids=True, order=order))
    assert by_name(forward, "is_parent") == by_name(shuffled, "is_parent")
    assert by_name(forward, "is_mother") == by_name(shuffled, "is_mother")


# Linked households for the Medicaid MAGI non-filer composition.

AGE_LIMIT = 19  # gov.hhs.medicaid.household.child_age_limit.non_student


def random_linked_households(
    seed, *, drop_ids=0.0, extra_count=0.0, split_families=0.0, n=40
):
    """Households with true parent-child relationships and recorded ids.

    Children draw zero to two co-resident parents at least 14 years older
    (teen parents included) and, when they have fewer than two, possibly an
    absent parent whose id another child can share. Every child has at least
    one parent. ``drop_ids`` zeroes a child's recorded ids while its parents
    still count it; ``extra_count`` adds a child no id names to an adult's
    count; ``split_families`` spreads members over two family entities.
    Incomes are multiples of 1/8 below 2**20, so float32 storage and float64
    sums are exact in any order.
    """
    rng = np.random.default_rng(seed)
    households = []
    for h in range(n):
        people = []
        for a in range(int(rng.integers(1, 4))):
            people.append({"name": f"h{h}_a{a}", "age": int(rng.integers(18, 70))})
        married = len(people) >= 2 and rng.random() < 0.4
        # Older children come first, so a teen can parent a later baby.
        ages = sorted(rng.integers(0, 21, size=int(rng.integers(0, 5))), reverse=True)
        if rng.random() < 0.3:
            ages = [int(rng.integers(14, 19))] + ages + [int(rng.integers(0, 2))]
        for c, age in enumerate(ages):
            people.append({"name": f"h{h}_c{c}", "age": int(age)})
        for i, person in enumerate(people):
            candidates = [k for k in range(i) if people[k]["age"] >= person["age"] + 14]
            is_child = person["name"].split("_")[1].startswith("c")
            k = int(rng.integers(1 if not candidates else 0, 3)) if is_child else 0
            k = min(k, len(candidates))
            parents = [int(p) for p in rng.choice(candidates, size=k, replace=False)]
            absent = []
            if is_child and len(parents) < 2 and (not parents or rng.random() < 0.3):
                absent = [900 + int(rng.integers(0, 3))]
            recorded = [p + 1 for p in parents] + absent
            rng.shuffle(recorded)
            person.update(
                parents=parents,
                absent=absent,
                recorded=[0, 0]
                if is_child and rng.random() < drop_ids
                else (recorded + [0, 0])[:2],
                extra=int(not is_child and rng.random() < extra_count),
                family=int(rng.random() < split_families),
                income=float(rng.integers(0, 80_000 * 8)) / 8,
                pregnancies=int(12 <= person["age"] <= 45 and rng.random() < 0.15),
                spouse=None,
            )
        if married:
            people[0]["spouse"], people[1]["spouse"] = 1, 0
        households.append(people)
    return households


def linked_situation(households, order=None):
    people, households_, families, tax_units, marital_units = {}, {}, {}, {}, {}
    for h, members in enumerate(households):
        indices = range(len(members)) if order is None else order[h]
        names = []
        for i in indices:
            i = int(i)
            person = members[i]
            children = sum(i in other["parents"] for other in members)
            people[person["name"]] = {
                "age": {PERIOD: person["age"]},
                "person_id": {PERIOD: i + 1},
                "parent_1_id": {PERIOD: person["recorded"][0]},
                "parent_2_id": {PERIOD: person["recorded"][1]},
                "own_children_in_household": {PERIOD: children + person["extra"]},
                "current_pregnancies": {PERIOD: person["pregnancies"]},
                "medicaid_uses_non_filer_rules": {PERIOD: True},
                "medicaid_household_income_member": {PERIOD: person["income"]},
            }
            names.append(person["name"])
        households_[f"h{h}"] = {"members": names, "state_code": {PERIOD: "CA"}}
        for f in (0, 1):
            family = [n for n in names if members[_index(members, n)]["family"] == f]
            if family:
                families[f"h{h}_f{f}"] = {"members": family}
        couple = [n for n in names if members[_index(members, n)]["spouse"] is not None]
        rest = [n for n in names if n not in couple]
        if couple:
            tax_units[f"h{h}_couple"] = {
                "members": couple,
                "filing_status": {PERIOD: "JOINT"},
            }
            marital_units[f"h{h}_couple"] = {"members": couple}
        # Everyone outside the couple files alone: PE treats any tax unit with
        # two adults as married.
        for name in rest:
            tax_units[name] = {"members": [name]}
            marital_units[name] = {"members": [name]}
    return {
        "people": people,
        "households": households_,
        "families": families,
        "tax_units": tax_units,
        "spm_units": {k: {"members": v["members"]} for k, v in households_.items()},
        "marital_units": marital_units,
    }


def _index(members, name):
    return next(i for i, person in enumerate(members) if person["name"] == name)


def true_members(members, i):
    """42 CFR 435.603(f)(3) membership from the true relationships."""
    person = members[i]
    child = person["age"] < AGE_LIMIT
    result = {i}
    for m, other in enumerate(members):
        other_child = other["age"] < AGE_LIMIT
        shared = set(person["parents"]) & set(other["parents"]) or (
            set(person["absent"]) & set(other["absent"])
        )
        if (
            person["spouse"] == m
            or (other_child and i in other["parents"])
            or (child and m in person["parents"])
            or (child and other_child and m != i and shared)
        ):
            result.add(m)
    return result


def rule_members(members, i):
    """Scalar statement of the membership rule documented for data with gaps.

    Links resolve by recorded id. Main's family proxy survives only among
    unlinked people: child-age members without ids and members reporting
    more own children than the ids naming them.
    """
    ids = [person["recorded"] for person in members]
    by_id = {k + 1: k for k in range(len(members))}
    parents = [
        {by_id[x] for x in pair if x in by_id and by_id[x] != k}
        for k, pair in enumerate(ids)
    ]
    child = [person["age"] < AGE_LIMIT for person in members]
    unlinked = [child[k] and not any(ids[k]) for k in range(len(members))]
    linked_children = [sum(k in p for p in parents) for k in range(len(members))]
    reports = [
        sum(k in other["parents"] for other in members) + members[k]["extra"]
        > linked_children[k]
        for k in range(len(members))
    ]
    family = [person["family"] for person in members]

    def reporting_parent_in(k, fam):
        return any(reports[p] and family[p] == fam for p in parents[k])

    result = {i}
    for m in range(len(members)):
        if m == i:
            continue
        same_family = family[m] == family[i]
        spouse = members[i]["spouse"] == m
        own_child = child[m] and (
            i in parents[m] or (reports[i] and unlinked[m] and same_family)
        )
        parent = child[i] and (
            m in parents[i] or (unlinked[i] and reports[m] and same_family)
        )
        sibling = (
            child[i]
            and child[m]
            and (
                bool(({*ids[i]} - {0}) & ({*ids[m]} - {0}))
                or (unlinked[m] and reporting_parent_in(i, family[m]))
                or (unlinked[i] and reporting_parent_in(m, family[i]))
                or (unlinked[i] and unlinked[m] and same_family)
            )
        )
        if spouse or own_child or parent or sibling:
            result.add(m)
    return result


def check_composition(households, members_of):
    simulation = Simulation(situation=linked_situation(households))
    size = by_name(simulation, "medicaid_household_size")
    income = by_name(simulation, "medicaid_household_income")
    pregnancies = by_name(simulation, "ca_medicaid_household_pregnancies")
    # Households without any nonzero id keep main's family-sum expressions,
    # which the zero-id differential covers; check every household with ids.
    linked = [
        people for people in households if any(any(p["recorded"]) for p in people)
    ]
    assert len(linked) >= len(households) // 2
    for people in linked:
        for i, person in enumerate(people):
            members = members_of(people, i)
            expected_pregnancies = sum(people[m]["pregnancies"] for m in members)
            name = person["name"]
            assert size[name] >= 1, name
            assert pregnancies[name] == expected_pregnancies, name
            # California counts each member's unborn children in the size.
            assert size[name] == len(members) + expected_pregnancies, name
            assert income[name] == np.float32(
                sum(people[m]["income"] for m in members)
            ), name


def test_linked_composition_matches_the_regulation_on_consistent_data():
    # Consistent ids and counts: every relationship is recorded, so the
    # household must be exactly the one 42 CFR 435.603(f)(3) defines.
    check_composition(random_linked_households(seed=435603), true_members)


def test_linked_composition_follows_the_documented_rule_on_gappy_data():
    households = random_linked_households(
        seed=9406, drop_ids=0.3, extra_count=0.2, split_families=0.3
    )
    check_composition(households, rule_members)


def test_linked_composition_is_invariant_to_member_order():
    households = random_linked_households(
        seed=20260926, drop_ids=0.3, extra_count=0.2, split_families=0.3
    )
    rng = np.random.default_rng(2)
    order = [rng.permutation(len(members)) for members in households]
    forward = Simulation(situation=linked_situation(households))
    shuffled = Simulation(situation=linked_situation(households, order=order))
    for variable in [
        "is_parent",
        "medicaid_household_size",
        "medicaid_household_income",
        "ca_medicaid_household_pregnancies",
    ]:
        assert by_name(forward, variable) == by_name(shuffled, variable), variable


def test_is_parent_is_the_union_of_the_child_count_and_the_links():
    # Neither source erases the other, whatever the gaps in the data.
    households = random_linked_households(
        seed=884, drop_ids=0.3, extra_count=0.2, split_families=0.3
    )
    simulation = Simulation(situation=linked_situation(households))
    is_parent = by_name(simulation, "is_parent")
    for people in households:
        for i, person in enumerate(people):
            counted = sum(i in other["parents"] for other in people) + person["extra"]
            named = any(i + 1 in other["recorded"] for other in people)
            assert is_parent[person["name"]] == (counted > 0 or named), person["name"]
