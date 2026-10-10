"""Invariants for the IRC section 129 dependent care assistance exclusion.

The exclusion is the lesser of the employer-provided benefits, the section
129(a)(2)(A) dollar cap for the year and filing status, and the section 129(b)
earned-income limit. Section 129(a)(2)(D) raised the cap to $10,500 ($5,250 on
a separate return) for 2021 only. California keeps $5,000 ($2,500) in every
year (FTB 3506 Part IV line 22). Section 21(c) reduces the CDCC dollar limit
by the exclusion.

Hypothesis draws batches of tax units with all five filing statuses and
zero to three children under 13, and a seeded population of 200 units adds
breadth. Each batch and a copy with every filer's benefits raised by a drawn
non-negative amount run together in one vectorized California simulation.
For every tax unit:

1. Differential: dependent_care_assistance_exclusion equals an independent
   numpy min of the benefits, the cap printed on Form 2441 line 21 for the
   year (not the model's parameter) and the lesser of the filers' earnings.
2. Bound: 0 <= exclusion <= benefits, the year/status cap and earned income.
3. Monotone: raising benefits never lowers the exclusion.
4. California: ca_dependent_care_assistance_exclusion equals the same min with
   the FTB 3506 line 22 cap, and never exceeds the federal exclusion.
   Separate filers treated as unmarried use the full cap in both systems.
5. Section 21(c): cdcc_limit equals max(Form 2441 line 27 amount x the
   number of qualifying persons (at most two) - exclusion, 0).
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# Form 2441 line 21: (cap, cap for a separate return), by taxable year.
# https://www.irs.gov/pub/irs-prior/f2441--2020.pdf#page=2
# https://www.irs.gov/pub/irs-prior/f2441--2021.pdf#page=2
# https://www.irs.gov/pub/irs-prior/f2441--2022.pdf#page=2
# The post-2025 cap is Pub. L. 119-21 section 70404:
# https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=144
PUBLISHED_CAP = {
    2020: (5_000, 2_500),
    2021: (10_500, 5_250),
    2022: (5_000, 2_500),
    2025: (5_000, 2_500),
    2026: (7_500, 3_750),
}
# FTB 3506 Part IV line 22, unchanged by ARPA section 9632 and Pub. L. 119-21
# section 70404.
CALIFORNIA_CAP = (5_000, 2_500)
# Form 2441 line 27: dollar limit per qualifying person, by taxable year.
PUBLISHED_LIMIT = {2020: 3_000, 2021: 8_000, 2022: 3_000, 2025: 3_000, 2026: 3_000}
YEARS = sorted(PUBLISHED_CAP)
FILING_STATUSES = [
    "SINGLE",
    "JOINT",
    "HEAD_OF_HOUSEHOLD",
    "SEPARATE",
    "SURVIVING_SPOUSE",
]

# Mostly amounts around the caps, plus zeros and large amounts.
benefits = st.one_of(
    st.sampled_from([0.0, 2_500.0, 3_750.0, 5_000.0, 5_250.0, 7_500.0, 10_500.0]),
    st.integers(1, 5_000).map(float),
    st.integers(5_000, 12_000).map(float),
)
increases = st.one_of(st.just(0.0), st.integers(1, 6_000).map(float))
wages = st.one_of(st.just(0.0), st.integers(1, 150_000).map(float))


@st.composite
def filers(draw):
    return {
        "employment_income": draw(wages),
        "benefits": draw(benefits),
        "increase": draw(increases),
    }


@st.composite
def tax_units(draw):
    filing_status = draw(st.sampled_from(FILING_STATUSES))
    return {
        "filing_status": filing_status,
        "head": draw(filers()),
        "spouse": draw(filers()) if filing_status == "JOINT" else None,
        "children": draw(st.integers(0, 3)),
        "is_separated": draw(st.booleans()) if filing_status == "SEPARATE" else False,
    }


SEED = 20261007


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)

    def filer():
        level = rng.choice([0, 1, 2])
        return {
            "employment_income": float(rng.integers(0, 150_001)),
            "benefits": float(
                [0, rng.integers(1, 5_001), rng.integers(5_000, 12_001)][level]
            ),
            "increase": float(rng.integers(0, 6_001)) if rng.random() < 0.7 else 0.0,
        }

    units = []
    for _ in range(n):
        filing_status = str(rng.choice(FILING_STATUSES))
        units.append(
            {
                "filing_status": filing_status,
                "head": filer(),
                "spouse": filer() if filing_status == "JOINT" else None,
                "children": int(rng.integers(0, 4)),
                "is_separated": filing_status == "SEPARATE"
                and bool(rng.integers(0, 2)),
            }
        )
    return units


def _situation(units, year):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}

    def add_filer(name, values, role):
        people[name] = {
            "age": 40,
            "is_tax_unit_head": role == "head",
            "is_tax_unit_spouse": role == "spouse",
            "employment_income": values["employment_income"],
            "dependent_care_employer_benefits": values["benefits"],
        }

    for i, unit in enumerate(units):
        head = f"head_{i}"
        add_filer(head, unit["head"], "head")
        people[head]["is_separated"] = unit["is_separated"]
        members, couple = [head], [head]
        if unit["spouse"] is not None:
            spouse = f"spouse_{i}"
            add_filer(spouse, unit["spouse"], "spouse")
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j in range(unit["children"]):
            child = f"child_{i}_{j}"
            people[child] = {"age": 5, "is_tax_unit_dependent": True}
            members.append(child)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [child]}
        groups["tax_units"][f"tax_unit_{i}"] = {
            "members": members,
            "filing_status": unit["filing_status"],
        }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": "CA",
        }
    people = {
        name: {key: {year: value} for key, value in values.items()}
        for name, values in people.items()
    }
    for kind in ("tax_units", "households"):
        for group in groups[kind].values():
            for key in ("filing_status", "state_code"):
                if key in group:
                    group[key] = {year: group[key]}
    return {"people": people, **groups}


def _run(units, year):
    # Base and raised-benefit units are disjoint households in one simulation.
    # This preserves vectorized and monotonicity coverage with half as many
    # full model constructions as two independent simulations would require.
    def raised_filer(filer):
        if filer is None:
            return None
        return {**filer, "benefits": filer["benefits"] + filer["increase"]}

    raised_units = [
        {
            **unit,
            "head": raised_filer(unit["head"]),
            "spouse": raised_filer(unit["spouse"]),
        }
        for unit in units
    ]
    sim = Simulation(situation=_situation(units + raised_units, year))
    results = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in [
            "dependent_care_assistance_exclusion",
            "ca_dependent_care_assistance_exclusion",
            "cdcc_limit",
            "cdcc_treated_as_unmarried",
        ]
    }
    return (
        {name: values[: len(units)] for name, values in results.items()},
        {name: values[len(units) :] for name, values in results.items()},
    )


def _treated_as_unmarried(unit):
    return (
        unit["filing_status"] == "SEPARATE"
        and unit["is_separated"]
        and unit["children"] > 0
    )


def _expected(units, year, caps, *, raised=False):
    benefits, cap, earned = [], [], []
    for unit in units:
        filers = [unit["head"]] + ([unit["spouse"]] if unit["spouse"] else [])
        benefits.append(sum(f["benefits"] + raised * f["increase"] for f in filers))
        ordinary_separate = unit[
            "filing_status"
        ] == "SEPARATE" and not _treated_as_unmarried(unit)
        cap.append(caps[1] if ordinary_separate else caps[0])
        earned.append(min(f["employment_income"] for f in filers))
    return np.minimum(np.array(benefits), np.minimum(cap, earned))


def _check(units, year):
    base, raised = _run(units, year)
    exclusion = base["dependent_care_assistance_exclusion"]

    # 1. Differential against the published caps.
    expected = _expected(units, year, PUBLISHED_CAP[year])
    np.testing.assert_allclose(exclusion, expected, atol=TOLERANCE)

    np.testing.assert_array_equal(
        base["cdcc_treated_as_unmarried"],
        np.array([_treated_as_unmarried(unit) for unit in units]),
    )

    # 2. Bounds are stated independently, including the year's published cap
    # and the actual lesser earnings, rather than only relying on equality.
    benefits = np.array(
        [
            unit["head"]["benefits"]
            + (unit["spouse"]["benefits"] if unit["spouse"] else 0)
            for unit in units
        ]
    )
    assert (exclusion >= 0).all()
    assert (exclusion <= benefits + TOLERANCE).all()
    caps = np.array(
        [
            PUBLISHED_CAP[year][
                int(
                    unit["filing_status"] == "SEPARATE"
                    and not _treated_as_unmarried(unit)
                )
            ]
            for unit in units
        ]
    )
    earned_income_limits = np.array(
        [
            min(unit["head"]["employment_income"], unit["spouse"]["employment_income"])
            if unit["spouse"]
            else unit["head"]["employment_income"]
            for unit in units
        ]
    )
    assert (exclusion <= caps + TOLERANCE).all()
    assert (exclusion <= earned_income_limits + TOLERANCE).all()

    # 3. Monotone in benefits.
    assert (
        raised["dependent_care_assistance_exclusion"] >= exclusion - TOLERANCE
    ).all()
    np.testing.assert_allclose(
        raised["dependent_care_assistance_exclusion"],
        _expected(units, year, PUBLISHED_CAP[year], raised=True),
        atol=TOLERANCE,
    )

    # 4. California's line 22 cap.
    california = base["ca_dependent_care_assistance_exclusion"]
    np.testing.assert_allclose(
        california, _expected(units, year, CALIFORNIA_CAP), atol=TOLERANCE
    )
    assert (california <= exclusion + TOLERANCE).all()

    # 5. Section 21(c) dollar limit.
    persons = np.array([min(unit["children"], 2) for unit in units])
    np.testing.assert_allclose(
        base["cdcc_limit"],
        np.maximum(PUBLISHED_LIMIT[year] * persons - exclusion, 0),
        atol=TOLERANCE,
    )


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.sampled_from(YEARS), st.lists(tax_units(), min_size=5, max_size=30))
def test_dependent_care_assistance_exclusion_invariants(year, units):
    _check(units, year)


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    _check(_seeded_units(), year)
