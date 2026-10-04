"""Invariants for dependents' losses in the filer's AGI.

A tax unit dependent's business, rental, estate and capital items belong on the
dependent's own return (26 USC 1(g)(7) moves only a child's interest and
dividend gross income to a parent's return; Form 8814 has no line for a loss).
`irs_gross_income` already drops dependents' income, so `loss_ald` and
`limited_capital_loss` must drop dependents' losses and must not let
dependents' business income raise the section 461(l) limit.

Each property must hold for every tax unit, so the tests draw a seeded random
population of tax units (single, head of household with dependents, joint with
and without dependents) plus deterministic edge rows. Each scenario runs as one
vectorized simulation:

1. Dependents' loss-bearing inputs, of either sign, never change the filer's
   `loss_ald` or `limited_capital_loss`. They also leave AGI unchanged when the
   dependents have no positive self-employment or farm income. (A dependent's
   positive self-employment income still reaches the filer's AGI through
   `self_employment_tax_ald`, a separate path this change does not touch.)
2. 0 <= limited_capital_loss <= the filing-status cap, and it never exceeds
   the non-dependents' own capital losses (26 USC 1211(b)).
3. loss_ald >= limited_capital_loss >= 0.
4. For tax units without dependents, both variables equal the pre-change
   all-member formula (a reference implementation below), so filers without
   dependents see no change.
"""

import numpy as np
import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation

YEARS = [2024, 2025]
N_RANDOM = 300
SEED = 20260927
TOLERANCE = 0.01  # dollars

# Person-level inputs that feed loss_ald and limited_capital_loss.
BUSINESS_INPUTS = [
    "self_employment_income",
    "sstb_self_employment_income",
    "farm_operations_income",
    "rental_income",
    "farm_rent_income",
    "estate_income",
    "partnership_s_corp_income",
]
CAPITAL_INPUTS = ["short_term_capital_gains", "long_term_capital_gains"]
INPUTS = BUSINESS_INPUTS + CAPITAL_INPUTS
# Inputs whose positive values also create self-employment tax.
SE_TAX_INPUTS = [
    "self_employment_income",
    "sstb_self_employment_income",
    "farm_operations_income",
]


def _draw_amounts(rng, scale):
    """Whole-dollar amounts of either sign, with many zeros."""
    amounts = {}
    for name in INPUTS:
        amounts[name] = float(
            round(
                rng.choice(
                    [0.0, rng.uniform(-scale, 0), rng.uniform(0, scale)],
                    p=[0.5, 0.3, 0.2],
                )
            )
        )
    return amounts


