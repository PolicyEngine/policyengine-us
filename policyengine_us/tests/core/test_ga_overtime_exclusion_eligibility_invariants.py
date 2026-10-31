"""Invariants for who qualifies for Georgia's overtime exclusion.

O.C.G.A. § 48-7-27(a)(16)(A) subtracts, for tax years 2026 through 2028, "any
amount of qualified overtime compensation, as such term is defined in Section
225 of the Internal Revenue Code, up to $1,750.00 received by a full-time
employee paid by an hourly wage". (16)(B) continues: "Notwithstanding
subparagraph (A) of this paragraph, for employers governed by the federal
National Railway Labor Act, the exemption provided in this paragraph shall
apply to hourly component overtime compensation as defined in applicable
collective bargaining agreements."

Each case below compares runs or sums a population, which a YAML case can't do.
The YAML file for the variable holds the worked examples.

Hypothesis draws batches of Georgia tax units (single, joint, and either with
dependents), and a seeded population of 300 units adds breadth. Each person
gets an hourly flag, usual weekly hours on both sides of the 35-hour line,
overtime premiums and Railway Labor Act overtime, some above the cap. Each
batch runs as vectorized simulations with one input changed at a time. For
every tax unit:

1. Differential: the exclusion equals an independent numpy sum, over the head
   and spouse who are paid hourly and work at least 35 hours, of min(premium
   plus Railway Labor Act overtime, $1,750), with both constants restated from
   the law rather than read from the parameter files.
2. No leakage: zeroing both overtime amounts of everyone who fails either test
   leaves the exclusion, Georgia subtractions and Georgia AGI unchanged.
3. Monotonicity: paying everyone hourly, raising hours, raising the premium or
   raising Railway Labor Act overtime never lowers the exclusion.
4. The two amounts are interchangeable: swapping each person's premium and
   Railway Labor Act overtime leaves the exclusion unchanged, since one limit
   and the same tests cover both.
5. Flow: a change in the exclusion moves Georgia subtractions by the same
   amount and Georgia AGI by the opposite amount.

Case 1 also bounds the exclusion between 0 and $1,750 times the number of
filers.

The seeded population also checks that each failing group holds amounts, so
1 and 2 are not vacuous.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
# O.C.G.A. § 48-7-27(a)(16)(A): "up to $1,750.00".
CAP = 1_750
# Chapter 7's job credits set full-time at "a minimum of 35 hours a week"
# (O.C.G.A. § 48-7-40(a)(5)).
FULL_TIME_HOURS = 35
HOURS = [0, 20, 34, 34.99, 35, 35.01, 40, 60]

OUTPUTS = [
    "ga_qualified_overtime_exclusion",
    "ga_subtractions",
    "ga_agi",
]
AMOUNTS = [
    "is_paid_hourly",
    "weekly_hours_worked_before_lsr",
    "fsla_overtime_premium",
    "ga_rla_hourly_component_overtime",
]

overtime = st.one_of(st.just(0.0), st.integers(1, 4_000).map(float))


@st.composite
def person_amounts(draw):
    premium = draw(overtime)
    rla_overtime = draw(st.one_of(st.just(0.0), overtime))
    return {
        "employment_income": (
            float(draw(st.integers(0, 60_000))) + premium + rla_overtime
        ),
        "is_paid_hourly": draw(st.booleans()),
        "weekly_hours_worked_before_lsr": draw(st.sampled_from(HOURS)),
        "fsla_overtime_premium": premium,
        "ga_rla_hourly_component_overtime": rla_overtime,
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "joint"]))
    n_dependents = draw(st.integers(0, 1))
    return {
        "head": {"age": draw(st.integers(25, 70)), **draw(person_amounts())},
        "spouse": (
            {"age": draw(st.integers(25, 70)), **draw(person_amounts())}
            if kind == "joint"
            else None
        ),
        "dependents": [
            {"age": draw(st.integers(14, 18)), **draw(person_amounts())}
            for _ in range(n_dependents)
        ],
    }


SEED = 20261031


def _seeded_amounts(rng):
    def some(low, high, p):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    premium = some(1, 4_000, 0.7)
    rla_overtime = some(1, 4_000, 0.25)
    return {
        "employment_income": some(1, 60_000, 0.8) + premium + rla_overtime,
        "is_paid_hourly": bool(rng.random() < 0.6),
        "weekly_hours_worked_before_lsr": float(rng.choice(HOURS)),
        "fsla_overtime_premium": premium,
        "ga_rla_hourly_component_overtime": rla_overtime,
    }


def _seeded_units(n=300):
    rng = np.random.default_rng(SEED)
    units = []
    for _ in range(n):
        joint = rng.random() < 0.5
        units.append(
            {
                "head": {"age": int(rng.integers(25, 71)), **_seeded_amounts(rng)},
                "spouse": (
                    {"age": int(rng.integers(25, 71)), **_seeded_amounts(rng)}
                    if joint
                    else None
                ),
                "dependents": [
                    {"age": int(rng.integers(14, 19)), **_seeded_amounts(rng)}
                    for _ in range(int(rng.integers(0, 2)))
                ],
            }
        )
    return units


def _situation(units, year, change):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {
            "is_tax_unit_head": True,
            "is_tax_unit_spouse": False,
            "is_tax_unit_dependent": False,
            **change(u["head"]),
        }
        members, couple = [head], [head]
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "is_tax_unit_head": False,
                "is_tax_unit_spouse": True,
                "is_tax_unit_dependent": False,
                **change(u["spouse"]),
            }
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, d in enumerate(u["dependents"]):
            child = f"dependent_{i}_{j}"
            people[child] = {
                "is_tax_unit_head": False,
                "is_tax_unit_spouse": False,
                "is_tax_unit_dependent": True,
                **change(d),
            }
            members.append(child)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [child]}
        groups["tax_units"][f"tax_unit_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "GA"},
        }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _run(units, year, change=lambda amounts: amounts):
    sim = Simulation(situation=_situation(units, year, change))
    out = {name: np.asarray(sim.calculate(name, year), dtype=float) for name in OUTPUTS}
    for name in AMOUNTS:
        out[name] = np.asarray(sim.calculate(name, year), dtype=float)
    out["hourly"] = out["is_paid_hourly"] > 0
    out["filer"] = ~np.asarray(sim.calculate("is_tax_unit_dependent", year), dtype=bool)
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_sum(run, values):
    return np.bincount(
        run["unit"],
        weights=values,
        minlength=len(run["ga_qualified_overtime_exclusion"]),
    )


def _without_failing_amounts(amounts):
    if (
        amounts["is_paid_hourly"]
        and amounts["weekly_hours_worked_before_lsr"] >= FULL_TIME_HOURS
    ):
        return amounts
    return {
        **amounts,
        "fsla_overtime_premium": 0.0,
        "ga_rla_hourly_component_overtime": 0.0,
    }


def _swap_overtime(amounts):
    return {
        **amounts,
        "fsla_overtime_premium": amounts["ga_rla_hourly_component_overtime"],
        "ga_rla_hourly_component_overtime": amounts["fsla_overtime_premium"],
    }


def _expected(run):
    passes = run["hourly"] & (run["weekly_hours_worked_before_lsr"] >= FULL_TIME_HOURS)
    counted = run["fsla_overtime_premium"] + run["ga_rla_hourly_component_overtime"]
    return _unit_sum(run, run["filer"] * passes * np.minimum(counted, CAP))


def _at_least(lower, higher, name):
    assert (higher[name] >= lower[name] - TOLERANCE).all(), name


def _check(units, year, *, require_failing_premiums=False):
    base = _run(units, year)
    exclusion = "ga_qualified_overtime_exclusion"

    # 1. Differential against numpy.
    np.testing.assert_allclose(base[exclusion], _expected(base), atol=TOLERANCE)

    # 2. An amount that fails its tests reaches nothing.
    no_failing_amounts = _run(units, year, _without_failing_amounts)
    for name in (exclusion, "ga_subtractions", "ga_agi"):
        np.testing.assert_allclose(
            base[name], no_failing_amounts[name], atol=TOLERANCE, err_msg=name
        )

    # 3. Monotonicity in each input.
    all_hourly = _run(units, year, lambda a: {**a, "is_paid_hourly": True})
    more_hours = _run(
        units,
        year,
        lambda a: {
            **a,
            "weekly_hours_worked_before_lsr": a["weekly_hours_worked_before_lsr"] + 5,
        },
    )
    more_premium = _run(
        units,
        year,
        lambda a: {
            **a,
            "fsla_overtime_premium": a["fsla_overtime_premium"] + 100,
        },
    )
    more_rla = _run(
        units,
        year,
        lambda a: {
            **a,
            "ga_rla_hourly_component_overtime": a["ga_rla_hourly_component_overtime"]
            + 100,
        },
    )
    for higher in (all_hourly, more_hours, more_premium, more_rla):
        _at_least(base, higher, exclusion)

    # 4. One limit and the same tests cover both amounts.
    swapped = _run(units, year, _swap_overtime)
    np.testing.assert_allclose(base[exclusion], swapped[exclusion], atol=TOLERANCE)

    # 5. The exclusion flows dollar for dollar.
    change = all_hourly[exclusion] - base[exclusion]
    np.testing.assert_allclose(
        all_hourly["ga_subtractions"] - base["ga_subtractions"],
        change,
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        all_hourly["ga_agi"] - base["ga_agi"], -change, atol=TOLERANCE
    )

    if require_failing_premiums:
        full_time = base["weekly_hours_worked_before_lsr"] >= FULL_TIME_HOURS
        for amount in ("fsla_overtime_premium", "ga_rla_hourly_component_overtime"):
            held = base["filer"] & (base[amount] > 0)
            assert (held & base["hourly"] & ~full_time).sum() >= 10, amount
            assert (held & ~base["hourly"] & full_time).sum() >= 10, amount
            assert (held & base["hourly"] & full_time).sum() >= 10, amount
        assert (change > 0).sum() >= 10


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=30))
def test_overtime_exclusion_eligibility_invariants(units):
    _check(units, 2026)


@pytest.mark.parametrize("year", [2026, 2028])
def test_seeded_population(year):
    _check(_seeded_units(), year, require_failing_premiums=True)
