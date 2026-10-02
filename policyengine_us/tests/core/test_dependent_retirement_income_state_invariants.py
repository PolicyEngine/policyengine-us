"""Invariants for a tax unit dependent's retirement income in state income tax.

`irs_gross_income` leaves out every tax unit dependent's income: a dependent
reports it on their own return, and 26 USC 1(g)(7) can move only a child's
interest and dividends to a parent's return. State income taxes that start
from federal AGI therefore must not subtract a dependent's pension, IRA or
401(k) distributions, or military retirement pay from the filer's income.

The tests draw a seeded random population of tax units (single or joint, with
zero to two dependents, head and spouse aged under or over the common
retirement-exclusion ages) and run each scenario as one vectorized simulation:

1. `tax_unit_non_dep_add` equals a numpy reference: the head's and spouse's
   amounts of person-level variables plus tax-unit-level variables. For tax
   units without dependents it equals `add`.
2. In every state with an income tax, giving the dependents retirement income
   never lowers the filer's state income tax. Outside
   STATES_COUNTING_DEPENDENT_INCOME it changes neither the state AGI nor the
   state taxable income. (State income tax itself may still rise: credits
   keyed to household income, such as Oklahoma's sales tax relief credit,
   count every household member's income.)
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.model_api import add, tax_unit_non_dep_add
from policyengine_core.periods import period as make_period

SEED = 20260928
TOLERANCE = 0.01  # dollars

RETIREMENT_INPUTS = [
    "taxable_public_pension_income",
    "taxable_private_pension_income",
    "military_retirement_pay",
    "taxable_ira_distributions",
    "taxable_401k_distributions",
    "taxable_403b_distributions",
]


def _draw_units(n, rng):
    units = []
    for _ in range(n):
        joint = bool(rng.random() < 0.5)
        n_dependents = int(rng.integers(0, 3))

        def retirement(scale):
            return {
                name: float(round(rng.choice([0.0, rng.uniform(0, scale)])))
                for name in RETIREMENT_INPUTS
            }

        units.append(
            {
                "joint": joint,
                "head_age": int(rng.choice([35, 60, 70])),
                "spouse_age": int(rng.choice([35, 60, 70])),
                "head_wages": float(round(rng.uniform(0, 120_000))),
                "head": retirement(40_000),
                "spouse": retirement(40_000) if joint else None,
                "dependents": [
                    {
                        # Qualifying children (under 19), so no dependency
                        # test turns on the child's own income.
                        "age": int(rng.integers(1, 19)),
                        "income": retirement(15_000),
                    }
                    for _ in range(n_dependents)
                ],
            }
        )
    return units


def _situation(units, states, year, *, zero_dependents=False):
    people, tax_units, marital_units, households = {}, {}, {}, {}
    for s, state in enumerate(states):
        for i, u in enumerate(units):
            key = f"{s}_{i}"
            head = f"head_{key}"
            members = [head]
            people[head] = {
                "age": {year: u["head_age"]},
                "is_tax_unit_head": {year: True},
                "is_tax_unit_spouse": {year: False},
                "is_tax_unit_dependent": {year: False},
                "employment_income": {year: u["head_wages"]},
                **{name: {year: value} for name, value in u["head"].items()},
            }
            couple = [head]
            if u["spouse"] is not None:
                spouse = f"spouse_{key}"
                members.append(spouse)
                couple.append(spouse)
                people[spouse] = {
                    "age": {year: u["spouse_age"]},
                    "is_tax_unit_head": {year: False},
                    "is_tax_unit_spouse": {year: True},
                    "is_tax_unit_dependent": {year: False},
                    **{name: {year: value} for name, value in u["spouse"].items()},
                }
            marital_units[f"mu_{key}"] = {"members": couple}
            factor = 0.0 if zero_dependents else 1.0
            for j, dependent in enumerate(u["dependents"]):
                child = f"child_{key}_{j}"
                members.append(child)
                marital_units[f"mu_{key}_{j}"] = {"members": [child]}
                people[child] = {
                    "age": {year: dependent["age"]},
                    "is_tax_unit_head": {year: False},
                    "is_tax_unit_spouse": {year: False},
                    "is_tax_unit_dependent": {year: True},
                    **{
                        name: {year: factor * value}
                        for name, value in dependent["income"].items()
                    },
                }
            tax_units[f"tu_{key}"] = {"members": members}
            households[f"hh_{key}"] = {
                "members": members,
                "state_name": {year: state},
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
    }


def test_tax_unit_non_dep_add_matches_reference():
    rng = np.random.default_rng(SEED)
    units = _draw_units(200, rng)
    year = 2025
    sim = Simulation(situation=_situation(units, ["TX"], year))
    tax_unit = sim.populations["tax_unit"]
    period = make_period(year)
    # Two person-level inputs and one tax-unit-level aggregate.
    variables = [
        "taxable_public_pension_income",
        "military_retirement_pay",
        "tax_unit_social_security",
    ]
    result = tax_unit_non_dep_add(tax_unit, period, variables)

    expected = []
    for u in units:
        filers = [u["head"]] + ([u["spouse"]] if u["spouse"] else [])
        expected.append(
            sum(
                f["taxable_public_pension_income"] + f["military_retirement_pay"]
                for f in filers
            )
        )
    expected = np.array(expected) + sim.calculate("tax_unit_social_security", year)
    np.testing.assert_allclose(result, expected, atol=TOLERANCE)

    no_dependents = np.array([not u["dependents"] for u in units])
    everyone = add(tax_unit, period, variables)
    np.testing.assert_allclose(
        result[no_dependents], everyone[no_dependents], atol=TOLERANCE
    )
    assert (result <= everyone + TOLERANCE).all()


# States with an individual income tax on wages and retirement income.
INCOME_TAX_STATES = [
    "AL", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "UT", "VT", "VA", "WV", "WI",
]  # fmt: skip
# These states build state income from every tax unit member's income, so a
# dependent's income can raise the filer's state AGI or taxable income (and,
# except in Iowa since 2023, the tax). That is a separate issue from
# subtracting income that never entered AGI; property 2 checks only that it
# never lowers tax there.
STATES_COUNTING_DEPENDENT_INCOME = {"AL", "AR", "IA", "MS", "NJ"}
YEARS = [2025, 2026]


@pytest.mark.parametrize("year", YEARS)
def test_dependents_retirement_income_never_reduces_state_income_tax(year):
    rng = np.random.default_rng(SEED + year)
    units = _draw_units(12, rng)
    with_income = Simulation(situation=_situation(units, INCOME_TAX_STATES, year))
    without_income = Simulation(
        situation=_situation(units, INCOME_TAX_STATES, year, zero_dependents=True)
    )
    tax_with = with_income.calculate("state_income_tax", year)
    tax_without = without_income.calculate("state_income_tax", year)
    changed = np.zeros_like(tax_with, dtype=bool)
    for variable in ["state_agi", "state_taxable_income"]:
        changed |= (
            np.abs(
                with_income.calculate(variable, year)
                - without_income.calculate(variable, year)
            )
            > TOLERANCE
        )
    states = np.repeat(INCOME_TAX_STATES, len(units))
    has_dependent_income = np.tile(
        [any(any(d["income"].values()) for d in u["dependents"]) for u in units],
        len(INCOME_TAX_STATES),
    )

    lowered = tax_with < tax_without - TOLERANCE
    assert not lowered.any(), sorted(set(states[lowered]))

    counts_dependents = np.isin(states, list(STATES_COUNTING_DEPENDENT_INCOME))
    changed &= ~counts_dependents
    assert not changed.any(), sorted(set(states[changed]))
    # The population must exercise the property.
    assert has_dependent_income.sum() >= len(INCOME_TAX_STATES)
