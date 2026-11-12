"""Check Georgia's funded copays and the households outside their scope.

GaDOE pays both copays with federal ESSER funds in SY2023-24, then state
appropriations under HB 916 (FY2025), program 24.13, line 1871; HB 68
(FY2026), item 155.4; and HB 974 (FY2027), program 24.13. Date the school
year from July 1 under 7 CFR 210.2. The annual formulas read January 1,
so coverage changes 2024 through 2027.

Each draw puts Georgia households beside identical Alabama, Florida and
North Carolina households in one simulation per year. Generated incomes
include the federal boundaries and preserve categorical eligibility.
One system serves every example. Parameter checks cover each fiscal start
and the enacted end directly, including July dates that annual formulas
cannot distinguish.
"""

from itertools import product

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us import Simulation

YEARS = (2023, 2024, 2025, 2026, 2027, 2028)
STATES = ("GA", "AL", "FL", "NC")
TIERS = (
    "school_meal_tier",
    "school_meal_breakfast_tier",
    "school_meal_lunch_tier",
)
BOUNDARY_INCOMES = (12_999, 13_000, 13_001, 18_499, 18_500, 18_501)
FPG = 10_000
FREE_LIMIT = 13_000
REDUCED_LIMIT = 18_500


@pytest.fixture(scope="module")
def school_meal_system():
    return Simulation.default_tax_benefit_system_instance


@pytest.mark.parametrize(
    "date, expected",
    (
        ("2023-06-30", False),
        ("2023-07-01", True),
        ("2024-06-30", True),
        ("2024-07-01", True),
        ("2025-06-30", True),
        ("2025-07-01", True),
        ("2026-06-30", True),
        ("2026-07-01", True),
        ("2027-06-30", True),
        ("2027-07-01", False),
    ),
)
def test_fiscal_funding_boundaries(school_meal_system, date, expected):
    parameter = get_parameter(
        school_meal_system.parameters,
        "gov.usda.school_meals.state_covers_reduced_price_copay.GA",
    )
    assert bool(parameter(date)) == expected


def _situation(incomes, children, year):
    people, spm_units, households = {}, {}, {}
    records = []
    for index, (income, categorical, state) in enumerate(
        product(incomes, (False, True), STATES)
    ):
        parent = f"parent_{index}"
        people[parent] = {"age": {year: 35}, "is_in_k12_school": {year: False}}
        members = [parent]
        for child_index in range(children):
            name = f"child_{index}_{child_index}"
            people[name] = {
                "age": {year: 10},
                "is_in_k12_school": {year: True},
            }
            members.append(name)
        spm_units[f"unit_{index}"] = {
            "members": members,
            "spm_unit_fpg": {year: FPG},
            "school_meal_countable_income": {year: income},
            "meets_school_meal_categorical_eligibility": {year: categorical},
        }
        households[f"household_{index}"] = {
            "members": members,
            "state_code": {year: state},
        }
        records.append((income, categorical, state))
    return {"people": people, "spm_units": spm_units, "households": households}, records


def _expected_tier(income, categorical, copays):
    if categorical or income <= FREE_LIMIT:
        return "FREE"
    if income > REDUCED_LIMIT:
        return "PAID"
    return "FREE" if copays else "REDUCED"


def _check(incomes, children, system):
    incomes = sorted(set((*BOUNDARY_INCOMES, *incomes)))
    for year in YEARS:
        situation, records = _situation(incomes, children, year)
        simulation = Simulation(situation=situation, tax_benefit_system=system)
        results = {
            name: simulation.calculate(name, year).decode_to_str() for name in TIERS
        }
        net = np.asarray(simulation.calculate("school_meal_net_subsidy", year))
        meal_parameters = system.parameters(f"{year}-01-01").gov.usda.school_meals
        rates = meal_parameters.amount
        paid = rates.sbp.CONTIGUOUS_US.PAID + rates.nslp.CONTIGUOUS_US.PAID
        control_results = {}
        for index, (income, categorical, state) in enumerate(records):
            ga_coverage = state == "GA" and 2024 <= year <= 2027
            # North Carolina already covers both copays throughout these years.
            old_tier = _expected_tier(income, categorical, state == "NC")
            tier = _expected_tier(income, categorical, ga_coverage or state == "NC")
            for name in TIERS:
                assert results[name][index] == tier, (year, state, income, name)
            intended_change = (
                ga_coverage and not categorical and FREE_LIMIT < income <= REDUCED_LIMIT
            )
            assert (tier != old_tier) == intended_change
            daily = (
                rates.sbp.CONTIGUOUS_US[tier] + rates.nslp.CONTIGUOUS_US[tier] - paid
            )
            np.testing.assert_allclose(
                net[index],
                children * meal_parameters.school_days * daily,
                atol=0.01,
                rtol=0,
            )
            control_results[income, categorical, state] = (tier, net[index])

        for income, categorical in product(incomes, (False, True)):
            ga_tier, ga_net = control_results[income, categorical, "GA"]
            fl_tier, fl_net = control_results[income, categorical, "FL"]
            if 2024 <= year <= 2027:
                assert ga_net >= fl_net - 0.01
                if categorical or income <= FREE_LIMIT or income > REDUCED_LIMIT:
                    assert ga_tier == fl_tier
                    np.testing.assert_allclose(ga_net, fl_net, atol=0.01, rtol=0)
            else:
                assert ga_tier == fl_tier
                np.testing.assert_allclose(ga_net, fl_net, atol=0.01, rtol=0)

        generosity = {"FREE": 2, "REDUCED": 1, "PAID": 0}
        for categorical, state in product((False, True), STATES):
            scores = [
                generosity[control_results[income, categorical, state][0]]
                for income in incomes
            ]
            assert all(left >= right for left, right in zip(scores, scores[1:]))


@given(
    incomes=st.lists(st.integers(0, 40_000), min_size=1, max_size=4),
    children=st.integers(1, 3),
)
@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
def test_copay_scope_and_income_monotonicity(school_meal_system, incomes, children):
    _check(incomes, children, school_meal_system)
