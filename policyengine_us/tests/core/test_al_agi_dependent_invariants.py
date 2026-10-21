"""Invariants for tax unit dependents in Alabama adjusted gross income.

Alabama taxes every resident individual on their own income (Ala. Code
40-18-2(a)(1)), and every taxpayer over the filing threshold files a return
stating their own items of gross income (40-18-27(a)). Only a husband and
wife may combine income on one return (Ala. Admin. Code r. 810-3-27-.01(1)),
and the Form 40 booklet tells resident dependents to file their own returns.
So a tax unit dependent's income and deductions never belong in the filer's
Alabama AGI.

Hypothesis draws batches of Alabama tax units (single, head of family with
dependents, joint with and without dependents), and a seeded population of
150 units adds breadth. Each batch runs as one vectorized simulation, twice:
with the dependents' income and deduction inputs as drawn and with them set
to zero. For every tax unit:

1. The dependents' inputs never change Alabama AGI, the standard deduction
   or the personal and dependent exemptions. Alabama income tax is unchanged
   too wherever the itemized deductions and the federal income tax deduction
   are. Two leaks outside AGI remain, and are left out here: Alabama
   itemized deductions still count a dependent's FICA and self-employment
   tax (PolicyEngine/policyengine-us#9941), and a dependent's dividends or
   business income can still change the filer's federal tax through the
   federal preferential-rate base and QBI deduction.
2. Differential: Alabama AGI equals an independent numpy sum, over the head
   and spouse, of the parameterized gross income sources less the
   person-level deductions, less the tax-unit deductions. For units without
   dependents this is the previous all-member sum, so they see no change.
3. The dependent exemption per dependent is $1,000 for Alabama AGI up to and
   including $50,000, $500 up to and including $100,000 and $300 above
   (Ala. Code 40-18-19(a)(9)d-e, 2022 on), so it never rises with AGI.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# Person-level inputs behind Alabama's gross income sources and deductions.
DEPENDENT_INPUTS = [
    "employment_income",
    "self_employment_income",
    "self_employed_health_insurance_premiums",
    "self_employed_pension_contributions",
    "taxable_interest_income",
    "us_govt_interest_person",
    "qualified_dividend_income",
    "alimony_income",
    "alimony_expense",
    "taxable_ira_distributions",
    "traditional_ira_contributions",
    "early_withdrawal_penalty",
    "rental_income",
    "long_term_capital_gains",
    "taxable_public_pension_income",
]
UNIT_OUTPUTS = [
    "al_agi",
    "al_standard_deduction",
    "al_personal_exemption",
    "al_dependent_exemption",
    "al_itemized_deductions",
    "al_federal_income_tax_deduction",
    "al_income_tax",
    "tax_unit_dependents",
]
# Outputs that depend on Alabama AGI but not on federal tax or itemized
# deductions.
INVARIANT_OUTPUTS = [
    "al_agi",
    "al_standard_deduction",
    "al_personal_exemption",
    "al_dependent_exemption",
]

amount = st.integers(1, 40_000).map(float)
small = st.one_of(st.just(0.0), st.integers(1, 5_000).map(float))


def _maybe(draw, strategy):
    return draw(strategy) if draw(st.booleans()) else 0.0


@st.composite
def person_amounts(draw):
    interest = _maybe(draw, st.integers(1, 5_000).map(float))
    public_pension = _maybe(draw, st.integers(1, 20_000).map(float))
    return {
        "employment_income": _maybe(draw, amount),
        # Draw some business losses: a dependent's loss must not lower the
        # filer's AGI either.
        "self_employment_income": _maybe(draw, st.integers(-10_000, 40_000).map(float)),
        "self_employed_health_insurance_premiums": draw(small),
        "self_employed_pension_contributions": draw(small),
        "taxable_interest_income": interest,
        # U.S. obligation interest is part of the person's interest income.
        "us_govt_interest_person": float(draw(st.integers(0, int(interest)))),
        "qualified_dividend_income": draw(small),
        "alimony_income": draw(small),
        "alimony_expense": draw(small),
        "taxable_ira_distributions": draw(small),
        "traditional_ira_contributions": draw(small),
        "early_withdrawal_penalty": draw(st.integers(0, 300).map(float)),
        "rental_income": _maybe(draw, st.integers(-5_000, 20_000).map(float)),
        "long_term_capital_gains": draw(small),
        # A public pension is both in pension income and subtracted from
        # Alabama gross income.
        "taxable_public_pension_income": public_pension,
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "hof", "joint", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hof", "joint_dependents") else 0
    return {
        "head": {"age": draw(st.integers(25, 75)), **draw(person_amounts())},
        "spouse": (
            {"age": draw(st.integers(25, 75)), **draw(person_amounts())}
            if kind.startswith("joint")
            else None
        ),
        "dependents": [
            {"age": draw(st.integers(5, 23)), **draw(person_amounts())}
            for _ in range(n_dependents)
        ],
    }


SEED = 20261006


def _seeded_amounts(rng):
    def some(low, high, p=0.5):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    interest = some(1, 5_000)
    public_pension = some(1, 20_000, 0.3)
    return {
        "employment_income": some(1, 40_000, 0.6),
        "self_employment_income": some(-10_000, 40_000, 0.4),
        "self_employed_health_insurance_premiums": some(1, 5_000, 0.3),
        "self_employed_pension_contributions": some(1, 5_000, 0.3),
        "taxable_interest_income": interest,
        "us_govt_interest_person": float(round(rng.uniform(0, interest))),
        "qualified_dividend_income": some(1, 5_000, 0.3),
        "alimony_income": some(1, 5_000, 0.2),
        "alimony_expense": some(1, 5_000, 0.2),
        "taxable_ira_distributions": some(1, 5_000, 0.3),
        "traditional_ira_contributions": some(1, 5_000, 0.3),
        "early_withdrawal_penalty": some(0, 300, 0.2),
        "rental_income": some(-5_000, 20_000, 0.3),
        "long_term_capital_gains": some(1, 5_000, 0.3),
        "taxable_public_pension_income": public_pension,
    }


def _seeded_units(n=150):
    rng = np.random.default_rng(SEED)
    units = []
    for _ in range(n):
        kind = rng.choice(["single", "hof", "joint", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hof", "joint_dependents") else 0
        )
        units.append(
            {
                "head": {"age": int(rng.integers(25, 76)), **_seeded_amounts(rng)},
                "spouse": (
                    {"age": int(rng.integers(25, 76)), **_seeded_amounts(rng)}
                    if kind.startswith("joint")
                    else None
                ),
                "dependents": [
                    {"age": int(rng.integers(5, 24)), **_seeded_amounts(rng)}
                    for _ in range(n_dependents)
                ],
            }
        )
    return units


def _situation(units, year, *, zero_dependents):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {
            "is_tax_unit_head": True,
            "is_tax_unit_spouse": False,
            "is_tax_unit_dependent": False,
            **u["head"],
        }
        members, couple = [head], [head]
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "is_tax_unit_head": False,
                "is_tax_unit_spouse": True,
                "is_tax_unit_dependent": False,
                **u["spouse"],
            }
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, d in enumerate(u["dependents"]):
            child = f"dependent_{i}_{j}"
            amounts = dict(d)
            if zero_dependents:
                amounts.update({name: 0.0 for name in DEPENDENT_INPUTS})
            people[child] = {
                "is_full_time_student": d["age"] >= 19,
                "is_tax_unit_head": False,
                "is_tax_unit_spouse": False,
                "is_tax_unit_dependent": True,
                **amounts,
            }
            members.append(child)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [child]}
        groups["tax_units"][f"tax_unit_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "AL"},
        }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _agi_items(sim, year):
    """Alabama's AGI items split by entity, read from the parameter lists."""
    p = sim.tax_benefit_system.parameters(year).gov.states.al.tax.income.agi
    variables = sim.tax_benefit_system.variables
    items = {}
    for kind, names in (
        ("gross", p.gross_income_sources),
        ("deduction", p.deductions),
    ):
        for name in names:
            entity = variables[name].entity.key
            items[(kind, name)] = (
                entity,
                np.asarray(sim.calculate(name, year), dtype=float),
            )
    return items


