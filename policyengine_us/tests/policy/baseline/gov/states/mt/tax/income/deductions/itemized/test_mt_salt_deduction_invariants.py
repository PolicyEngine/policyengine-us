"""Check Montana's state and local tax deduction for 2021-2023.

A taxpayer elects general sales taxes or local income taxes under 26 USC
164(b)(5)(A), then adds real estate taxes before applying the cap. A joint
return deducts at most $10,000 once, through the head's mt_salt_deduction.
Spouses filing separately on the same form each elect within their own
return and deduct at most $5,000 through mt_salt_deduction_indiv.
Spouses can deduct more in separate columns than jointly when they choose
different tax categories. From 2024 we preserve the earlier per-person
amounts after Montana discontinued the schedule.

We check mixed tax units in one vectorized simulation, including all filing
statuses, dependents, sales taxes, city earnings taxes and residual local
income taxes. For every tax unit:

1. Each deduction matches an independent NumPy calculation, using the caps
   from the forms and choosing the larger eligible tax category.
2. Each return or column deducts between zero and its cap.
3. Raising any member's real estate taxes never lowers the return's or any
   column's deduction.
4. Swapping which spouse is the head moves each column with its spouse and
   leaves the joint return's deduction unchanged.
5. From 2024 each person deducts min(real estate taxes, federal cap) for the
   tax unit's filing status, as before this change.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# Form 2 (2021-2023), Itemized Deductions Schedule, line 5.
FORM_CAP = {
    "SINGLE": 10_000,
    "HEAD_OF_HOUSEHOLD": 10_000,
    "JOINT": 10_000,
    "SURVIVING_SPOUSE": 10_000,
}
FORM_CAP["SEPARATE"] = 5_000
SCHEDULE_YEARS = [2021, 2022, 2023]
# Kansas City and St. Louis earnings tax rates: local income taxes with no
# residence test, on each person's own earnings in the city.
KANSAS_CITY_RATE = 0.01
ST_LOUIS_RATE = 0.01
# 26 USC 164(b)(6) and (7)(A): $10,000 ($5,000 separate) through 2024, and
# $40,400 ($20,200 separate) for 2026.
FEDERAL_CAP = {
    2024: {"SINGLE": 10_000, "HEAD_OF_HOUSEHOLD": 10_000, "JOINT": 10_000},
    2026: {"SINGLE": 40_400, "HEAD_OF_HOUSEHOLD": 40_400, "JOINT": 40_400},
}
FEDERAL_CAP[2024]["SEPARATE"] = 5_000
FEDERAL_CAP[2026]["SEPARATE"] = 20_200
for caps in FEDERAL_CAP.values():
    caps["SURVIVING_SPOUSE"] = caps["JOINT"]
KINDS = ["single", "hoh", "separate", "surviving_spouse", "joint", "joint_dependents"]
STATUS = {
    "single": "SINGLE",
    "hoh": "HEAD_OF_HOUSEHOLD",
    "separate": "SEPARATE",
    "surviving_spouse": "SURVIVING_SPOUSE",
    "joint": "JOINT",
    "joint_dependents": "JOINT",
}

# Mostly amounts near the caps, plus zeros and large amounts.
taxes = st.one_of(
    st.just(0.0),
    st.integers(1, 6_000).map(float),
    st.integers(6_000, 30_000).map(float),
)
sales = st.one_of(st.just(0.0), st.integers(1, 3_000).map(float))
increases = st.one_of(st.just(0.0), st.integers(1, 5_000).map(float))
city_earnings = st.one_of(st.just(0.0), st.integers(1, 300_000).map(float))
city_credits = st.one_of(st.just(0.0), st.integers(1, 3_000).map(float))


@st.composite
def people(draw):
    return {
        "real_estate_taxes": draw(taxes),
        "increase": draw(increases),
        "kansas_city_earnings": draw(city_earnings),
        "st_louis_earnings": draw(city_earnings),
        "st_louis_credit": draw(city_credits),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(KINDS))
    n_dependents = (
        draw(st.integers(1, 2))
        if kind in ("hoh", "surviving_spouse", "joint_dependents")
        else 0
    )
    return {
        "kind": kind,
        "head": draw(people()),
        "spouse": draw(people()) if kind.startswith("joint") else None,
        "dependents": [draw(people()) for _ in range(n_dependents)],
        "state_sales_tax": draw(sales),
        "local_sales_tax": draw(sales),
        "other_local_income_tax": draw(sales),
    }


SEED = 20261007


def _seeded_units(n=150):
    rng = np.random.default_rng(SEED)

    def person():
        band = rng.choice(3)
        return {
            "real_estate_taxes": float(
                [0, rng.integers(1, 6_001), rng.integers(6_000, 30_001)][band]
            ),
            "increase": float(rng.integers(0, 5_001)) if rng.random() < 0.7 else 0.0,
            "kansas_city_earnings": float(rng.integers(1, 300_001))
            if rng.random() < 0.2
            else 0.0,
            "st_louis_earnings": float(rng.integers(1, 300_001))
            if rng.random() < 0.2
            else 0.0,
            "st_louis_credit": float(rng.integers(1, 3_001))
            if rng.random() < 0.3
            else 0.0,
        }

    units = []
    for _ in range(n):
        kind = str(rng.choice(KINDS))
        n_dependents = (
            int(rng.integers(1, 3))
            if kind in ("hoh", "surviving_spouse", "joint_dependents")
            else 0
        )
        units.append(
            {
                "kind": kind,
                "head": person(),
                "spouse": person() if kind.startswith("joint") else None,
                "dependents": [person() for _ in range(n_dependents)],
                "state_sales_tax": float(rng.integers(0, 3_001))
                if rng.random() < 0.3
                else 0.0,
                "local_sales_tax": float(rng.integers(0, 601))
                if rng.random() < 0.3
                else 0.0,
                "other_local_income_tax": float(rng.integers(1, 3_001))
                if rng.random() < 0.3
                else 0.0,
            }
        )
    return units


def _situation(units, year, *, raised=False, swapped=False):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}

    def add(name, values, role):
        people[name] = {
            "age": 20 if role == "dependent" else 45,
            "is_tax_unit_head": role == "head",
            "is_tax_unit_spouse": role == "spouse",
            "is_tax_unit_dependent": role == "dependent",
            "real_estate_taxes": values["real_estate_taxes"]
            + raised * values["increase"],
            "mo_kansas_city_earnings_tax_taxable_earnings": values[
                "kansas_city_earnings"
            ],
            "mo_st_louis_earnings_tax_taxable_earnings": values["st_louis_earnings"],
            "mo_st_louis_earnings_tax_credit": values["st_louis_credit"],
        }

    # Core fills unspecified entries of an input array with defaults.
    # Set all units when any unit supplies residual local income tax.
    has_local_income_tax_override = any(
        unit["other_local_income_tax"] for unit in units
    )
    for i, unit in enumerate(units):
        first, second = f"first_{i}", f"second_{i}"
        couple = unit["spouse"] is not None
        # With swapped, the second spouse is the head.
        add(first, unit["head"], "spouse" if couple and swapped else "head")
        members, marital = [first], [first]
        if couple:
            add(second, unit["spouse"], "head" if swapped else "spouse")
            members.append(second)
            marital.append(second)
        groups["marital_units"][f"couple_{i}"] = {"members": marital}
        for j, dependent in enumerate(unit["dependents"]):
            name = f"dependent_{i}_{j}"
            add(name, dependent, "dependent")
            members.append(name)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [name]}
        groups["tax_units"][f"tax_unit_{i}"] = {
            "members": members,
            "filing_status": STATUS[unit["kind"]],
            "state_sales_tax": unit["state_sales_tax"],
            "local_sales_tax": unit["local_sales_tax"],
        }
        if has_local_income_tax_override:
            payers = [unit["head"], *unit["dependents"]]
            if couple:
                payers.append(unit["spouse"])
            city_income_tax = sum(
                KANSAS_CITY_RATE * payer["kansas_city_earnings"]
                + max(
                    0,
                    ST_LOUIS_RATE * payer["st_louis_earnings"]
                    - payer["st_louis_credit"],
                )
                for payer in payers
            )
            groups["tax_units"][f"tax_unit_{i}"]["local_income_tax"] = (
                city_income_tax + unit["other_local_income_tax"]
            )
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": "MT",
        }
    situation = {"people": people, **groups}
    for entities in situation.values():
        for values in entities.values():
            for key, value in values.items():
                if key != "members":
                    values[key] = {year: value}
    return situation


def _run(units, year, **kwargs):
    sim = Simulation(situation=_situation(units, year, **kwargs))
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in [
            "mt_salt_deduction",
            "mt_salt_deduction_indiv",
            "real_estate_taxes",
            "mo_kansas_city_earnings_tax_taxable_earnings",
            "mo_st_louis_earnings_tax_taxable_earnings",
            "mo_st_louis_earnings_tax_credit",
        ]
    }
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    out["head"] = np.asarray(sim.calculate("is_tax_unit_head", year))
    out["filer"] = np.asarray(sim.calculate("is_tax_unit_head_or_spouse", year))
    return out


def _unit_sum(run, values):
    return np.bincount(run["unit"], weights=values)


def _check_schedule_year(units, year):
    base = _run(units, year)
    unit, head, filer = base["unit"], base["head"], base["filer"]
    status = np.array([STATUS[u["kind"]] for u in units])
    married = status == "JOINT"
    sales = np.array([u["state_sales_tax"] + u["local_sales_tax"] for u in units])
    joint_cap = np.array([FORM_CAP[s] for s in status])
    column_cap = np.where(married, FORM_CAP["SEPARATE"], joint_cap)

    # 1. Each taxpayer chooses the larger sales-tax or income-tax amount.
    # Each spouse keeps their own city tax and half the residual local tax.
    city_tax = KANSAS_CITY_RATE * base[
        "mo_kansas_city_earnings_tax_taxable_earnings"
    ] + np.maximum(
        0,
        ST_LOUIS_RATE * base["mo_st_louis_earnings_tax_taxable_earnings"]
        - base["mo_st_louis_earnings_tax_credit"],
    )
    other_local_tax = np.array([u["other_local_income_tax"] for u in units])
    income_tax = _unit_sum(base, city_tax) + other_local_tax
    total = _unit_sum(base, base["real_estate_taxes"]) + np.maximum(sales, income_tax)
    np.testing.assert_allclose(
        base["mt_salt_deduction"],
        head * np.minimum(total, joint_cap)[unit],
        atol=TOLERANCE,
    )
    share = np.where(married, 0.5, 1.0)[unit]
    own_income_tax = city_tax + share * other_local_tax[unit]
    own = base["real_estate_taxes"] + np.maximum(share * sales[unit], own_income_tax)
    np.testing.assert_allclose(
        base["mt_salt_deduction_indiv"],
        filer * np.minimum(own, column_cap[unit]),
        atol=TOLERANCE,
    )

    # 2. Each return or column stays within its cap.
    joint = _unit_sum(base, base["mt_salt_deduction"])
    assert (base["mt_salt_deduction"] >= 0).all()
    assert (base["mt_salt_deduction_indiv"] >= 0).all()
    assert (joint <= joint_cap + TOLERANCE).all()
    assert (base["mt_salt_deduction_indiv"] <= column_cap[unit] + TOLERANCE).all()

    # 3. Monotone in real estate taxes.
    raised = _run(units, year, raised=True)
    for name in ["mt_salt_deduction", "mt_salt_deduction_indiv"]:
        assert (raised[name] >= base[name] - TOLERANCE).all(), name

    # 4. Head swap.
    swapped = _run(units, year, swapped=True)
    np.testing.assert_allclose(
        _unit_sum(swapped, swapped["mt_salt_deduction"]), joint, atol=TOLERANCE
    )
    np.testing.assert_allclose(
        swapped["mt_salt_deduction_indiv"],
        base["mt_salt_deduction_indiv"],
        atol=TOLERANCE,
    )


def _check_unchanged_year(units, year):
    base = _run(units, year)
    status = np.array([STATUS[u["kind"]] for u in units])
    cap = np.array([FEDERAL_CAP[year][s] for s in status])[base["unit"]]
    np.testing.assert_allclose(
        base["mt_salt_deduction"],
        np.minimum(base["real_estate_taxes"], cap),
        atol=TOLERANCE,
    )
    # Spouses no longer file separately on the same form.
    assert (base["mt_salt_deduction_indiv"] == 0).all()


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.sampled_from(SCHEDULE_YEARS), st.lists(tax_units(), min_size=5, max_size=30))
def test_mt_salt_deduction_schedule_invariants(year, units):
    _check_schedule_year(units, year)


@settings(**SETTINGS)
@given(
    st.sampled_from(sorted(FEDERAL_CAP)), st.lists(tax_units(), min_size=5, max_size=30)
)
def test_mt_salt_deduction_unchanged_from_2024(year, units):
    _check_unchanged_year(units, year)


@pytest.mark.parametrize("year", SCHEDULE_YEARS)
def test_seeded_population_schedule_years(year):
    _check_schedule_year(_seeded_units(), year)


@pytest.mark.parametrize("year", sorted(FEDERAL_CAP))
def test_seeded_population_unchanged_from_2024(year):
    _check_unchanged_year(_seeded_units(), year)
