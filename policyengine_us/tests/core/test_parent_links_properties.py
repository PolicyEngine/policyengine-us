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
    one parent. A married couple files jointly, so a child whose ids name one
    spouse alone has the other as a step parent (42 CFR 435.603(b)); a child
    never names one spouse and a third adult, since two id slots cannot
    record three co-resident parents. ``drop_ids`` zeroes a child's recorded
    ids while its parents still count it; ``extra_count`` adds a child no id
    names to an adult's count; ``split_families`` spreads members over two
    family entities.
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
            in_couple = [p for p in parents if married and p in (0, 1)]
            if len(in_couple) == 1 and len(parents) == 2:
                parents = [in_couple[0], 1 - in_couple[0]]
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
            # A married couple living together is one family.
            people[0]["spouse"], people[1]["spouse"] = 1, 0
            people[1]["family"] = people[0]["family"]
        for person in people:
            # Legal co-resident parents: a lone parent's spouse is a step parent.
            legal = list(person["parents"])
            if len(legal) == 1 and people[legal[0]]["spouse"] is not None:
                legal.append(people[legal[0]]["spouse"])
            person["legal"] = legal
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
    """42 CFR 435.603(f)(3) membership from the true relationships.

    Parents, children and siblings include step relatives (435.603(b)).
    """
    person = members[i]
    child = person["age"] < AGE_LIMIT
    result = {i}
    for m, other in enumerate(members):
        other_child = other["age"] < AGE_LIMIT
        shared = set(person["legal"]) & set(other["legal"]) or (
            set(person["absent"]) & set(other["absent"])
        )
        if (
            person["spouse"] == m
            or (other_child and i in other["legal"])
            or (child and m in person["legal"])
            or (child and other_child and m != i and shared)
        ):
            result.add(m)
    return result


def rule_members(members, i):
    """Scalar statement of the membership rule documented for data with gaps.

    Links resolve by recorded id. When the ids name exactly one co-resident
    parent, that parent's spouse (the couple files jointly) is a step parent.
    Main's family proxy survives only among unlinked people: child-age
    members without ids and members reporting more own children than the ids
    naming them.
    """
    ids = [person["recorded"] for person in members]
    by_id = {k + 1: k for k in range(len(members))}
    named = [
        {by_id[x] for x in pair if x in by_id and by_id[x] != k}
        for k, pair in enumerate(ids)
    ]
    parents = [set(p) for p in named]
    for k, p in enumerate(named):
        if len(p) == 1:
            step = members[next(iter(p))]["spouse"]
            if step is not None and step != k and k not in named[step]:
                parents[k].add(step)
    child = [person["age"] < AGE_LIMIT for person in members]
    unlinked = [child[k] and not any(ids[k]) for k in range(len(members))]
    # is_parent counts only the parents the ids name.
    linked_children = [sum(k in p for p in named) for k in range(len(members))]
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
        spouse = members[i]["spouse"] == m and same_family
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
                or bool(parents[i] & parents[m])
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


# A tax dependent's co-resident spouse on the tax-household route.

SPOUSE_PLACEMENTS = [
    "unmarried",
    # Living with the child, filing alone with the cohabiting-spouses flag.
    "flagged",
    # Living with the child in one family, filing alone without the flag.
    "same_family",
    # Living with the child in one family, claimed on the parent's return too.
    "same_return",
    # Living with the child in one family, filing alone, claimed by the
    # parent's return from the spouse's own unit.
    "claimed_into",
    # Married to the child but living in another household.
    "elsewhere",
]
# Placements whose marriage the family shows, since no flag or joint return
# does; the last two already belong to the parent's tax household.
IN_CHILDS_FAMILY = ("same_family", "same_return", "claimed_into")


