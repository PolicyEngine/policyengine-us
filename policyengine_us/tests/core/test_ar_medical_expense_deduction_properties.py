"""Invariants of Arkansas's medical expense deduction.

Ark. Code § 26-51-423(a)(1)(B) adopts 26 U.S.C. § 213 as in effect on
January 1, 2011. That version sets the floor at 7.5% of adjusted gross income
before 2013 and 10% from 2013, except that 26 U.S.C. § 213(f) keeps 7.5% for
2013 through 2016 when "such taxpayer or such taxpayer's spouse has attained
age 65". Form AR3 applies the floor to Arkansas AGI.

Every tax unit in a grid of ages, dependents, expenses and incomes shares one
simulation, run with and without explicit marital units, and is checked
against that schedule, restated here independently of the parameter files:

1. The floor depends only on the year and the ages of the taxpayer and spouse,
   including a spouse who files a separate return. A dependent's age never
   changes it, and neither does anyone else in the simulation.
2. Each deduction equals max(0, expenses - floor * AGI), so it lies between 0
   and the expenses, rises with expenses and falls with AGI.
3. The separate-on-the-same-return and joint deductions agree when the two
   AGI measures agree.
"""

from itertools import product

import numpy as np
import pytest

from policyengine_us import Simulation

YEARS = range(2011, 2027)
HEAD_AGES = (30, 64, 65, 90)
SPOUSE_AGES = (None, 30, 64, 65, 90)
DEPENDENT_AGES = (None, 10, 70)
EXPENSES = (0, 5_000, 23_000, 60_000)
AGIS = (0, 50_000, 100_000, 240_000)
SEPARATE_COUPLES = tuple(product(HEAD_AGES, HEAD_AGES))


def expected_floor(year, ages):
    """Floor under 26 U.S.C. § 213 as in effect on January 1, 2011."""
    if year < 2013:
        return 0.075
    if year <= 2016 and max(ages) >= 65:
        return 0.075
    return 0.1


def _units():
    """Tax units as (people, filing status, expenses, AGI, spouse link)."""
    units = []
    shapes = product(HEAD_AGES, SPOUSE_AGES, DEPENDENT_AGES)
    for i, (head, spouse, dependent) in enumerate(shapes):
        people = {"head": head}
        if spouse is not None:
            people["spouse"] = spouse
        if dependent is not None:
            people["dependent"] = dependent
        filing_status = "SINGLE" if spouse is None else "JOINT"
        expenses = EXPENSES[i % len(EXPENSES)]
        agi = AGIS[(i // len(EXPENSES)) % len(AGIS)]
        units.append((people, filing_status, expenses, agi, None))
    # Married couples filing separate returns: one tax unit per spouse.
    for j, (a, b) in enumerate(SEPARATE_COUPLES):
        expenses = EXPENSES[j % len(EXPENSES)]
        agi = AGIS[(j // len(EXPENSES)) % len(AGIS)]
        couple = f"couple{j}"
        units.append(({"head": a}, "SEPARATE", expenses, agi, (couple, b)))
        units.append(({"head": b}, "SEPARATE", expenses, agi, (couple, a)))
    return units


UNITS = _units()


def _situation(year, explicit_marital_units):
    period = str(year)
    people, tax_units, marital_units = {}, {}, {}
    for i, (members, filing_status, expenses, agi, link) in enumerate(UNITS):
        names = []
        for role, age in members.items():
            name = f"u{i}_{role}"
            names.append(name)
            people[name] = {
                "age": {period: age},
                "is_tax_unit_head": {period: role == "head"},
                "is_tax_unit_spouse": {period: role == "spouse"},
                "is_tax_unit_dependent": {period: role == "dependent"},
                # Tax unit AGI sits on the head, so both measures equal `agi`.
                "ar_agi_indiv": {period: agi if role == "head" else 0},
                "ar_agi_joint": {period: agi if role == "head" else 0},
            }
        tax_units[f"t{i}"] = {
            "members": names,
            # An input keeps pre-2015 years runnable: computing filing status
            # reaches the federal 401(k) limit, undefined before 2015.
            "filing_status": {period: filing_status},
            "itemized_medical_expenses": {period: expenses},
        }
        if link is not None:
            couple = link[0]
            marital_units.setdefault(couple, {"members": []})
            marital_units[couple]["members"].extend(names)
        else:
            couple = [n for n in names if not n.endswith("_dependent")]
            marital_units[f"m{i}"] = {"members": couple}
            for name in names:
                if name.endswith("_dependent"):
                    marital_units[f"m{i}_dependent"] = {"members": [name]}
    situation = {
        "people": people,
        "tax_units": tax_units,
        "households": {
            "household": {
                "members": list(people),
                "state_code": {period: "AR"},
            }
        },
    }
    if explicit_marital_units:
        situation["marital_units"] = marital_units
    return Simulation(situation=situation)


def _expected_floors(year, explicit_marital_units):
    floors = []
    for members, _, _, _, link in UNITS:
        ages = [age for role, age in members.items() if role != "dependent"]
        # A separately filing spouse is identifiable only through an explicit
        # marital unit; the default unit holds everyone in the simulation.
        if link is not None and explicit_marital_units:
            ages.append(link[1])
        floors.append(expected_floor(year, ages))
    return np.array(floors)


@pytest.mark.parametrize("explicit_marital_units", [True, False])
@pytest.mark.parametrize("year", YEARS)
def test_ar_medical_expense_deduction_invariants(year, explicit_marital_units):
    simulation = _situation(year, explicit_marital_units)
    period = str(year)
    floor = simulation.calculate("ar_medical_expense_deduction_floor", period)
    indiv = simulation.calculate("ar_medical_expense_deduction_indiv", period)
    joint = simulation.calculate("ar_medical_expense_deduction_joint", period)
    expenses = np.array([unit[2] for unit in UNITS], dtype=float)
    agi = np.array([unit[3] for unit in UNITS], dtype=float)

    # 1. The floor follows the adopted § 213 schedule for every unit.
    np.testing.assert_allclose(floor, _expected_floors(year, explicit_marital_units))

    # 2. The deduction is the excess of expenses over the floor.
    np.testing.assert_allclose(joint, np.maximum(0, expenses - floor * agi))
    assert np.all(joint >= 0)
    assert np.all(joint <= expenses)

    # 3. Both filing arrangements give the same deduction for equal AGI.
    np.testing.assert_allclose(indiv, joint)


@pytest.mark.parametrize("year", [2012, 2015, 2017])
def test_ar_medical_expense_deduction_is_monotone(year):
    period = str(year)
    variable = "ar_medical_expense_deduction_joint"
    base = _situation(year, True).calculate(variable, period)

    more_expenses = _situation(year, True)
    expenses = more_expenses.calculate("itemized_medical_expenses", period)
    more_expenses.set_input("itemized_medical_expenses", period, expenses + 1_000)
    assert np.all(more_expenses.calculate(variable, period) >= base)

    more_income = _situation(year, True)
    agi = more_income.calculate("ar_agi_joint", period)
    more_income.set_input("ar_agi_joint", period, agi + 10_000)
    assert np.all(more_income.calculate(variable, period) <= base)
