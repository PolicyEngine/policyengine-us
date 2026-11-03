"""Invariants for a tax unit dependent's Social Security in per-return readers.

Social Security benefits are included in the taxable income of "the person
who has the legal right to receive the benefits" (IRS Pub. 915, 2025, "Who is
taxed"), so a tax unit dependent's benefits are the dependent's, not the
filers'.
`filer_tax_exempt_social_security` is the nontaxable part of the head's and
spouse's benefits. These measures count the filers' own return:

- the Optional State Sales Tax Table income row,
  `state_sales_tax_income_bracket`: "the amount shown on your Form 1040 or
  1040-SR, line 11b, plus any nontaxable items" (2025 Schedule A
  instructions). A dependent's other nontaxable items (SSI, tax-exempt
  interest, veterans' benefits, workers' compensation, nontaxable pensions
  and retirement distributions) are the dependent's own too. The table also
  counts the family's TANF, which a dependent's own benefits can lower
  (Texas counts a child's Social Security as unearned income), so the
  population's TANF is zero;
- Colorado's sales tax refund income, `co_modified_agi`: C.R.S.
  39-22-2003(1.5)(b) adds the "Social security benefits excluded from
  federal adjusted gross income", and subsection (3) measures the qualified
  individuals' own income;
- Maine's fairness credit income,
  `me_sales_and_property_tax_fairness_credit_income`: 36 M.R.S. 5213-A(1)(B)
  and 5219-KK(1)(D) add interest and Social Security left out of federal
  adjusted gross income, and Rule 813 .03 makes the income "the
  taxpayer's";
- Washington's combined disposable income,
  `wa_pte_combined_disposable_income`: RCW 84.36.383(2) combines the
  claimant's, spouse's and cotenants' disposable income, and WAC
  458-16A-120(2)(b) adds each item left out of AGI to the AGI of "the person
  receiving these benefits". The measure also subtracts members' medical
  costs, and a member's net Medicare premium can turn on another member's
  income through the Medicare Savings Program, so the population's Medicare
  premiums are zero.

READERS holds the income measures. AMOUNTS holds what they feed: the table
amount, the refund and the credits. These also read the filing status and
who counts as a dependent, which an aged parent's own income can move: a
parent must pass a gross income test to be a dependent, and a filer heads a
household for a parent only if the parent is the filer's dependent. So
AMOUNTS are checked for the units whose dependents are all children.

`tax_exempt_social_security`, the household amount, still carries a
dependent's whole benefit for the readers whose law counts a household's
income.

The tests draw a seeded random population of tax units: a single filer or a
married couple filing jointly, whose head and spouse have wages, Social
Security and the nontaxable items above, and whose head may pay rent, with
one to three dependents, each a child or an aged parent. A dependent draws
benefits of $1 to $1,000,000, log-uniformly, and the other nontaxable items,
each of them zero about half the time. Amounts are whole dollars and stay
below 2**24, so their float32 sums, and the subtraction that takes
dependents' benefits out of the tax unit's, are exact. Every unit is placed
in each state in READERS, and each scenario runs as one vectorized
simulation.

1. Each reader is the same whether the dependents' benefits and nontaxable
   items are zero, as drawn, or doubled, and so is each amount for the units
   whose dependents are all children.
2. The household amount moves with the dependents' benefits, so the
   population exercises the property.
3. Moving the dependents' benefits and items onto the head changes each
   reader and each amount for some units, so they count the filers' own
   amounts.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

SEED = 20261102
YEAR = 2025
N_UNITS = 40
TOLERANCE = 0.01  # dollars
# The readers that measure the filers' own return, by the state each runs in.
READERS = {
    "TX": ["filer_tax_exempt_social_security", "state_sales_tax_income_bracket"],
    "CO": ["co_modified_agi"],
    "ME": ["me_sales_and_property_tax_fairness_credit_income"],
    "WA": ["wa_pte_combined_disposable_income"],
}
# What the readers feed, checked for units whose dependents are all children.
AMOUNTS = {
    "TX": ["state_sales_tax"],
    "CO": ["co_sales_tax_refund"],
    "ME": ["me_sales_tax_fairness_credit", "me_property_tax_fairness_credit"],
    "WA": [],
}
STATES = list(READERS)
CHILD_AGE_LIMIT = 18
# Person-level nontaxable items the sales tax table income counts.
NONTAXABLE_ITEMS = [
    "ssi",
    "tax_exempt_interest_income",
    "veterans_benefits",
    "workers_compensation",
    "tax_exempt_pension_income",
    "tax_exempt_retirement_distributions",
]
SCENARIOS = {"zero": 0, "as_drawn": 1, "doubled": 2}


def _draw_units(n, rng):
    def maybe(high):
        # Zero about half the time, otherwise a whole-dollar amount.
        return float(rng.choice([0, rng.integers(1, high)]))

    def filer(age):
        if age >= 62:
            benefit = "social_security_retirement"
        else:
            benefit = "social_security_disability"
        return {
            "age": age,
            "employment_income": maybe(120_000),
            "benefit": benefit,
            "social_security": maybe(40_000),
            "items": {item: maybe(8_000) for item in NONTAXABLE_ITEMS},
        }

    def dependent():
        aged_parent = bool(rng.random() < 0.3)
        benefit = (
            "social_security_retirement"
            if aged_parent
            else str(
                rng.choice(["social_security_survivors", "social_security_dependents"])
            )
        )
        # Log-uniform from $1 to $1,000,000.
        amount = float(np.floor(10 ** rng.uniform(0, 6)))
        return {
            "age": int(rng.integers(70, 90))
            if aged_parent
            else int(rng.integers(0, 18)),
            "benefit": benefit,
            "social_security": amount,
            "items": {item: maybe(20_000) for item in NONTAXABLE_ITEMS},
        }

    units = []
    for _ in range(n):
        joint = bool(rng.random() < 0.5)
        head_age = int(rng.integers(25, 85))
        units.append(
            {
                "joint": joint,
                "rent": maybe(24_000),
                "head": filer(head_age),
                "spouse": filer(int(rng.integers(25, 85))) if joint else None,
                "dependents": [dependent() for _ in range(int(rng.integers(1, 4)))],
            }
        )
    return units


def _amounts(person, scale=1):
    """A person's benefit and nontaxable items, each multiplied by scale."""
    amounts = {
        person["benefit"]: {YEAR: scale * person["social_security"]},
        "medicare_part_b_premium": {YEAR: 0},
    }
    for item, value in person["items"].items():
        amounts[item] = {YEAR: scale * value}
    return amounts