def random_married_dependents(seed, n=60):
    """Parents claiming a child whose id names them; the child may be married.

    The parent claims the child either on the parent's own return or, as a
    known claiming tax unit, from the child's separate unit. Every tax unit
    gets a distinct tax_unit_id. Incomes are multiples of 1/8 below 2**20.
    """
    rng = np.random.default_rng(seed)
    return [
        {
            "parent_income": float(rng.integers(0, 80_000 * 8)) / 8,
            "child_age": int(rng.integers(15, 26)),
            "child_with_parent": bool(rng.random() < 0.5),
            "known_claim": bool(rng.random() < 0.5),
            "placement": SPOUSE_PLACEMENTS[int(rng.integers(len(SPOUSE_PLACEMENTS)))],
            "spouse_age": int(rng.integers(16, 31)),
            "spouse_income": float(rng.integers(0, 80_000 * 8)) / 8,
            "spouse_must_file": bool(rng.random() < 0.5),
            "pregnancies": [int(rng.random() < 0.2) for _ in range(3)],
        }
        for _ in range(n)
    ]


def married_dependent_situation(scenarios, reverse=False, with_ids=True, prefix="s"):
    """Scenarios as a situation; ``prefix`` keeps names and tax unit ids apart."""
    people, households, families, tax_units, marital_units = {}, {}, {}, {}, {}
    id_offset = 0 if prefix == "s" else 10_000

    def ordered(members):
        return members[::-1] if reverse else members

    for s, scenario in enumerate(scenarios):
        name = f"{prefix}{s}"
        parent, child, spouse = f"{name}_parent", f"{name}_child", f"{name}_spouse"
        placement = scenario["placement"]
        spouse_income = scenario["spouse_income"]
        # Countable income follows 42 CFR 435.603(d)(2)(i)'s child-age proxy.
        spouse_member_income = spouse_income * (
            scenario["spouse_must_file"] or scenario["spouse_age"] >= AGE_LIMIT
        )
        for name, person_id, age, magi, member_income, must_file in [
            (parent, 1, 45, scenario["parent_income"], scenario["parent_income"], True),
            (child, 2, scenario["child_age"], 0, 0, False),
            (
                spouse,
                3,
                scenario["spouse_age"],
                spouse_income,
                spouse_member_income,
                scenario["spouse_must_file"],
            ),
        ]:
            people[name] = {
                "age": {PERIOD: age},
                "person_id": {PERIOD: person_id},
                "is_tax_unit_spouse": {PERIOD: False},
                "medicaid_magi_person": {PERIOD: magi},
                "medicaid_household_income_member": {PERIOD: member_income},
                "medicaid_person_is_required_to_file": {PERIOD: must_file},
                "current_pregnancies": {PERIOD: scenario["pregnancies"][person_id - 1]},
            }
        if with_ids:
            people[child]["parent_1_id"] = {PERIOD: 1}
        parent_unit_id = id_offset + 10 * s + 1

        # The parent's return, and the child's own unit under a known claim.
        parent_return = [parent]
        if scenario["known_claim"]:
            people[child]["claimed_as_dependent_on_another_return"] = {PERIOD: True}
            people[child]["medicaid_claiming_tax_unit_id"] = {PERIOD: parent_unit_id}
            tax_units[f"{name}_child_unit"] = {
                "members": [child],
                "tax_unit_id": {PERIOD: id_offset + 10 * s + 2},
                "tax_unit_is_filer": {PERIOD: False},
            }
        else:
            parent_return.append(child)
        if placement == "same_return":
            parent_return.append(spouse)
        else:
            tax_units[f"{name}_spouse_unit"] = {
                "members": [spouse],
                "tax_unit_id": {PERIOD: id_offset + 10 * s + 3},
                "tax_unit_is_filer": {PERIOD: True},
                "cohabitating_spouses": {PERIOD: placement == "flagged"},
            }
        if placement == "claimed_into":
            people[spouse]["claimed_as_dependent_on_another_return"] = {PERIOD: True}
            people[spouse]["medicaid_claiming_tax_unit_id"] = {PERIOD: parent_unit_id}
        tax_units[f"{name}_parent_unit"] = {
            "members": ordered(parent_return),
            "tax_unit_id": {PERIOD: parent_unit_id},
            "tax_unit_is_filer": {PERIOD: True},
        }

        # Homes and families.
        couple_home = [child] + ([spouse] if placement != "elsewhere" else [])
        couple_family = [child] + ([spouse] if placement in IN_CHILDS_FAMILY else [])
        if scenario["child_with_parent"]:
            homes = [[parent] + couple_home]
            family_groups = [[parent] + couple_family]
        else:
            homes = [[parent], couple_home]
            family_groups = [[parent], couple_family]
        if placement == "elsewhere":
            homes.append([spouse])
        if placement not in IN_CHILDS_FAMILY:
            family_groups.append([spouse])
        for k, members in enumerate(homes):
            households[f"{name}_home{k}"] = {
                "members": ordered(members),
                "state_code": {PERIOD: "CA"},
            }
        for k, members in enumerate(family_groups):
            families[f"{name}_family{k}"] = {"members": ordered(members)}
        if placement == "unmarried":
            marital_units[f"{name}_child"] = {"members": [child]}
            marital_units[f"{name}_spouse"] = {"members": [spouse]}
        else:
            marital_units[f"{name}_couple"] = {"members": ordered([child, spouse])}
        marital_units[f"{name}_parent"] = {"members": [parent]}
    return {
        "people": people,
        "households": households,
        "families": families,
        "tax_units": tax_units,
        "spm_units": {k: {"members": v["members"]} for k, v in households.items()},
        "marital_units": marital_units,
    }


