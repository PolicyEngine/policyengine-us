"""Invariants for estate and trust income in gross income, AGI, and the NIIT.

Each property must hold for every tax unit, so the tests draw a seeded random
population of tax units (single filers, joint filers, and filers with a
dependent) plus deterministic edge rows, run it through one vectorized
simulation per scenario, and compare scenarios that differ only in the estate
and trust inputs:

1. Person gross income rises by exactly max(0, estate_income) for a filer and
   head or spouse, and not at all for a dependent (IRC § 61(a)(14); dependents'
   income is excluded from the filer's gross income throughout the model).
2. Tax unit net investment income rises by exactly the sum of estate_income
   plus the Schedule K-1 (Form 1041) box 14 code H adjustment over non-dependent
   members (Form 8960 lines 4a and 7).
3. When every member's estate income is nonnegative and nothing else produces
   a loss, AGI rises by exactly the non-dependents' estate income.
4. A dependent's estate income and adjustment, of either sign, leave the
   filer's net investment income unchanged. When the dependent's estate income
   is nonnegative they also leave the filer's AGI and NIIT unchanged. A
   dependent's estate LOSS still reaches the filer's AGI because loss_ald pools
   every member's losses; that is a pre-existing treatment outside this change,
   recorded below as a strict expected failure so it surfaces when fixed.
5. The NIIT is nonnegative and never exceeds the rate times either net
   investment income or AGI in excess of the filing-status threshold
   (§ 1411(a)(1)).
6. The NIIT is nondecreasing in the head's estate income.
"""

import numpy as np
import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation

YEARS = [2024, 2026]
N_RANDOM = 300
SEED = 20260925
TOLERANCE = 0.01  # dollars


def _draw_units():
    rng = np.random.default_rng(SEED)
    units = []
    for _ in range(N_RANDOM):
        kind = rng.choice(["single", "joint", "dependent"])
        head_estate = float(
            rng.choice(
                [0.0, rng.uniform(-100_000, 0), rng.uniform(0, 300_000)],
                p=[0.2, 0.2, 0.6],
            )
        )
        # Code H is usually zero or removes part of the positive amount.
        head_adjustment = float(
            rng.choice(
                [
                    0.0,
                    -rng.uniform(0, max(head_estate, 0.0)),
                    rng.uniform(0, 20_000),
                ],
                p=[0.6, 0.3, 0.1],
            )
        )
        unit = {
            "kind": kind,
            "head_wages": float(rng.uniform(0, 400_000)),
            "head_interest": float(rng.uniform(0, 50_000)),
            "head_estate": head_estate,
            "head_adjustment": head_adjustment,
            "spouse_estate": 0.0,
            "spouse_adjustment": 0.0,
            "dependent_estate": 0.0,
            "dependent_adjustment": 0.0,
        }
        if kind == "joint":
            unit["spouse_estate"] = float(rng.uniform(-50_000, 200_000))
            unit["spouse_adjustment"] = float(
                -rng.uniform(0, max(unit["spouse_estate"], 0.0))
            )
        if kind == "dependent":
            # Both signs: losses test the net investment income property on
            # the full domain and feed the loss_ald expected-failure test.
            unit["dependent_estate"] = float(
                rng.choice(
                    [rng.uniform(-80_000, 0), rng.uniform(0, 150_000)],
                    p=[0.3, 0.7],
                )
            )
            unit["dependent_adjustment"] = float(
                rng.choice(
                    [
                        -rng.uniform(0, max(unit["dependent_estate"], 0.0)),
                        rng.uniform(0, 10_000),
                    ],
                    p=[0.8, 0.2],
                )
            )
        # Whole dollars keep every sum exact in float32 (integers below 2**24),
        # so the identities below can be checked to the cent.
        units.append(
            {k: (round(v) if isinstance(v, float) else v) for k, v in unit.items()}
        )
    edge = dict(
        kind="single",
        head_wages=0.0,
        head_interest=0.0,
        head_estate=0.0,
        head_adjustment=0.0,
        spouse_estate=0.0,
        spouse_adjustment=0.0,
        dependent_estate=0.0,
        dependent_adjustment=0.0,
    )
    units += [
        # Estate income exactly offset by its code H adjustment.
        {**edge, "head_wages": 240_000.0, "head_estate": 7_500.0,
         "head_adjustment": -7_500.0},
        # AGI lands exactly on the single threshold.
        {**edge, "head_wages": 170_000.0, "head_estate": 30_000.0},
        # Pure estate loss, no other income.
        {**edge, "head_estate": -40_000.0},
        # Dependent carries all the estate income.
        {**edge, "kind": "dependent", "head_wages": 300_000.0,
         "dependent_estate": 100_000.0},
        # Dependent carries an estate loss and a positive code H adjustment.
        {**edge, "kind": "dependent", "head_wages": 300_000.0,
         "dependent_estate": -60_000.0, "dependent_adjustment": 5_000.0},
    ]  # fmt: skip
    return units