def _run(units, year, *, zero_dependents):
    sim = Simulation(situation=_situation(units, year, zero_dependents=zero_dependents))
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in UNIT_OUTPUTS
    }
    out["is_dependent"] = np.asarray(
        sim.calculate("is_tax_unit_dependent", year), dtype=bool
    )
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    out["items"] = _agi_items(sim, year)
    return out


def _unit_sum(run, values):
    return np.bincount(run["unit"], weights=values, minlength=len(run["al_agi"]))


def _check(units, year):
    run = _run(units, year, zero_dependents=False)
    zeroed = _run(units, year, zero_dependents=True)
    filer = ~run["is_dependent"]
    has_dependent = run["tax_unit_dependents"] > 0

    # 1. Dependents' items never reach the filer's Alabama return.
    for name in INVARIANT_OUTPUTS:
        np.testing.assert_allclose(
            run[name], zeroed[name], atol=TOLERANCE, err_msg=name
        )
    same_other_deductions = np.isclose(
        run["al_federal_income_tax_deduction"],
        zeroed["al_federal_income_tax_deduction"],
        atol=TOLERANCE,
    ) & np.isclose(
        run["al_itemized_deductions"],
        zeroed["al_itemized_deductions"],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        run["al_income_tax"][same_other_deductions],
        zeroed["al_income_tax"][same_other_deductions],
        atol=TOLERANCE,
    )

    # 2. Differential against numpy sums over the head and spouse.
    reference = np.zeros_like(run["al_agi"])
    all_members = np.zeros_like(run["al_agi"])
    for (kind, name), (entity, values) in run["items"].items():
        sign = 1 if kind == "gross" else -1
        if entity == "person":
            reference += sign * _unit_sum(run, filer * values)
            all_members += sign * _unit_sum(run, values)
        else:
            assert entity == "tax_unit", name
            reference += sign * values
            all_members += sign * values
    np.testing.assert_allclose(run["al_agi"], reference, atol=TOLERANCE)
    np.testing.assert_allclose(
        run["al_agi"][~has_dependent],
        all_members[~has_dependent],
        atol=TOLERANCE,
    )

    # 3. Statutory dependent exemption tiers, "equal to or less than" each
    # threshold (Ala. Code 40-18-19(a)(9)d-e).
    agi = run["al_agi"]
    per_dependent = np.select([agi <= 50_000, agi <= 100_000], [1_000, 500], 300)
    np.testing.assert_allclose(
        run["al_dependent_exemption"],
        run["tax_unit_dependents"] * per_dependent,
        atol=TOLERANCE,
    )


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
def test_dependents_stay_off_the_filers_alabama_return(units):
    _check(units, 2025)


@pytest.mark.parametrize("year", [2025, 2026])
def test_seeded_population(year):
    _check(_seeded_units(), year)