def expected_tax_households(scenario):
    """Members of the parent's and the child's households, by role."""
    placement = scenario["placement"]
    # 42 CFR 435.603(f)(1)-(2): the parent's return and whoever it claims
    # from elsewhere form the parent's household, which the claimed child's
    # household copies.
    parent_household = {"parent", "child"}
    if placement in ("same_return", "claimed_into"):
        parent_household.add("spouse")
    # (f)(4): a co-resident spouse joins the child's household, once.
    child_household = set(parent_household)
    if placement in ("flagged", "same_family"):
        child_household.add("spouse")
    return parent_household, child_household


def test_tax_dependent_counts_a_co_resident_spouse_exactly_once():
    scenarios = random_married_dependents(seed=435604)
    simulation = Simulation(situation=married_dependent_situation(scenarios))
    non_filer = by_name(simulation, "medicaid_uses_non_filer_rules")
    size = by_name(simulation, "medicaid_household_size")
    income = by_name(simulation, "medicaid_household_income")
    pregnancies = by_name(simulation, "ca_medicaid_household_pregnancies")
    placements = {scenario["placement"] for scenario in scenarios}
    assert placements == set(SPOUSE_PLACEMENTS)
    for s, scenario in enumerate(scenarios):
        roles = {"parent": 0, "child": 1, "spouse": 2}
        preg = {role: scenario["pregnancies"][k] for role, k in roles.items()}
        spouse_is_dependent = scenario["placement"] in ("same_return", "claimed_into")
        # (d)(2): a dependent who need not file adds no income to the
        # claiming taxpayer's household; the spouse the child adds under
        # (f)(4) counts with its countable income.
        tax_income = {
            "parent": scenario["parent_income"],
            "child": 0.0,
            "spouse": 0.0
            if spouse_is_dependent and not scenario["spouse_must_file"]
            else scenario["spouse_income"],
        }
        spouse_member_income = scenario["spouse_income"] * (
            scenario["spouse_must_file"] or scenario["spouse_age"] >= AGE_LIMIT
        )
        parent_household, child_household = expected_tax_households(scenario)
        for role, members in [("parent", parent_household), ("child", child_household)]:
            name = f"s{s}_{role}"
            assert not non_filer[name], name
            expected_pregnancies = sum(preg[m] for m in members)
            assert pregnancies[name] == expected_pregnancies, name
            # California counts each member's unborn children in the size.
            assert size[name] == len(members) + expected_pregnancies, name
            expected_income = sum(tax_income[m] for m in parent_household)
            if members != parent_household:
                expected_income += spouse_member_income
            assert income[name] == np.float32(expected_income), name

        # The spouse's own household holds the child exactly once whenever
        # they live together as spouses, with or without the flag ((f)(4)).
        name = f"s{s}_spouse"
        placement = scenario["placement"]
        lives_with_child = placement not in ("unmarried", "elsewhere")
        if spouse_is_dependent and not non_filer[name]:
            # Claimed into the parent's return: the parent's tax household,
            # which already holds the child.
            members = parent_household
            expected_income = sum(tax_income[m] for m in parent_household)
        else:
            # Files alone, or a dependent under (f)(2)(i)'s non-filer rules.
            assert spouse_is_dependent or not non_filer[name], name
            members = {"spouse", "child"} if lives_with_child else {"spouse"}
            expected_income = (
                spouse_member_income if non_filer[name] else scenario["spouse_income"]
            )
        expected_pregnancies = sum(preg[m] for m in members)
        assert pregnancies[name] == expected_pregnancies, name
        assert size[name] == len(members) + expected_pregnancies, name
        assert income[name] == np.float32(expected_income), name

    # Member order within every group does not change any result.
    reversed_ = Simulation(
        situation=married_dependent_situation(scenarios, reverse=True)
    )
    for variable in [
        "medicaid_household_size",
        "medicaid_household_income",
        "ca_medicaid_household_pregnancies",
    ]:
        assert by_name(simulation, variable) == by_name(reversed_, variable), variable


