"""Properties of the Alabama miscellaneous itemized deduction.

Ala. Code 40-18-15(a)(23) allows unreimbursed employee business expenses and
the subdivision (14) deduction only above 2% of Alabama AGI. Alabama applies
that one floor to the expenses themselves, whether or not the federal
deduction is suspended. For every generated tax unit (one or two filers):

1. For Alabama AGI of zero or more, the deduction is never negative, never
   exceeds the unit's Alabama expenses, and is at least the expenses less 2%
   of Alabama AGI. Federal AGI is drawn independently of Alabama AGI, so a
   floor at federal AGI breaks the lower bound whenever federal AGI exceeds
   Alabama AGI and the expenses exceed 2% of Alabama AGI.
2. It does not fall when expenses rise and does not rise when Alabama AGI
   rises.
3. It is the same in 2017 and 2025: the federal suspension from 2018
   (26 U.S.C. 67(g)) does not reach it.
4. In 2017, when Alabama AGI equals federal AGI, it equals the federal
   miscellaneous deduction for units whose only miscellaneous expenses are
   on both lists, since each then applies one 2% floor to the same expenses.
5. A federal total supplied directly, with no Alabama expenses, yields no
   Alabama deduction: Alabama reads its own list of expenses.

A deduction that starts from the federal misc_deduction fails property 1 in
2025 whenever the expenses exceed the Alabama floor, because the federal
deduction is zero. In 2017 it also fails property 4 wherever the two AGIs
agree and the expenses exceed the floor, and property 3 wherever the expenses
exceed the two floors combined.

The strategy draws Alabama AGI from 0 to $200,000, so floors of up to $4,000
($4,200 in the arrangement with $10,000 more AGI). It draws expenses of up to
$20,000 for single filers ($21,000 with the extra $1,000) and up to $40,000
for couples ($41,000), so most generated units have a positive deduction.
test_worked_cases checks the exact values of three worked cases and runs the
properties on them; it does not draw from the strategy.
"""

import hypothesis
import hypothesis.strategies as st
import numpy as np
import pytest

from policyengine_us import Simulation

YEARS = (2017, 2025)
FLOOR = 0.02
EXTRA_EXPENSE = 1_000
EXTRA_AGI = 10_000
ARRANGEMENTS = ("base", "more_expenses", "more_agi")
TOLERANCE = 0.01


def federal_agi_of(case):
    # None draws federal AGI equal to the base Alabama AGI.
    if case["federal_agi"] is None:
        return case["al_agi"]
    return case["federal_agi"]


def unit_inputs(case, arrangement):
    head = {
        "unreimbursed_business_employee_expenses": case["head_employee"],
        "tax_preparation_fees": case["head_prep"],
    }
    spouse = {
        "unreimbursed_business_employee_expenses": case["spouse_employee"],
        "tax_preparation_fees": case["spouse_prep"],
    }
    agi = case["al_agi"]
    if arrangement == "more_expenses":
        head["unreimbursed_business_employee_expenses"] += EXTRA_EXPENSE
    elif arrangement == "more_agi":
        agi += EXTRA_AGI
    elif arrangement == "federal_only":
        head = {name: 0 for name in head}
        spouse = {name: 0 for name in spouse}
    return head, spouse, agi


def build_situation(cases, arrangements):
    # A variable supplied for any tax unit is an input for every tax unit, so
    # the federal-only units, which supply total_misc_deductions, get their
    # own simulation.
    people, tax_units, households = {}, {}, {}
    for i, case in enumerate(cases):
        for arrangement in arrangements:
            key = f"{arrangement}_{i}"
            head_inputs, spouse_inputs, agi = unit_inputs(case, arrangement)
            members = [f"head_{key}"]
            people[f"head_{key}"] = {
                name: {year: value for year in YEARS}
                for name, value in head_inputs.items()
            }
            people[f"head_{key}"]["age"] = {year: 40 for year in YEARS}
            if case["couple"]:
                members.append(f"spouse_{key}")
                people[f"spouse_{key}"] = {
                    name: {year: value for year in YEARS}
                    for name, value in spouse_inputs.items()
                }
                people[f"spouse_{key}"]["age"] = {year: 40 for year in YEARS}
            tax_unit = {
                "members": members,
                "al_agi": {year: agi for year in YEARS},
                "positive_agi": {year: federal_agi_of(case) for year in YEARS},
            }
            if arrangement == "federal_only":
                expenses = case["head_employee"] + case["head_prep"]
                tax_unit["total_misc_deductions"] = {year: expenses for year in YEARS}
            tax_units[f"tax_unit_{key}"] = tax_unit
            households[f"household_{key}"] = {
                "members": members,
                "state_code": {year: "AL" for year in YEARS},
            }
    return {"people": people, "tax_units": tax_units, "households": households}