def _moved_to_head(unit):
    """The unit's head with every dependent's benefit and items added."""
    head = {**unit["head"], "items": dict(unit["head"]["items"])}
    for dependent in unit["dependents"]:
        head["social_security"] += dependent["social_security"]
        for item, value in dependent["items"].items():
            head["items"][item] += value
    return head


def _situation(units, scale=1, moved_to_head=False):
    people, tax_units, marital_units, spm_units = {}, {}, {}, {}
    families, households = {}, {}
    for state in STATES:
        for i, unit in enumerate(units):
            key = f"{state}_{i}"
            head = f"head_{key}"
            members = [head]
            couple = [head]
            head_amounts = _moved_to_head(unit) if moved_to_head else unit["head"]
            people[head] = {
                "age": {YEAR: unit["head"]["age"]},
                "is_tax_unit_head": {YEAR: True},
                "is_tax_unit_spouse": {YEAR: False},
                "is_tax_unit_dependent": {YEAR: False},
                "employment_income": {YEAR: unit["head"]["employment_income"]},
                "rent": {YEAR: unit["rent"]},
                **_amounts(head_amounts),
            }
            if unit["spouse"] is not None:
                spouse = f"spouse_{key}"
                members.append(spouse)
                couple.append(spouse)
                people[spouse] = {
                    "age": {YEAR: unit["spouse"]["age"]},
                    "is_tax_unit_head": {YEAR: False},
                    "is_tax_unit_spouse": {YEAR: True},
                    "is_tax_unit_dependent": {YEAR: False},
                    "employment_income": {YEAR: unit["spouse"]["employment_income"]},
                    **_amounts(unit["spouse"]),
                }
            marital_units[f"mu_{key}"] = {"members": couple}
            for j, dependent in enumerate(unit["dependents"]):
                person = f"dependent_{key}_{j}"
                members.append(person)
                marital_units[f"mu_{key}_{j}"] = {"members": [person]}
                people[person] = {
                    "age": {YEAR: dependent["age"]},
                    "is_tax_unit_head": {YEAR: False},
                    "is_tax_unit_spouse": {YEAR: False},
                    "is_tax_unit_dependent": {YEAR: True},
                    **_amounts(dependent, scale=0 if moved_to_head else scale),
                }
            tax_units[f"tu_{key}"] = {"members": members}
            # TANF is a family amount that a dependent's benefits can move.
            spm_units[f"spm_{key}"] = {"members": members, "tanf": {YEAR: 0}}
            families[f"fam_{key}"] = {"members": members}
            households[f"hh_{key}"] = {
                "members": members,
                "state_code": {YEAR: state},
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "families": families,
        "households": households,
    }


