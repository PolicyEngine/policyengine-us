"""Filing status and the filing requirement for a filer who can be claimed as
a dependent on another return (`claimed_as_dependent_on_another_return`).

A taxpayer who can be claimed is treated as having no dependents (IRC
152(b)(1)). Head of household status through a qualifying child (IRC
2(b)(1)(A)(i)) and surviving spouse status (IRC 2(a)(1)(B), "without regard
to subsections (b)(1)") remain open to them; the qualifying relative and
parent routes (IRC 2(b)(1)(A)(ii), (B)) and the considered-unmarried route
(IRC 7703(b)(1)) do not. Such a filer must file when their own unearned
income exceeds the dependent standard deduction floor (IRC
6012(a)(1)(C)(i)(I), 6012(f)(2)(D)); a filer who cannot be claimed is held
only to the gross income test.

Hypothesis draws batches of unmarried filers, some separated or widowed, with
up to two dependents of any age, and married couples, for 2021-2026. A
seeded population checks the same in every year. Each batch is one
vectorized simulation. Invariants:

1. Swap invariance: exchanging a couple's head and spouse labels leaves
   `tax_unit_is_required_to_file` and `filing_status` unchanged, whichever
   spouses are claimed.
2. Monotonicity: marking a filer as claimable never turns
   `head_of_household_eligible` on or `tax_unit_is_required_to_file` off.
3. The qualifying child route: an unmarried, unseparated filer with a
   dependent who meets the qualifying child age test (or is permanently
   disabled) has the same head of household eligibility whether or not they
   can be claimed.
4. `surviving_spouse_eligible` does not depend on whether the filer can be
   claimed.
5. When no filer can be claimed, `tax_unit_is_required_to_file` equals the
   gross income test: gross income above the standard deduction, or above
   zero on a separate return (Chart A).
6. When every filer can be claimed, a unit is eligible for head of household
   only through invariant 3's route: never through a qualifying relative or
   parent alone, and never when separated.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
SEED = 20261009


def money(high):
    return st.one_of(st.just(0.0), st.integers(1, high).map(float))


@st.composite
def adults(draw):
    return {
        "age": draw(st.integers(17, 80)),
        "is_blind": draw(st.booleans()),
        "employment_income": draw(money(40_000)),
        "self_employment_income": draw(st.integers(-5_000, 10_000).map(float)),
        "taxable_interest_income": draw(money(6_000)),
        "dividend_income": draw(money(6_000)),
        "social_security_retirement": draw(money(20_000)),
    }


@st.composite
def dependents(draw):
    return {
        "age": draw(st.integers(0, 80)),
        "is_full_time_student": draw(st.booleans()),
        "is_permanently_and_totally_disabled": draw(st.booleans()),
        "is_related_to_head_or_spouse": draw(st.booleans()),
        "employment_income": draw(money(8_000)),
    }


@st.composite
def units(draw):
    married = draw(st.booleans())
    return {
        "married": married,
        "adults": [draw(adults()) for _ in range(2 if married else 1)],
        "separated": (not married) and draw(st.booleans()),
        "widowed": (not married) and draw(st.booleans()),
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": tuple(draw(st.booleans()) for _ in range(2 if married else 1)),
    }


def _seeded_units(count):
    rng = np.random.default_rng(SEED)

    def some(high, p):
        return float(round(rng.uniform(1, high))) if rng.random() < p else 0.0

    def adult():
        return {
            "age": int(rng.integers(17, 81)),
            "is_blind": bool(rng.random() < 0.1),
            "employment_income": some(40_000, 0.6),
            "self_employment_income": some(10_000, 0.15),
            "taxable_interest_income": some(6_000, 0.4),
            "dividend_income": some(6_000, 0.3),
            "social_security_retirement": some(20_000, 0.2),
        }

    def dependent():
        return {
            "age": int(rng.integers(0, 81)),
            "is_full_time_student": bool(rng.random() < 0.3),
            "is_permanently_and_totally_disabled": bool(rng.random() < 0.1),
            "is_related_to_head_or_spouse": bool(rng.random() < 0.8),
            "employment_income": some(8_000, 0.3),
        }

    result = []
    for _ in range(count):
        married = bool(rng.random() < 0.4)
        result.append(
            {
                "married": married,
                "adults": [adult() for _ in range(2 if married else 1)],
                "separated": (not married) and bool(rng.random() < 0.25),
                "widowed": (not married) and bool(rng.random() < 0.15),
                "dependents": [dependent() for _ in range(int(rng.integers(0, 3)))],
                "claimed": tuple(
                    bool(rng.random() < 0.5) for _ in range(2 if married else 1)
                ),
            }
        )
    return result


def _situation(units, year, variants):
    # Each unit appears once per variant: (first adult is head, claimed flags
    # by adult). People keep their order and every other input in each copy.
    people, groups = {}, {"tax_units": {}, "marital_units": {}, "households": {}}
    for i, unit in enumerate(units):
        for copy, (first_is_head, claimed) in enumerate(variants(unit)):
            names = [f"adult_{i}_{copy}_{k}" for k in range(len(unit["adults"]))]
            for k, (name, amounts) in enumerate(zip(names, unit["adults"])):
                is_head = (k == 0) == first_is_head
                people[name] = {
                    **amounts,
                    "is_tax_unit_head": is_head,
                    "is_tax_unit_spouse": not is_head,
                    "is_tax_unit_dependent": False,
                    "is_separated": unit["separated"],
                    "is_surviving_spouse": unit["widowed"],
                    "claimed_as_dependent_on_another_return": claimed[k],
                }
            groups["marital_units"][f"filers_{i}_{copy}"] = {"members": list(names)}
            members = list(names)
            for j, amounts in enumerate(unit["dependents"]):
                child = f"dependent_{i}_{copy}_{j}"
                people[child] = {
                    **amounts,
                    "is_tax_unit_head": False,
                    "is_tax_unit_spouse": False,
                    "is_tax_unit_dependent": True,
                }
                members.append(child)
                groups["marital_units"][f"single_{i}_{copy}_{j}"] = {"members": [child]}
            groups["tax_units"][f"tax_unit_{i}_{copy}"] = {"members": members}
            groups["households"][f"household_{i}_{copy}"] = {
                "members": members,
                "state_code": {year: "TX"},
            }
    people = {
        name: {key: {year: value} for key, value in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _variants(unit):
    # 0: as drawn; 1: labels exchanged (couples) or the same (others);
    # 2: nobody claimed; 3: every filer claimed.
    n = len(unit["adults"])
    return [
        (True, unit["claimed"]),
        (n == 1, unit["claimed"]),
        (True, (False,) * n),
        (True, (True,) * n),
    ]


def _calc(sim, name, year):
    return np.asarray(sim.calculate(name, year)).reshape(-1, 4)


def _describe(units, rows):
    return "; ".join(
        f"married={units[i]['married']} separated={units[i]['separated']} "
        f"widowed={units[i]['widowed']} claimed={units[i]['claimed']} "
        f"dependents={[d['age'] for d in units[i]['dependents']]}"
        for i in np.flatnonzero(rows)[:5]
    )


def _check(units, year):
    sim = Simulation(situation=_situation(units, year, _variants))
    required = _calc(sim, "tax_unit_is_required_to_file", year)
    status = _calc(sim, "filing_status", year)
    hoh = _calc(sim, "head_of_household_eligible", year)
    surviving = _calc(sim, "surviving_spouse_eligible", year)

    # 1. Swap invariance.
    for name, values in (("tax_unit_is_required_to_file", required), ("filing_status", status)):
        differs = values[:, 0] != values[:, 1]
        assert not differs.any(), (
            f"{name} in {year} changes when the head and spouse labels are "
            f"exchanged: {_describe(units, differs)}"
        )

    # 2. Monotonicity in claimability.
    hoh_gained = hoh[:, 3] & ~hoh[:, 2]
    assert not hoh_gained.any(), (
        f"head_of_household_eligible in {year} turns on when filers are "
        f"claimable: {_describe(units, hoh_gained)}"
    )
    requirement_lost = required[:, 2] & ~required[:, 3]
    assert not requirement_lost.any(), (
        f"tax_unit_is_required_to_file in {year} turns off when filers are "
        f"claimable: {_describe(units, requirement_lost)}"
    )

    # 3. The qualifying child route.
    child_route = np.array(
        [
            not u["married"]
            and not u["separated"]
            and any(
                d["is_permanently_and_totally_disabled"]
                or d["age"] < (24 if d["is_full_time_student"] else 19)
                for d in u["dependents"]
            )
            for u in units
        ]
    )
    child_route_lost = child_route & (hoh[:, 3] != hoh[:, 2])
    assert not child_route_lost.any(), (
        f"head_of_household_eligible in {year} through a qualifying child "
        f"depends on whether the filer can be claimed: "
        f"{_describe(units, child_route_lost)}"
    )
    # 6. A claimable filer qualifies only through that route.
    other_route = hoh[:, 3] & ~child_route
    assert not other_route.any(), (
        f"head_of_household_eligible in {year} for a claimable filer without "
        f"a qualifying child, or separated: {_describe(units, other_route)}"
    )

    # 4. Surviving spouse status.
    surviving_changes = surviving[:, 3] != surviving[:, 2]
    assert not surviving_changes.any(), (
        f"surviving_spouse_eligible in {year} depends on whether the filer "
        f"can be claimed: {_describe(units, surviving_changes)}"
    )

    # 5. Nobody claimable: the gross income test alone.
    gross_income = np.asarray(
        sim.calculate("irs_gross_income", year, map_to="tax_unit")
    ).reshape(-1, 4)[:, 2]
    standard_deduction = _calc(sim, "standard_deduction", year)[:, 2]
    separate = (
        np.asarray(sim.calculate("filing_status", year, decode_enums=True)).reshape(
            -1, 4
        )[:, 2]
        == "SEPARATE"
    )
    expected = gross_income > np.where(separate, 0, standard_deduction)
    mismatch = required[:, 2] != expected
    assert not mismatch.any(), (
        f"tax_unit_is_required_to_file in {year} differs from the gross "
        f"income test when nobody can be claimed: {_describe(units, mismatch)}"
    )


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(units(), min_size=10, max_size=25))
def test_claimable_filer_status_and_filing_invariants(year, drawn):
    _check(drawn, year)


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    _check(_seeded_units(60), year)