def test_households_without_ids_keep_their_values_next_to_linked_ones():
    # The same scenarios without ids give the same values whether or not the
    # simulation also holds linked households: the tax-dependent spouse rule
    # applies only in households with links.
    scenarios = random_married_dependents(seed=435605)
    alone = Simulation(
        situation=married_dependent_situation(scenarios, with_ids=False, prefix="z")
    )
    linked = married_dependent_situation(scenarios)
    unlinked = married_dependent_situation(scenarios, with_ids=False, prefix="z")
    mixed = Simulation(
        situation={key: {**linked[key], **unlinked[key]} for key in linked}
    )
    for variable in [
        "medicaid_uses_non_filer_rules",
        "medicaid_household_size",
        "medicaid_household_income",
        "ca_medicaid_household_pregnancies",
    ]:
        in_mixed = by_name(mixed, variable)
        for name, value in by_name(alone, variable).items():
            assert in_mixed[name] == value, (variable, name)


# Who claims: a named parent counts only as the claiming return's head or spouse.

NAMED_ROLES = ["head", "spouse", "dependent", "outside"]


def named_parent_situation(role, known_claim, co_resident):
    """A child whose id names X, claimed by a return in which X has ``role``.

    The claiming return is headed by X or by H. ``outside`` puts X on a return
    of their own. The child is on the claiming return, or under a known
    claiming tax unit, on a return of their own. X lives with the child or
    elsewhere; H lives with X.
    """
    x_age = 17 if role == "dependent" else 40
    people = {
        "x": {"person_id": {PERIOD: 1}, "age": {PERIOD: x_age}},
        "h": {"person_id": {PERIOD: 5}, "age": {PERIOD: 60}},
        "child": {
            "person_id": {PERIOD: 2},
            "age": {PERIOD: 1},
            "parent_1_id": {PERIOD: 1},
        },
    }
    claiming = {
        "head": ["x"],
        "spouse": ["h", "x"],
        "dependent": ["h", "x"],
        "outside": ["h"],
    }[role]
    tax_units = {"claiming": {"members": claiming, "tax_unit_id": {PERIOD: 1}}}
    if role == "spouse":
        tax_units["claiming"]["filing_status"] = {PERIOD: "JOINT"}
    if role == "dependent":
        people["x"]["is_tax_unit_spouse"] = {PERIOD: False}
    if role == "outside":
        tax_units["x_unit"] = {"members": ["x"], "tax_unit_id": {PERIOD: 3}}
    if role == "head":
        tax_units["h_unit"] = {"members": ["h"], "tax_unit_id": {PERIOD: 4}}
    if known_claim:
        people["child"]["medicaid_claiming_tax_unit_id"] = {PERIOD: 1}
        tax_units["child_unit"] = {"members": ["child"], "tax_unit_id": {PERIOD: 2}}
    else:
        tax_units["claiming"]["members"].append("child")
    for unit in tax_units.values():
        unit["tax_unit_is_filer"] = {PERIOD: True}
    homes = (
        {"home": ["x", "h", "child"]}
        if co_resident
        else {"adult_home": ["x", "h"], "child_home": ["child"]}
    )
    marital_units = {name: {"members": [name]} for name in people}
    if role == "spouse":
        marital_units = {
            "couple": {"members": ["h", "x"]},
            "child": {"members": ["child"]},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "families": {k: {"members": v} for k, v in homes.items()},
        "spm_units": {k: {"members": v} for k, v in homes.items()},
        "marital_units": marital_units,
        "households": {
            k: {"members": v, "state_code": {PERIOD: "OH"}} for k, v in homes.items()
        },
    }