def _state_slice(state):
    start = STATES.index(state) * N_UNITS
    return slice(start, start + N_UNITS)


def _child_dependents_only(units):
    return np.array(
        [all(d["age"] < CHILD_AGE_LIMIT for d in u["dependents"]) for u in units]
    )


@pytest.fixture(scope="module")
def population():
    rng = np.random.default_rng(SEED)
    units = _draw_units(N_UNITS, rng)
    simulations = {
        name: Simulation(situation=_situation(units, scale=scale))
        for name, scale in SCENARIOS.items()
    }
    simulations["moved_to_head"] = Simulation(
        situation=_situation(units, moved_to_head=True)
    )
    return units, simulations


def test_population_draws_exact_whole_dollar_amounts(population):
    units, _ = population
    amounts = [
        value
        for unit in units
        for person in [unit["head"], unit["spouse"], *unit["dependents"]]
        if person is not None
        for value in [person["social_security"], *person["items"].values()]
    ]
    assert all(value == int(value) for value in amounts)
    # Doubled, a unit's benefits and items still sum below 2**24.
    totals = [
        sum(
            SCENARIOS["doubled"]
            * (person["social_security"] + sum(person["items"].values()))
            for person in [unit["head"], unit["spouse"], *unit["dependents"]]
            if person is not None
        )
        for unit in units
    ]
    assert max(totals) < 2**24


def test_population_has_units_with_child_and_parent_dependents(population):
    units, _ = population
    children_only = _child_dependents_only(units)
    assert 10 <= children_only.sum() <= len(units) - 10


@pytest.mark.parametrize("scenario", ["as_drawn", "doubled"])
def test_dependents_benefits_leave_per_return_readers_unchanged(population, scenario):
    units, simulations = population
    assert any(d["social_security"] for u in units for d in u["dependents"])
    for state, readers in READERS.items():
        rows = _state_slice(state)
        for reader in readers:
            np.testing.assert_allclose(
                simulations[scenario].calculate(reader, YEAR)[rows],
                simulations["zero"].calculate(reader, YEAR)[rows],
                atol=TOLERANCE,
                err_msg=f"{state} {reader} {scenario}",
            )


@pytest.mark.parametrize("scenario", ["as_drawn", "doubled"])
def test_child_dependents_benefits_leave_amounts_unchanged(population, scenario):
    units, simulations = population
    children_only = _child_dependents_only(units)
    for state, amounts in AMOUNTS.items():
        rows = _state_slice(state)
        for amount in amounts:
            np.testing.assert_allclose(
                simulations[scenario].calculate(amount, YEAR)[rows][children_only],
                simulations["zero"].calculate(amount, YEAR)[rows][children_only],
                atol=TOLERANCE,
                err_msg=f"{state} {amount} {scenario}",
            )


def test_household_amount_carries_dependents_benefits(population):
    units, simulations = population
    dependents_benefits = np.array(
        [sum(d["social_security"] for d in u["dependents"]) for u in units]
    )
    for state in STATES:
        rows = _state_slice(state)
        # The household amount subtracts the filers' fractional taxable
        # benefits from a total of up to a few million dollars, so it is
        # exact only to float32's relative precision.
        np.testing.assert_allclose(
            simulations["as_drawn"].calculate("tax_exempt_social_security", YEAR)[rows]
            - simulations["zero"].calculate("tax_exempt_social_security", YEAR)[rows],
            dependents_benefits,
            rtol=1e-6,
            atol=TOLERANCE,
        )


def test_readers_and_amounts_count_the_filers_own_amounts(population):
    units, simulations = population
    children_only = _child_dependents_only(units)
    for state in STATES:
        rows = _state_slice(state)
        checks = [(reader, slice(None)) for reader in READERS[state]]
        checks += [(amount, children_only) for amount in AMOUNTS[state]]
        for variable, units_checked in checks:
            moved = simulations["moved_to_head"].calculate(variable, YEAR)[rows]
            kept = simulations["as_drawn"].calculate(variable, YEAR)[rows]
            changed = np.abs(moved - kept)[units_checked] > TOLERANCE
            assert changed.any(), f"{state} {variable}"
