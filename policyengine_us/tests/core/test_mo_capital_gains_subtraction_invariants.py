"""Invariants for Missouri's capital gains subtraction, RSMo 143.121.3(14)(a).

From 2025 Missouri subtracts income reported as a capital gain for federal
income tax purposes. The Department of Revenue reads that as the positive
amount on federal Form 1040 line 7a: the filers' Schedule D net gain with
capital gain distributions, limited under 26 USC 1211(b), or the
distributions alone. It goes in the Form MO-A column of the spouse with the
gain. A tax unit dependent's gains and losses are on the dependent's own
return, so they never reach the filers' line 7a.

Hypothesis draws batches of tax units (single, head of household with
dependents, joint with and without dependents) whose members have signed
short- and long-term gains and capital gain distributions, and a seeded
population of 200 units adds breadth. Each batch runs as one vectorized
simulation, and again with every dependent's capital inputs set to zero.
For every tax unit:

1. Dependents' gains, losses and distributions never change
   mo_capital_gains_subtraction, the head's and spouse's
   mo_capital_gains_subtraction_person, mo_agi_subtractions or
   mo_adjusted_gross_income. (mo_income_tax is left out: it deducts federal
   income tax, which a dependent's gains still move through the Schedule D
   tax worksheet until that is fixed separately.)
2. Differential: mo_capital_gains_subtraction equals an independent numpy
   computation, rate x max(0, max(-loss limit, the head's and spouse's
   short- and long-term gains + their distributions floored at zero)), with
   the rate and loss limit taken from the statute rather than the model.
3. Accounting: the person amounts add up to the tax unit amount; dependents
   get zero; each filer gets between zero and their own positive gain, and
   a filer without a positive gain of their own gets zero.
4. For tax units without dependents and without distributions, the amount
   equals the previous all-member formula, rate x max(0, net_capital_gains).
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# RSMo 143.121.3(14)(a): 100% from tax year 2025, nothing before.
RATE = {2024: 0.0, 2025: 1.0, 2026: 1.0}
YEARS = sorted(RATE)
# 26 USC 1211(b)(1): $3,000, or $1,500 for a married individual filing
# separately. The draws below never file separately.
LOSS_LIMIT = 3_000.0

CAPITAL_INPUTS = [
    "short_term_capital_gains",
    "long_term_capital_gains",
    "non_sch_d_capital_gains",
]
OUTPUTS = [
    "mo_capital_gains_subtraction",
    "mo_capital_gains_subtraction_person",
    "mo_agi_subtractions",
    "mo_adjusted_gross_income",
    "net_capital_gains",
    "is_tax_unit_dependent",
]

signed = st.one_of(
    st.just(0.0),
    st.integers(-60_000, -1).map(float),
    st.integers(1, 60_000).map(float),
)
# Form 1099-DIV box 2a amounts are not negative; the model floors a negative
# input at zero, so a few are drawn to check that.
distributions = st.one_of(
    st.just(0.0),
    st.integers(1, 20_000).map(float),
    st.integers(-5_000, -1).map(float),
)


@st.composite
def capital(draw):
    return {
        "short_term_capital_gains": draw(signed),
        "long_term_capital_gains": draw(signed),
        "non_sch_d_capital_gains": draw(distributions),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "hoh", "joint", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    return {
        "head_wages": float(draw(st.integers(0, 120_000))),
        "head": draw(capital()),
        "spouse": draw(capital()) if kind.startswith("joint") else None,
        "dependents": [draw(capital()) for _ in range(n_dependents)],
    }


def _seeded_units(n=200, seed=20261006):
    rng = np.random.default_rng(seed)

    def amounts():
        out = {}
        for name in ["short_term_capital_gains", "long_term_capital_gains"]:
            out[name] = float(
                round(
                    rng.choice(
                        [0.0, rng.uniform(-60_000, 0), rng.uniform(0, 60_000)],
                        p=[0.4, 0.25, 0.35],
                    )
                )
            )
        out["non_sch_d_capital_gains"] = float(
            round(rng.choice([0.0, rng.uniform(0, 20_000)], p=[0.6, 0.4]))
        )
        return out

    units = []
    for _ in range(n):
        kind = rng.choice(["single", "hoh", "joint", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "head_wages": float(round(rng.uniform(0, 120_000))),
                "head": amounts(),
                "spouse": amounts() if kind.startswith("joint") else None,
                "dependents": [amounts() for _ in range(n_dependents)],
            }
        )
    return units


def _situation(units, year, zero_dependents):
    people, tax_units_, households = {}, {}, {}
    for i, u in enumerate(units):
        head = f"head_{i}"
        members = [head]
        people[head] = {
            "age": {year: 45},
            "is_tax_unit_head": {year: True},
            "employment_income": {year: u["head_wages"]},
            **{name: {year: value} for name, value in u["head"].items()},
        }
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            members.append(spouse)
            people[spouse] = {
                "age": {year: 44},
                "is_tax_unit_spouse": {year: True},
                **{name: {year: value} for name, value in u["spouse"].items()},
            }
        factor = 0.0 if zero_dependents else 1.0
        for j, amounts in enumerate(u["dependents"]):
            child = f"child_{i}_{j}"
            members.append(child)
            people[child] = {
                "age": {year: 10 + j},
                "is_tax_unit_dependent": {year: True},
                **{name: {year: factor * value} for name, value in amounts.items()},
            }
        tax_units_[f"tu_{i}"] = {"members": members}
        households[f"hh_{i}"] = {"members": members, "state_code": {year: "MO"}}
    return {"people": people, "tax_units": tax_units_, "households": households}


def _run(units, year, zero_dependents=False):
    sim = Simulation(situation=_situation(units, year, zero_dependents))
    out = {v: np.asarray(sim.calculate(v, year), dtype=float) for v in OUTPUTS}
    out["person_tax_unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _by_person(units, key):
    """Person-level input arrays in simulation member order."""
    rows = []
    for u in units:
        rows.append((u["head"], False))
        if u["spouse"] is not None:
            rows.append((u["spouse"], False))
        rows += [(amounts, True) for amounts in u["dependents"]]
    if key == "is_dependent":
        return np.array([dependent for _, dependent in rows])
    return np.array([amounts[key] for amounts, _ in rows])


def _unit_sum(run, person_values):
    return np.bincount(
        run["person_tax_unit"],
        weights=person_values,
        minlength=len(run["mo_capital_gains_subtraction"]),
    )


def _check(units, year):
    base = _run(units, year)
    dependent = _by_person(units, "is_dependent")
    filer = ~dependent
    assert np.array_equal(base["is_tax_unit_dependent"].astype(bool), dependent)
    rate = RATE[year]

    # 1. Dependents never move the filers' amounts.
    no_dependents = _run(units, year, zero_dependents=True)
    for name in ["mo_capital_gains_subtraction"]:
        np.testing.assert_allclose(
            base[name], no_dependents[name], atol=TOLERANCE, err_msg=name
        )
    for name in [
        "mo_capital_gains_subtraction_person",
        "mo_agi_subtractions",
        "mo_adjusted_gross_income",
    ]:
        np.testing.assert_allclose(
            base[name][filer],
            no_dependents[name][filer],
            atol=TOLERANCE,
            err_msg=name,
        )

    # 2. Differential against numpy.
    gains = _by_person(units, "short_term_capital_gains") + _by_person(
        units, "long_term_capital_gains"
    )
    own = gains + np.maximum(0, _by_person(units, "non_sch_d_capital_gains"))
    line_7a = np.maximum(-LOSS_LIMIT, _unit_sum(base, filer * own))
    expected = rate * np.maximum(0, line_7a)
    subtraction = base["mo_capital_gains_subtraction"]
    np.testing.assert_allclose(subtraction, expected, atol=TOLERANCE)

    # 3. Accounting.
    person = base["mo_capital_gains_subtraction_person"]
    np.testing.assert_allclose(_unit_sum(base, person), subtraction, atol=TOLERANCE)
    assert np.all(person[dependent] == 0)
    assert np.all(person >= -TOLERANCE)
    assert np.all(person <= rate * np.maximum(0, own) + TOLERANCE)
    assert np.all(person[filer & (own <= 0)] == 0)

    # 4. Unchanged for units without dependents and distributions.
    unit_has_dependent = _unit_sum(base, dependent.astype(float)) > 0
    unit_has_distributions = (
        _unit_sum(base, np.abs(_by_person(units, "non_sch_d_capital_gains"))) > 0
    )
    unchanged = ~unit_has_dependent & ~unit_has_distributions
    old = rate * np.maximum(0, base["net_capital_gains"])
    np.testing.assert_allclose(subtraction[unchanged], old[unchanged], atol=TOLERANCE)
    return base, unit_has_dependent


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.sampled_from(YEARS), st.lists(tax_units(), min_size=5, max_size=30))
def test_mo_capital_gains_subtraction_invariants(year, units):
    _check(units, year)


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    base, unit_has_dependent = _check(_seeded_units(), year)
    # The draw exercises the cases the fix is about.
    assert unit_has_dependent.sum() > 50
    if RATE[year] > 0:
        assert (base["mo_capital_gains_subtraction"] > 0).sum() > 50