def test_named_parent_must_be_claiming_head_or_spouse():
    # 42 CFR 435.603(f)(2)(i): the exception turns on whether the taxpayer
    # claiming the person is a parent. A named parent who is another
    # dependent on that return (a teen parent claimed by a grandparent) or
    # who files elsewhere is not the claiming taxpayer.
    for role in NAMED_ROLES:
        for known_claim in (False, True):
            for co_resident in (False, True):
                case = (role, known_claim, co_resident)
                simulation = Simulation(
                    situation=named_parent_situation(*case)
                )
                claimed = by_name(simulation, "medicaid_claimed_by_parent_in_tax_unit")
                other = by_name(
                    simulation,
                    "medicaid_tax_dependent_exception_other_than_spouse_or_child",
                )
                expected = role in ("head", "spouse")
                assert claimed["child"] == expected, case
                if not known_claim:
                    assert other["child"] == (not expected), case


# Both parents: (f)(2)(ii) needs two co-resident parents, a parent's claim and
# no joint return between those two parents.

BOTH_PARENT_CASES = {
    # arrangement: whether (f)(2)(ii) applies
    "joint_filer": False,
    "joint_non_filer": True,
    "separate_filers": True,
    "two_joint_returns": True,
    "claimed_by_parent_elsewhere": True,
    "claimed_by_grandparent_elsewhere": False,
}