def _situation(units, year, *, scale_head=0.0, zero_estate=False, zero_dep=False):
    people, tax_units, households = {}, {}, {}
    for i, u in enumerate(units):
        estate_factor = 0.0 if zero_estate else 1.0
        dep_factor = 0.0 if (zero_estate or zero_dep) else 1.0
        head = f"head_{i}"
        members = [head]
        people[head] = {
            "age": {year: 45},
            "is_tax_unit_head": {year: True},
            "employment_income": {year: u["head_wages"]},
            "taxable_interest_income": {year: u["head_interest"]},
            "estate_income": {year: estate_factor * (u["head_estate"] + scale_head)},
            "estate_income_net_investment_income_adjustment": {
                year: estate_factor * u["head_adjustment"]
            },
        }
        if u["kind"] == "joint":
            spouse = f"spouse_{i}"
            members.append(spouse)
            people[spouse] = {
                "age": {year: 44},
                "is_tax_unit_spouse": {year: True},
                "estate_income": {year: estate_factor * u["spouse_estate"]},
                "estate_income_net_investment_income_adjustment": {
                    year: estate_factor * u["spouse_adjustment"]
                },
            }
        if u["kind"] == "dependent":
            child = f"child_{i}"
            members.append(child)
            people[child] = {
                "age": {year: 10},
                "is_tax_unit_dependent": {year: True},
                "estate_income": {year: dep_factor * u["dependent_estate"]},
                "estate_income_net_investment_income_adjustment": {
                    year: dep_factor * u["dependent_adjustment"]
                },
            }
        tax_units[f"tu_{i}"] = {"members": members}
        households[f"hh_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
    return {"people": people, "tax_units": tax_units, "households": households}


@pytest.fixture(scope="module")
def units():
    return _draw_units()


@pytest.fixture(scope="module", params=YEARS)
def runs(request, units):
    year = request.param
    variants = {
        "with": {},
        "zero": {"zero_estate": True},
        "no_dependent": {"zero_dep": True},
        "bump": {"scale_head": 10_000.0},
    }
    out = {"year": year}
    for name, kwargs in variants.items():
        sim = Simulation(situation=_situation(units, year, **kwargs))
        out[name] = {
            v: np.asarray(sim.calculate(v, year), dtype=float)
            for v in [
                "irs_gross_income",
                "adjusted_gross_income",
                "net_investment_income",
                "net_investment_income_tax",
            ]
        }
        out[name]["is_tax_unit_dependent"] = np.asarray(
            sim.calculate("is_tax_unit_dependent", year)
        )
        out[name]["filing_status"] = sim.calculate("filing_status", year)
        out[name]["person_tax_unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _person_inputs(units):
    estate, adjustment, dependent = [], [], []
    for u in units:
        estate.append(u["head_estate"])
        adjustment.append(u["head_adjustment"])
        dependent.append(False)
        if u["kind"] == "joint":
            estate.append(u["spouse_estate"])
            adjustment.append(u["spouse_adjustment"])
            dependent.append(False)
        if u["kind"] == "dependent":
            estate.append(u["dependent_estate"])
            adjustment.append(u["dependent_adjustment"])
            dependent.append(True)
    return np.array(estate), np.array(adjustment), np.array(dependent)


def test_gross_income_includes_positive_estate_income_of_non_dependents(runs, units):
    estate, _, dependent = _person_inputs(units)
    assert np.array_equal(runs["with"]["is_tax_unit_dependent"], dependent)
    delta = runs["with"]["irs_gross_income"] - runs["zero"]["irs_gross_income"]
    expected = np.where(dependent, 0, np.maximum(estate, 0))
    np.testing.assert_allclose(delta, expected, atol=TOLERANCE)


def test_net_investment_income_adds_estate_income_and_code_h(runs, units):
    estate, adjustment, dependent = _person_inputs(units)
    per_person = np.where(dependent, 0, estate + adjustment)
    expected = np.bincount(
        runs["with"]["person_tax_unit"], weights=per_person, minlength=len(units)
    )
    delta = (
        runs["with"]["net_investment_income"] - runs["zero"]["net_investment_income"]
    )
    np.testing.assert_allclose(delta, expected, atol=TOLERANCE)


def test_agi_rises_by_nonnegative_estate_income(runs, units):
    estate, _, dependent = _person_inputs(units)
    tax_unit = runs["with"]["person_tax_unit"]
    any_negative = np.bincount(
        tax_unit, weights=(estate < 0).astype(float), minlength=len(units)
    )
    expected = np.bincount(
        tax_unit, weights=np.where(dependent, 0, estate), minlength=len(units)
    )
    delta = (
        runs["with"]["adjusted_gross_income"] - runs["zero"]["adjusted_gross_income"]
    )
    clean = any_negative == 0
    assert clean.sum() > len(units) // 3
    np.testing.assert_allclose(delta[clean], expected[clean], atol=TOLERANCE)


def _dependent_estate_by_unit(units):
    return np.array([u["dependent_estate"] for u in units])


def test_dependent_estate_income_stays_out_of_filer_nii(runs, units):
    dependent_estate = _dependent_estate_by_unit(units)
    assert (dependent_estate < 0).any() and (dependent_estate > 0).any()
    np.testing.assert_allclose(
        runs["with"]["net_investment_income"],
        runs["no_dependent"]["net_investment_income"],
        atol=TOLERANCE,
    )


def test_nonnegative_dependent_estate_income_stays_off_filer_return(runs, units):
    nonnegative = _dependent_estate_by_unit(units) >= 0
    for variable in ["adjusted_gross_income", "net_investment_income_tax"]:
        np.testing.assert_allclose(
            runs["with"][variable][nonnegative],
            runs["no_dependent"][variable][nonnegative],
            atol=TOLERANCE,
            err_msg=variable,
        )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Pre-existing: loss_ald pools every tax unit member's business and "
        "estate losses, so a dependent's estate loss lowers the filer's AGI. "
        "Tracked as a separate follow-up; this test flips to passing when "
        "loss_ald excludes dependents."
    ),
)
def test_dependent_estate_loss_stays_off_filer_agi(runs, units):
    negative = _dependent_estate_by_unit(units) < 0
    np.testing.assert_allclose(
        runs["with"]["adjusted_gross_income"][negative],
        runs["no_dependent"]["adjusted_gross_income"][negative],
        atol=TOLERANCE,
    )


def test_niit_within_statutory_bounds(runs):
    p = (
        CountryTaxBenefitSystem()
        .parameters(f"{runs['year']}-01-01")
        .gov.irs.investment.net_investment_income_tax
    )
    for name in ["with", "zero", "bump"]:
        r = runs[name]
        threshold = p.threshold[r["filing_status"]]
        niit = r["net_investment_income_tax"]
        assert np.all(niit >= -TOLERANCE)
        assert np.all(
            niit <= p.rate * np.maximum(r["net_investment_income"], 0) + TOLERANCE
        )
        assert np.all(
            niit
            <= p.rate * np.maximum(r["adjusted_gross_income"] - threshold, 0)
            + TOLERANCE
        )


def test_niit_nondecreasing_in_estate_income(runs):
    assert np.all(
        runs["bump"]["net_investment_income_tax"]
        >= runs["with"]["net_investment_income_tax"] - TOLERANCE
    )
    # The bump must actually move the tax for some units, or the property is
    # vacuous.
    assert np.any(
        runs["bump"]["net_investment_income_tax"]
        > runs["with"]["net_investment_income_tax"] + 1
    )