def _draw_units():
    rng = np.random.default_rng(SEED)
    units = []
    for _ in range(N_RANDOM):
        kind = rng.choice(["single", "hoh", "joint", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        # A large head loss makes the section 461(l) limit bind in some units.
        head_scale = float(rng.choice([60_000.0, 600_000.0], p=[0.8, 0.2]))
        units.append(
            {
                "kind": kind,
                "head_wages": float(round(rng.uniform(0, 400_000))),
                "head": _draw_amounts(rng, head_scale),
                "spouse": (
                    _draw_amounts(rng, 60_000.0) if kind.startswith("joint") else None
                ),
                "dependents": [
                    _draw_amounts(rng, 80_000.0) for _ in range(n_dependents)
                ],
            }
        )
    zero = {name: 0.0 for name in INPUTS}
    units += [
        # The dependent's rental loss would offset the head's rental income.
        {"kind": "hoh", "head_wages": 20_000.0,
         "head": {**zero, "rental_income": 4_000.0},
         "spouse": None,
         "dependents": [{**zero, "rental_income": -4_000.0}]},
        # The dependent's short-term loss would offset the head's gain.
        {"kind": "hoh", "head_wages": 20_000.0,
         "head": {**zero, "long_term_capital_gains": 4_000.0},
         "spouse": None,
         "dependents": [{**zero, "short_term_capital_gains": -4_000.0}]},
        # The dependent's rental income would raise the head's 461(l) limit.
        {"kind": "hoh", "head_wages": 500_000.0,
         "head": {**zero, "self_employment_income": -400_000.0},
         "spouse": None,
         "dependents": [{**zero, "rental_income": 50_000.0}]},
        # Joint filers: the spouse's loss stays on the joint return.
        {"kind": "joint_dependents", "head_wages": 40_000.0,
         "head": {**zero, "rental_income": 4_000.0},
         "spouse": {**zero, "rental_income": -4_000.0},
         "dependents": [{**zero, "estate_income": -3_000.0}]},
    ]  # fmt: skip
    return units


def _situation(units, year, *, zero_dependents=False):
    people, tax_units, households = {}, {}, {}
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
                "age": {year: 12 + j},
                "is_tax_unit_dependent": {year: True},
                **{name: {year: factor * value} for name, value in amounts.items()},
            }
        tax_units[f"tu_{i}"] = {"members": members}
        households[f"hh_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
    return {"people": people, "tax_units": tax_units, "households": households}


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


@pytest.fixture(scope="module")
def units():
    return _draw_units()


@pytest.fixture(scope="module", params=YEARS)
def runs(request, units):
    year = request.param
    out = {"year": year}
    for name, kwargs in {"with": {}, "no_dependent": {"zero_dependents": True}}.items():
        sim = Simulation(situation=_situation(units, year, **kwargs))
        out[name] = {
            v: np.asarray(sim.calculate(v, year), dtype=float)
            for v in ["adjusted_gross_income", "loss_ald", "limited_capital_loss"]
        }
        out[name]["is_tax_unit_dependent"] = np.asarray(
            sim.calculate("is_tax_unit_dependent", year)
        )
        out[name]["filing_status"] = sim.calculate("filing_status", year)
        out[name]["person_tax_unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_sum(runs, person_values):
    return np.bincount(
        runs["with"]["person_tax_unit"],
        weights=person_values,
        minlength=len(runs["with"]["loss_ald"]),
    )


def test_dependent_flags_match_the_draw(runs, units):
    assert np.array_equal(
        runs["with"]["is_tax_unit_dependent"], _by_person(units, "is_dependent")
    )


def test_dependents_losses_stay_off_filer_loss_deductions(runs, units):
    dependent = _by_person(units, "is_dependent")
    has_dependent_items = _unit_sum(
        runs,
        dependent * sum(np.abs(_by_person(units, name)) for name in INPUTS),
    )
    assert (has_dependent_items > 0).sum() > 100
    for variable in ["loss_ald", "limited_capital_loss"]:
        np.testing.assert_allclose(
            runs["with"][variable],
            runs["no_dependent"][variable],
            atol=TOLERANCE,
            err_msg=variable,
        )


def test_dependents_losses_stay_off_filer_agi(runs, units):
    dependent = _by_person(units, "is_dependent")
    dependent_se_income = _unit_sum(
        runs,
        dependent
        * sum(np.maximum(_by_person(units, name), 0) for name in SE_TAX_INPUTS),
    )
    comparable = dependent_se_income == 0
    assert comparable.sum() > 200
    np.testing.assert_allclose(
        runs["with"]["adjusted_gross_income"][comparable],
        runs["no_dependent"]["adjusted_gross_income"][comparable],
        atol=TOLERANCE,
    )


def _capital_loss_cap(runs):
    p = CountryTaxBenefitSystem().parameters(f"{runs['year']}-01-01").gov.irs
    return p.ald.loss.capital.max[runs["with"]["filing_status"]]


def test_limited_capital_loss_within_statutory_bounds(runs, units):
    dependent = _by_person(units, "is_dependent")
    own_losses = np.maximum(0, -sum(_by_person(units, name) for name in CAPITAL_INPUTS))
    non_dependent_losses = _unit_sum(runs, ~dependent * own_losses)
    limited = runs["with"]["limited_capital_loss"]
    assert np.all(limited >= -TOLERANCE)
    assert np.all(limited <= _capital_loss_cap(runs) + TOLERANCE)
    assert np.all(limited <= non_dependent_losses + TOLERANCE)


def test_loss_ald_at_least_limited_capital_loss(runs):
    assert np.all(
        runs["with"]["loss_ald"] >= runs["with"]["limited_capital_loss"] - TOLERANCE
    )


def test_units_without_dependents_match_pre_change_formula(runs, units):
    """Differential check against the all-member formula used before."""
    p = CountryTaxBenefitSystem().parameters(f"{runs['year']}-01-01").gov.irs
    filing_status = runs["with"]["filing_status"]
    se = _by_person(units, "self_employment_income") + _by_person(
        units, "sstb_self_employment_income"
    )
    person_business = [se] + [_by_person(units, name) for name in BUSINESS_INPUTS[2:]]
    income = sum(_unit_sum(runs, np.maximum(x, 0)) for x in person_business)
    loss = sum(_unit_sum(runs, np.maximum(-x, 0)) for x in person_business)
    limited_business_loss = np.minimum(loss, income + p.ald.loss.max[filing_status])
    capital_losses = _unit_sum(
        runs,
        np.maximum(0, -sum(_by_person(units, name) for name in CAPITAL_INPUTS)),
    )
    limited_capital_loss = np.minimum(
        p.ald.loss.capital.max[filing_status], capital_losses
    )
    no_dependents = np.array([not u["dependents"] for u in units])
    assert no_dependents.sum() > 100
    np.testing.assert_allclose(
        runs["with"]["limited_capital_loss"][no_dependents],
        limited_capital_loss[no_dependents],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        runs["with"]["loss_ald"][no_dependents],
        (limited_business_loss + limited_capital_loss)[no_dependents],
        atol=TOLERANCE,
    )