def calculate(cases):
    simulation = Simulation(situation=build_situation(cases, ARRANGEMENTS))
    shape = (len(cases), len(ARRANGEMENTS))
    al = {
        year: np.asarray(simulation.calculate("al_misc_deduction", year)).reshape(shape)
        for year in YEARS
    }
    federal_2017 = np.asarray(simulation.calculate("misc_deduction", 2017)).reshape(
        shape
    )
    federal_only = Simulation(situation=build_situation(cases, ("federal_only",)))
    al_federal_only = {
        year: np.asarray(federal_only.calculate("al_misc_deduction", year))
        for year in YEARS
    }
    return al, federal_2017, al_federal_only


def expenses_of(case, arrangement):
    head, spouse, _ = unit_inputs(case, arrangement)
    total = sum(head.values())
    if case["couple"]:
        total += sum(spouse.values())
    return total


def assert_properties(cases):
    al, federal_2017, al_federal_only = calculate(cases)
    for i, case in enumerate(cases):
        for j, arrangement in enumerate(ARRANGEMENTS):
            expenses = expenses_of(case, arrangement)
            _, _, agi = unit_inputs(case, arrangement)
            for year in YEARS:
                value = al[year][i, j]
                assert value >= 0, (case, arrangement, year)
                assert value <= expenses + TOLERANCE, (case, arrangement, year)
                assert value >= expenses - FLOOR * agi - TOLERANCE, (
                    case,
                    arrangement,
                    year,
                )
            # The federal suspension does not reach the Alabama deduction.
            assert al[2017][i, j] == pytest.approx(al[2025][i, j], abs=TOLERANCE), (
                case,
                arrangement,
            )
        base, more_expenses, more_agi = range(len(ARRANGEMENTS))
        for year in YEARS:
            assert al[year][i, more_expenses] >= al[year][i, base] - TOLERANCE, case
            assert al[year][i, more_agi] <= al[year][i, base] + TOLERANCE, case
            assert al_federal_only[year][i] == 0, case
        # One floor each on the same expenses, where the two AGIs agree.
        for j, arrangement in enumerate(ARRANGEMENTS):
            _, _, agi = unit_inputs(case, arrangement)
            if agi != federal_agi_of(case):
                continue
            assert al[2017][i, j] == pytest.approx(federal_2017[i, j], abs=TOLERANCE), (
                case,
                ARRANGEMENTS[j],
            )


WORKED_CASES = [
    # 5,000 - 0.02 * 50,000 = 4,000 in both years.
    {
        "couple": False,
        "head_employee": 5_000,
        "head_prep": 0,
        "spouse_employee": 0,
        "spouse_prep": 0,
        "al_agi": 50_000,
        "federal_agi": 50_000,
    },
    # 1,500 + 700 - 0.02 * 60,000 = 1,000.
    {
        "couple": True,
        "head_employee": 1_500,
        "head_prep": 0,
        "spouse_employee": 0,
        "spouse_prep": 700,
        "al_agi": 60_000,
        "federal_agi": 60_000,
    },
    # Expenses equal to the floor: no deduction.
    {
        "couple": False,
        "head_employee": 1_000,
        "head_prep": 0,
        "spouse_employee": 0,
        "spouse_prep": 0,
        "al_agi": 50_000,
        "federal_agi": 50_000,
    },
]


def test_worked_cases():
    al, federal_2017, _ = calculate(WORKED_CASES)
    assert federal_2017[:, 0] == pytest.approx([4_000, 1_000, 0], abs=TOLERANCE)
    assert al[2025][:, 0] == pytest.approx([4_000, 1_000, 0], abs=TOLERANCE)
    assert al[2017][:, 0] == pytest.approx([4_000, 1_000, 0], abs=TOLERANCE)
    assert_properties(WORKED_CASES)


AMOUNTS = st.integers(min_value=0, max_value=10_000)


@hypothesis.settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[hypothesis.HealthCheck.too_slow],
)
@hypothesis.given(
    st.lists(
        st.fixed_dictionaries(
            {
                "couple": st.booleans(),
                "head_employee": AMOUNTS,
                "head_prep": AMOUNTS,
                "spouse_employee": AMOUNTS,
                "spouse_prep": AMOUNTS,
                "al_agi": st.integers(min_value=0, max_value=200_000),
                "federal_agi": st.one_of(
                    st.none(), st.integers(min_value=0, max_value=200_000)
                ),
            }
        ),
        min_size=1,
        max_size=8,
    )
)
def test_al_misc_deduction_properties(cases):
    assert_properties(cases)
