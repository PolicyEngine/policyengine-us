"""Invariants for the inferred tax unit spouse when members are separated.

Separation under 26 U.S.C. 7703 concerns the filer's own marriage, so only
the head's or the would-be spouse's `is_separated` can leave a tax unit
without a spouse. The would-be spouse is the oldest head-or-spouse candidate
other than the head; candidates are adults not input as dependents (every
adult when all are). Core's `get_rank` puts equal ages in member order.

Hypothesis draws batches of tax units of one to five people, with tied ages,
children, separated members and, in turn, no role inputs, input dependent
flags, or an input head. A seeded population of 300 units adds breadth. Each
batch runs as one vectorized simulation that also holds a twin of every unit
in which every member other than the head and the would-be spouse has
`is_separated` flipped. For every tax unit:

1. Structure: at most one spouse, who is neither the head nor a child.
2. Differential: head and spouse equal a pure-Python statement of the rule.
3. Separation of anyone but the head and the would-be spouse never changes
   the spouse: each unit and its twin get the same spouse.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2024
ADULT_AGE = 18
AGES = [6, 17, 18, 25, 30, 38, 40, 75]
MODES = ["no_roles", "dependents", "head"]


@st.composite
def tax_units(draw):
    size = draw(st.integers(1, 5))
    members = [
        {
            "age": draw(st.sampled_from(AGES)),
            "separated": draw(st.booleans()),
            "dependent": draw(st.booleans()),
        }
        for _ in range(size)
    ]
    return {"members": members, "head": draw(st.integers(0, size - 1))}


def _seeded_units(n=300, seed=20261006):
    rng = np.random.default_rng(seed)
    units = []
    for _ in range(n):
        size = int(rng.integers(1, 6))
        members = [
            {
                "age": int(rng.choice(AGES)),
                "separated": bool(rng.random() < 0.3),
                "dependent": bool(rng.random() < 0.4),
            }
            for _ in range(size)
        ]
        units.append({"members": members, "head": int(rng.integers(0, size))})
    return units


def _first_oldest(ages, eligible):
    """Index of the oldest eligible member, the earlier one on a tie."""
    order = [i for i in range(len(ages)) if eligible[i]]
    return min(order, key=lambda i: (-ages[i], i)) if order else None


def _reference(unit, mode):
    """(head index, spouse index) under the rule in the module docstring."""
    members = unit["members"]
    ages = [m["age"] for m in members]
    adult = [age >= ADULT_AGE for age in ages]
    candidate = adult
    if mode != "no_roles":
        non_dependent = [a and not m["dependent"] for a, m in zip(adult, members)]
        if any(non_dependent):
            candidate = non_dependent
    if mode == "head":
        head = unit["head"]
    else:
        head = _first_oldest(ages, candidate)
    would_be = _first_oldest(ages, [c and i != head for i, c in enumerate(candidate)])
    separated = [m["separated"] for m in members]
    if would_be is None or (head is not None and separated[head]):
        return head, None
    return head, None if separated[would_be] else would_be


def _twin(unit, mode):
    """The unit with every member but the head and would-be spouse's
    separation flipped."""
    members = unit["members"]
    head, _ = _reference(unit, mode)
    keep = {head}
    # The would-be spouse is the spouse the rule finds when nobody is separated.
    calm = {**unit, "members": [{**m, "separated": False} for m in members]}
    keep.add(_reference(calm, mode)[1])
    flipped = [
        m if i in keep else {**m, "separated": not m["separated"]}
        for i, m in enumerate(members)
    ]
    return {**unit, "members": flipped}


def _situation(units, mode):
    people, tax_unit_groups, households, marital_units = {}, {}, {}, {}
    for u, unit in enumerate(units):
        names = []
        for i, member in enumerate(unit["members"]):
            name = f"p{u}_{i}"
            person = {
                "age": {YEAR: member["age"]},
                "is_separated": {YEAR: member["separated"]},
            }
            if mode in ("dependents", "head"):
                person["is_tax_unit_dependent"] = {YEAR: member["dependent"]}
            if mode == "head":
                person["is_tax_unit_head"] = {YEAR: i == unit["head"]}
            people[name] = person
            names.append(name)
            marital_units[f"m{u}_{i}"] = {"members": [name]}
        tax_unit_groups[f"t{u}"] = {"members": names}
        households[f"h{u}"] = {"members": names, "state_code": {YEAR: "TX"}}
    return {
        "people": people,
        "tax_units": tax_unit_groups,
        "households": households,
        "marital_units": marital_units,
    }


def _check(units, mode):
    batch = units + [_twin(unit, mode) for unit in units]
    sim = Simulation(situation=_situation(batch, mode))
    head = np.asarray(sim.calculate("is_tax_unit_head", YEAR), dtype=bool)
    spouse = np.asarray(sim.calculate("is_tax_unit_spouse", YEAR), dtype=bool)
    start = 0
    spouses = []
    for u, unit in enumerate(batch):
        size = len(unit["members"])
        unit_head = head[start : start + size]
        unit_spouse = spouse[start : start + size]
        ages = [m["age"] for m in unit["members"]]
        start += size

        # 1. Structure.
        assert unit_spouse.sum() <= 1, (mode, unit)
        assert not (unit_spouse & unit_head).any(), (mode, unit)
        assert all(age >= ADULT_AGE for age, s in zip(ages, unit_spouse) if s)

        # 2. Differential against the reference rule.
        expected_head, expected_spouse = _reference(unit, mode)
        assert list(np.flatnonzero(unit_head)) == (
            [] if expected_head is None else [expected_head]
        ), (mode, unit, unit_head)
        assert list(np.flatnonzero(unit_spouse)) == (
            [] if expected_spouse is None else [expected_spouse]
        ), (mode, unit, unit_spouse)
        spouses.append(list(np.flatnonzero(unit_spouse)))

    # 3. Each unit and its twin share a spouse.
    assert spouses[: len(units)] == spouses[len(units) :]


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=10,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.sampled_from(MODES), st.lists(tax_units(), min_size=5, max_size=40))
def test_tax_unit_spouse_separation_invariants(mode, units):
    _check(units, mode)


@pytest.mark.parametrize("mode", MODES)
def test_seeded_population(mode):
    _check(_seeded_units(), mode)
