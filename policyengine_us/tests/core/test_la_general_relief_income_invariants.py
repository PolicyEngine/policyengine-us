"""Invariants for Los Angeles County General Relief gross and net income.

la_general_relief_gross_income adds the sources listed in
gov.local.ca.la.general_relief.income_sources. All of them are person-level
except tanf, which is an SPM unit amount. The SPM unit's gross income must
sum each member's own sources and count the unit's CalWORKs grant once, never
once per member.

Hypothesis draws batches of LA County SPM units (one to four people split
into one to three tax units, each person with drawn amounts of the
person-level sources, and a drawn unit CalWORKs grant), and a seeded
population of 150 units adds breadth. Each batch runs as one vectorized
simulation, again with every unit's CalWORKs grant raised by a drawn amount,
and again with a person with no income added to every unit. For every SPM
unit:

1. Differential: gross income equals an independent numpy sum of the
   members' input amounts plus the unit's CalWORKs grant.
2. Counted once: raising the CalWORKs grant by d raises gross income by
   exactly d and leaves withholdings unchanged, and net income is
   max(gross - withholdings, 0) before and after the raise.
3. Member invariance: adding a person with no income leaves gross income and
   net income unchanged.
4. Bounds: 0 <= net income <= gross income.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
YEAR = 2024

# Person-level inputs that feed the GR income sources one to one. With no
# pre-tax contributions irs_employment_income equals employment_income, and
# social_security adds social_security_retirement.
PERSON_INPUTS = [
    "employment_income",
    "self_employment_income",
    "unemployment_compensation",
    "veterans_benefits",
    "ca_state_disability_insurance",
    "social_security_retirement",
]

amounts = st.one_of(st.just(0.0), st.integers(1, 30_000).map(float))
grants = st.one_of(st.just(0.0), st.integers(1, 15_000).map(float))
raises = st.integers(1, 5_000).map(float)


@st.composite
def people(draw):
    return {name: draw(amounts) for name in PERSON_INPUTS}


@st.composite
def spm_units(draw):
    n_people = draw(st.integers(1, 4))
    n_tax_units = draw(st.integers(1, min(n_people, 3)))
    return {
        "people": [draw(people()) for _ in range(n_people)],
        # Person i files in tax unit min(i, n_tax_units - 1), so every tax
        # unit has at least one member.
        "n_tax_units": n_tax_units,
        "tanf": draw(grants),
        "raise": draw(raises),
    }


SEED = 20261006


def _seeded_units(n=150):
    rng = np.random.default_rng(SEED)

    def amount(high):
        return float(rng.integers(1, high + 1)) if rng.random() < 0.5 else 0.0

    units = []
    for _ in range(n):
        n_people = int(rng.integers(1, 5))
        units.append(
            {
                "people": [
                    {name: amount(30_000) for name in PERSON_INPUTS}
                    for _ in range(n_people)
                ],
                "n_tax_units": int(rng.integers(1, min(n_people, 3) + 1)),
                "tanf": amount(15_000),
                "raise": float(rng.integers(1, 5_001)),
            }
        )
    return units


def _situation(units, *, raise_tanf, add_person):
    people, groups = (
        {},
        {
            "tax_units": {},
            "spm_units": {},
            "families": {},
            "households": {},
        },
    )
    for i, unit in enumerate(units):
        members = []
        tax_units = [[] for _ in range(unit["n_tax_units"])]
        for j, values in enumerate(unit["people"]):
            name = f"person_{i}_{j}"
            people[name] = {"age": 40 if j == 0 else 30, **values}
            members.append(name)
            tax_units[min(j, unit["n_tax_units"] - 1)].append(name)
        if add_person:
            name = f"added_{i}"
            people[name] = {"age": 35}
            members.append(name)
            tax_units.append([name])
        for k, tax_unit in enumerate(tax_units):
            groups["tax_units"][f"tax_unit_{i}_{k}"] = {"members": tax_unit}
        tanf = unit["tanf"] + (unit["raise"] if raise_tanf else 0)
        groups["spm_units"][f"spm_unit_{i}"] = {
            "members": members,
            "tanf": {YEAR: tanf},
        }
        groups["families"][f"family_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "CA"},
            "in_la": {YEAR: True},
        }
    people = {
        name: {key: {YEAR: value} for key, value in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _run(units, *, raise_tanf=False, add_person=False):
    sim = Simulation(
        situation=_situation(units, raise_tanf=raise_tanf, add_person=add_person)
    )

    def spm(name):
        # map_to keeps the shape per SPM unit whatever the variable's entity.
        return np.asarray(sim.calculate(name, YEAR, map_to="spm_unit"), dtype=float)

    return {
        name: spm(name)
        for name in [
            "la_general_relief_gross_income",
            "la_general_relief_net_income",
            "spm_unit_paycheck_withholdings",
            "tanf",
        ]
    }


def _net(gross, withholdings):
    # The model subtracts in float32, so match its rounding at large amounts.
    difference = gross.astype(np.float32) - withholdings.astype(np.float32)
    return np.maximum(difference, np.float32(0)).astype(float)


def _check(units):
    base = _run(units)
    gross = base["la_general_relief_gross_income"]
    net = base["la_general_relief_net_income"]
    tanf = np.array([unit["tanf"] for unit in units])
    np.testing.assert_allclose(base["tanf"], tanf, atol=TOLERANCE)

    # 1. Differential against numpy.
    expected = np.array(
        [sum(sum(p.values()) for p in unit["people"]) for unit in units]
    )
    np.testing.assert_allclose(gross, expected + tanf, atol=TOLERANCE)

    # 2. CalWORKs counts exactly once.
    delta = np.array([unit["raise"] for unit in units])
    raised = _run(units, raise_tanf=True)
    np.testing.assert_allclose(
        raised["la_general_relief_gross_income"], gross + delta, atol=TOLERANCE
    )
    withholdings = base["spm_unit_paycheck_withholdings"]
    np.testing.assert_allclose(
        raised["spm_unit_paycheck_withholdings"], withholdings, atol=TOLERANCE
    )
    np.testing.assert_allclose(net, _net(gross, withholdings), atol=TOLERANCE)
    np.testing.assert_allclose(
        raised["la_general_relief_net_income"],
        _net(gross + delta, withholdings),
        atol=TOLERANCE,
    )

    # 3. A member with no income changes nothing.
    added = _run(units, add_person=True)
    for name in ["la_general_relief_gross_income", "la_general_relief_net_income"]:
        np.testing.assert_allclose(
            added[name], base[name], atol=TOLERANCE, err_msg=name
        )

    # 4. Bounds.
    assert (net >= 0).all()
    assert (net <= gross + TOLERANCE).all()


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(spm_units(), min_size=5, max_size=25))
def test_la_general_relief_income_invariants(units):
    _check(units)


def test_seeded_population():
    _check(_seeded_units())
