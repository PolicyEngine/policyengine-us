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
