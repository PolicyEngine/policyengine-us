"""Invariants for Colorado's state sales tax refund, C.R.S. 39-22-2003.

Subsection (2) allows the refund for a tax year only "if there were excess
state revenues for the fiscal year ending in that tax year". FY 2025-26 ended
below the Referendum C cap (State Controller certification of 2026-09-08), so
no tax year 2026 refund is paid. Tax year 2025 refunds come from the FY 2024-25
surplus, at the per-person tier amounts in the Legislative Council Staff March
2026 forecast, Table 8.

Hypothesis draws batches of tax units (single, joint, or head of household
with a dependent), each with a modified AGI, filer ages and wages; a seeded
population of 100 units adds breadth. Each batch runs as one vectorized
simulation per year. For every tax unit:

1. Gate: in 2026 the refund is zero, whatever the income, filing status or
   eligibility.
2. Differential: in 2025 the refund equals the number of eligible filers
   times the published tier amount for the unit's modified AGI, with the
   tiers taken from the forecast table rather than from the parameters.
3. Bounds: 0 <= refund <= 2 x the top tier amount, and the refund is
   positive exactly when a filer is eligible (2025).
4. Intended carry-forward: in 2027 the refund equals the 2025 refund. The
   LCS June 2026 forecast expects a tax year 2027 refund, and the 2025 tier
   amounts stand in until CDOR publishes the tax year 2027 table.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# LCS March 2026 forecast, Table 8, "Tax Year 2025 Refunds from FY 2024-25
# TABOR Refund Obligation", single filers: "up to $52,000" $19, "$52,001 to
# $105,000" $25, "$105,001 to $168,000" $29, "$168,001 to $233,000" $35,
# "$233,001 to $299,000" $37, "$299,001 and up" $59.
PUBLISHED_2025_STARTS = np.array([52_001, 105_001, 168_001, 233_001, 299_001])
PUBLISHED_2025_AMOUNTS = np.array([19, 25, 29, 35, 37, 59])

agis = st.one_of(
    st.integers(-50_000, 0).map(float),
    st.integers(0, 400_000).map(float),
    st.sampled_from([52_000.0, 52_001.0, 105_000.0, 299_000.0, 299_001.0]),
)
ages = st.one_of(st.integers(14, 17), st.integers(18, 90))
wages = st.one_of(st.just(0.0), st.integers(1, 100_000).map(float))


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "joint", "hoh"]))
    return {
        "kind": kind,
        "agi": draw(agis),
        "head": {"age": draw(ages), "employment_income": draw(wages)},
        "spouse": (
            {"age": draw(ages), "employment_income": draw(wages)}
            if kind == "joint"
            else None
        ),
    }


SEED = 20261006


def _seeded_units(n=100):
    rng = np.random.default_rng(SEED)

    def person():
        return {
            "age": int(rng.integers(14, 91)),
            "employment_income": float(rng.integers(0, 100_001))
            if rng.random() < 0.5
            else 0.0,
        }

    units = []
    for _ in range(n):
        kind = rng.choice(["single", "joint", "hoh"])
        units.append(
            {
                "kind": kind,
                "agi": float(rng.integers(-50_000, 400_001)),
                "head": person(),
                "spouse": person() if kind == "joint" else None,
            }
        )
    return units


def _situation(units, year):
    people, groups = {}, {"tax_units": {}, "households": {}}
    for i, unit in enumerate(units):
        head = f"head_{i}"
        people[head] = {**unit["head"], "is_tax_unit_head": True}
        members = [head]
        if unit["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {**unit["spouse"], "is_tax_unit_spouse": True}
            members.append(spouse)
        if unit["kind"] == "hoh":
            child = f"child_{i}"
            people[child] = {"age": 8, "is_tax_unit_dependent": True}
            members.append(child)
        groups["tax_units"][f"tax_unit_{i}"] = {
            "members": members,
            "co_modified_agi": unit["agi"],
            "co_income_tax_before_non_refundable_credits": 0,
        }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": "CO",
        }
    people = {
        name: {key: {year: value} for key, value in values.items()}
        for name, values in people.items()
    }
    groups = {
        group: {
            name: {
                key: value if key == "members" else {year: value}
                for key, value in values.items()
            }
            for name, values in entities.items()
        }
        for group, entities in groups.items()
    }
    return {"people": people, **groups}


def _run(units, year):
    sim = Simulation(situation=_situation(units, year))
    eligible = np.asarray(
        sim.calculate("co_sales_tax_refund_person_eligible", year), dtype=float
    )
    unit = sim.populations["tax_unit"].members_entity_id
    return {
        "refund": np.asarray(sim.calculate("co_sales_tax_refund", year), dtype=float),
        "agi": np.asarray(sim.calculate("co_modified_agi", year), dtype=float),
        "count": np.bincount(unit, weights=eligible, minlength=len(units)),
    }


def _check(units):
    by_year = {year: _run(units, year) for year in (2025, 2026, 2027)}
    published = PUBLISHED_2025_AMOUNTS[
        np.searchsorted(PUBLISHED_2025_STARTS, by_year[2025]["agi"], side="right")
    ]

    # 1. Gate: no tax year 2026 refund.
    np.testing.assert_array_equal(by_year[2026]["refund"], 0)

    # 2. Differential against the published tax year 2025 table.
    base = by_year[2025]
    np.testing.assert_allclose(
        base["refund"], base["count"] * published, atol=TOLERANCE
    )

    # 3. Bounds.
    for run in by_year.values():
        assert (run["refund"] >= 0).all()
        assert (run["refund"] <= 2 * PUBLISHED_2025_AMOUNTS.max()).all()
    np.testing.assert_array_equal(base["refund"] > 0, base["count"] > 0)

    # 4. Intended carry-forward of the 2025 table into 2027.
    np.testing.assert_allclose(by_year[2027]["refund"], base["refund"], atol=TOLERANCE)


@settings(
    max_examples=4,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(tax_units(), min_size=1, max_size=12))
def test_co_sales_tax_refund_invariants(units):
    _check(units)


def test_co_sales_tax_refund_invariants_seeded_population():
    _check(_seeded_units())