def both_parent_situation(arrangement):
    """A child whose ids name a mother and father who both live with them."""
    people = {
        "mother": {"person_id": {PERIOD: 1}, "age": {PERIOD: 38}},
        "father": {"person_id": {PERIOD: 2}, "age": {PERIOD: 40}},
        "child": {
            "person_id": {PERIOD: 3},
            "age": {PERIOD: 10},
            "parent_1_id": {PERIOD: 1},
            "parent_2_id": {PERIOD: 2},
        },
    }
    home = ["mother", "father", "child"]
    other_homes = {}
    marital_units = {name: {"members": [name]} for name in people}
    if arrangement in ("joint_filer", "joint_non_filer"):
        tax_units = {
            "unit": {
                "members": ["mother", "father", "child"],
                "filing_status": {PERIOD: "JOINT"},
                "tax_unit_is_filer": {PERIOD: arrangement == "joint_filer"},
            }
        }
        marital_units = {
            "couple": {"members": ["mother", "father"]},
            "child": {"members": ["child"]},
        }
    elif arrangement == "two_joint_returns":
        # Each parent files jointly with someone else: the mother as head with
        # her husband, the father as spouse of his wife.
        people["husband"] = {"person_id": {PERIOD: 4}, "age": {PERIOD: 39}}
        people["wife"] = {"person_id": {PERIOD: 5}, "age": {PERIOD: 45}}
        home += ["husband", "wife"]
        tax_units = {
            "mother_unit": {
                "members": ["mother", "husband", "child"],
                "filing_status": {PERIOD: "JOINT"},
                "tax_unit_is_filer": {PERIOD: True},
            },
            "father_unit": {
                "members": ["wife", "father"],
                "filing_status": {PERIOD: "JOINT"},
                "tax_unit_is_filer": {PERIOD: True},
            },
        }
        marital_units = {
            "mother_couple": {"members": ["mother", "husband"]},
            "father_couple": {"members": ["wife", "father"]},
            "child": {"members": ["child"]},
        }
    else:
        tax_units = {
            "mother_unit": {"members": ["mother"], "tax_unit_id": {PERIOD: 1}},
            "father_unit": {"members": ["father"], "tax_unit_id": {PERIOD: 2}},
        }
        if arrangement == "separate_filers":
            tax_units["mother_unit"]["members"].append("child")
        else:
            claimant = 1
            if arrangement == "claimed_by_grandparent_elsewhere":
                people["grandparent"] = {"person_id": {PERIOD: 6}, "age": {PERIOD: 65}}
                other_homes["grandparent_home"] = ["grandparent"]
                tax_units["grandparent_unit"] = {
                    "members": ["grandparent"],
                    "tax_unit_id": {PERIOD: 6},
                }
                marital_units["grandparent"] = {"members": ["grandparent"]}
                claimant = 6
            # A dependent on the mother's return, claimed by a known unit.
            tax_units["mother_unit"]["members"].append("child")
            people["child"]["medicaid_claiming_tax_unit_id"] = {PERIOD: claimant}
            if arrangement == "claimed_by_parent_elsewhere":
                # The child's own return, claimed by the mother's unit.
                tax_units["mother_unit"]["members"].remove("child")
                tax_units["child_unit"] = {
                    "members": ["child"],
                    "tax_unit_id": {PERIOD: 3},
                }
        for unit in tax_units.values():
            unit["tax_unit_is_filer"] = {PERIOD: True}
    homes = {"home": home, **other_homes}
    return {
        "people": people,
        "tax_units": tax_units,
        "families": {k: {"members": v} for k, v in homes.items()},
        "spm_units": {k: {"members": v} for k, v in homes.items()},
        "marital_units": marital_units,
        "households": {
            k: {"members": v, "state_code": {PERIOD: "OH"}} for k, v in homes.items()
        },
    }


def test_both_parent_joint_return_requires_same_filing_unit():
    # Parents "do not expect to file a joint tax return" unless they are the
    # head and spouse of one return that is filed; a known claiming unit must
    # have a co-resident parent as its head or spouse.
    for arrangement, expected in BOTH_PARENT_CASES.items():
        simulation = Simulation(situation=both_parent_situation(arrangement))
        both = by_name(
            simulation, "medicaid_tax_dependent_exception_living_with_both_parents"
        )
        non_filer = by_name(simulation, "medicaid_uses_non_filer_rules")
        assert both["child"] == expected, arrangement
        assert not both["mother"] and not both["father"], arrangement
        if expected:
            assert non_filer["child"], arrangement
        # The same household with the parents' ids swapped between slots.
        swapped = both_parent_situation(arrangement)
        swapped["people"]["child"]["parent_1_id"] = {PERIOD: 2}
        swapped["people"]["child"]["parent_2_id"] = {PERIOD: 1}
        swapped_both = by_name(
            Simulation(situation=swapped),
            "medicaid_tax_dependent_exception_living_with_both_parents",
        )
        assert swapped_both["child"] == expected, arrangement
