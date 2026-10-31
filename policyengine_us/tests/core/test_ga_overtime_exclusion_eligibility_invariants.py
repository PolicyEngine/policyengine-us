"""Invariants for who qualifies for Georgia's overtime exclusion.

O.C.G.A. § 48-7-27(a)(16)(A) subtracts, for tax years 2026 through 2028, "any
amount of qualified overtime compensation, as such term is defined in Section
225 of the Internal Revenue Code, up to $1,750.00 received by a full-time
employee paid by an hourly wage". (16)(B) continues: "Notwithstanding
subparagraph (A) of this paragraph, for employers governed by the federal
National Railway Labor Act, the exemption provided in this paragraph shall
apply to hourly component overtime compensation as defined in applicable
collective bargaining agreements."

Hypothesis draws batches of Georgia tax units (single, joint, and either with
dependents), and a seeded population of 300 units adds breadth. Each person
gets an hourly flag, usual weekly hours on both sides of the 35-hour line,
overtime premiums and Railway Labor Act overtime, some above the cap. Each
batch runs as vectorized simulations with one input changed at a time. For
every tax unit:

1. Differential: the exclusion equals an independent numpy sum, over the head
   and spouse who work at least 35 hours, of min(premium if hourly, plus
   Railway Labor Act overtime, $1,750), with both constants restated from the
   law rather than read from the parameter files.
2. No leakage: zeroing the premium of everyone who fails either test and the
   Railway Labor Act overtime of everyone under 35 hours leaves the exclusion,
   Georgia subtractions and Georgia AGI unchanged.
3. Monotonicity: paying everyone hourly, raising hours, raising the premium or
   raising Railway Labor Act overtime never lowers the exclusion.
4. Railway Labor Act overtime needs no hourly wage: with no premium, changing
   the hourly flag leaves the exclusion unchanged.
5. Bounds: the exclusion lies between 0 and $1,750 times the number of filers.
6. Flow: a change in the exclusion moves Georgia subtractions by the same
   amount and Georgia AGI by the opposite amount.
7. The cash tip exclusion, which has neither test, ignores hourly pay, hours
   and Railway Labor Act overtime.
8. A person paid hourly always passes is_eligible_for_fsla_overtime, so the
   exclusion gains nothing from reading it.

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
TIPPED_CODE = 102

OUTPUTS = [
    "ga_cash_tip_exclusion",
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
    tip_income = draw(st.one_of(st.just(0.0), st.integers(1, 4_000).map(float)))
    return {
        "employment_income": (
            float(draw(st.integers(0, 60_000))) + premium + rla_overtime + tip_income
        ),
        "is_paid_hourly": draw(st.booleans()),
        "weekly_hours_worked_before_lsr": draw(st.sampled_from(HOURS)),
        "fsla_overtime_premium": premium,
        "ga_rla_hourly_component_overtime": rla_overtime,
        "tip_income": tip_income,
        "treasury_tipped_occupation_code": TIPPED_CODE,
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
    tip_income = some(1, 4_000, 0.3)
    return {
        "employment_income": (
            some(1, 60_000, 0.8) + premium + rla_overtime + tip_income
        ),
        "is_paid_hourly": bool(rng.random() < 0.6),
        "weekly_hours_worked_before_lsr": float(rng.choice(HOURS)),
        "fsla_overtime_premium": premium,
        "ga_rla_hourly_component_overtime": rla_overtime,
        "tip_income": tip_income,
        "treasury_tipped_occupation_code": TIPPED_CODE,
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
    out["fsla_eligible"] = np.asarray(
        sim.calculate("is_eligible_for_fsla_overtime", year), dtype=bool
    )
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_sum(run, values):
    return np.bincount(
        run["unit"],
        weights=values,
        minlength=len(run["ga_qualified_overtime_exclusion"]),
    )


def _without_failing_amounts(amounts):
    full_time = amounts["weekly_hours_worked_before_lsr"] >= FULL_TIME_HOURS
    return {
        **amounts,
        "fsla_overtime_premium": (
            amounts["fsla_overtime_premium"]
            if full_time and amounts["is_paid_hourly"]
            else 0.0
        ),
        "ga_rla_hourly_component_overtime": (
            amounts["ga_rla_hourly_component_overtime"] if full_time else 0.0
        ),
    }


def _expected(run):
    full_time = run["weekly_hours_worked_before_lsr"] >= FULL_TIME_HOURS
    counted = (
        run["fsla_overtime_premium"] * run["hourly"]
        + run["ga_rla_hourly_component_overtime"]
    )
    return _unit_sum(run, run["filer"] * full_time * np.minimum(counted, CAP))


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

    # 4. Railway Labor Act overtime needs no hourly wage.
    rla_hourly = _run(
        units,
        year,
        lambda a: {**a, "fsla_overtime_premium": 0.0, "is_paid_hourly": True},
    )
    rla_salaried = _run(
        units,
        year,
        lambda a: {**a, "fsla_overtime_premium": 0.0, "is_paid_hourly": False},
    )
    np.testing.assert_allclose(
        rla_hourly[exclusion], rla_salaried[exclusion], atol=TOLERANCE
    )

    # 5. Bounds: 0 to $1,750 per filer.
    filers = _unit_sum(base, base["filer"].astype(float))
    assert (base[exclusion] >= -TOLERANCE).all()
    assert (base[exclusion] <= CAP * filers + TOLERANCE).all()

    # 6. The exclusion flows dollar for dollar.
    change = all_hourly[exclusion] - base[exclusion]
    np.testing.assert_allclose(
        all_hourly["ga_subtractions"] - base["ga_subtractions"],
        change,
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        all_hourly["ga_agi"] - base["ga_agi"], -change, atol=TOLERANCE
    )

    # 7. The tip exclusion has neither test.
    for other in (all_hourly, more_hours, more_rla, rla_salaried):
        np.testing.assert_allclose(
            other["ga_cash_tip_exclusion"],
            base["ga_cash_tip_exclusion"],
            atol=TOLERANCE,
        )

    # 8. Reading is_eligible_for_fsla_overtime would add nothing.
    assert base["fsla_eligible"][base["hourly"]].all()

    if require_failing_premiums:
        full_time = base["weekly_hours_worked_before_lsr"] >= FULL_TIME_HOURS
        has_premium = base["filer"] & (base["fsla_overtime_premium"] > 0)
        has_rla = base["filer"] & (base["ga_rla_hourly_component_overtime"] > 0)
        assert (has_premium & base["hourly"] & ~full_time).sum() >= 10
        assert (has_premium & ~base["hourly"] & full_time).sum() >= 10
        assert (has_premium & base["hourly"] & full_time).sum() >= 10
        assert (has_rla & ~base["hourly"] & full_time).sum() >= 10
        assert (has_rla & ~full_time).sum() >= 10
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


@pytest.mark.parametrize(
    "hours,counted",
    [(34.99, False), (35, True), (35.01, True)],
)
def test_full_time_threshold_edge(hours, counted):
    amounts = {
        "age": 40,
        "employment_income": 50_000.0,
        "is_paid_hourly": True,
        "weekly_hours_worked_before_lsr": hours,
        "fsla_overtime_premium": 1_000.0,
        "ga_rla_hourly_component_overtime": 0.0,
        "tip_income": 0.0,
        "treasury_tipped_occupation_code": TIPPED_CODE,
    }
    run = _run([{"head": amounts, "spouse": None, "dependents": []}], 2026)
    assert run["ga_qualified_overtime_exclusion"][0] == (1_000 if counted else 0)
