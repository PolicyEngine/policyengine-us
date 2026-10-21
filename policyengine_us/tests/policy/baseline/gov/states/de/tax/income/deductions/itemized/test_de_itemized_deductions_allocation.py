from itertools import product

import numpy as np
import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation


INCOME_PROFILES = [(60_000, 40_000), (45_000, -5_000), (0, -2_000)]
EXPENSE_PROFILES = [
    (
        {"real_estate_taxes": 2_000, "investment_interest_expense": 2_000},
        {"real_estate_taxes": 1_000, "charitable_cash_donations": 500},
    ),
    (
        {"real_estate_taxes": 120_000, "charitable_cash_donations": 600},
        {"real_estate_taxes": 90_000, "investment_interest_expense": 1_000},
    ),
    ({}, {}),
]


@pytest.fixture(scope="module")
def tax_benefit_system():
    # These tests do not mutate policy. Reuse the reference system while
    # keeping each simulation's inputs and calculated arrays independent.
    return CountryTaxBenefitSystem()


def _source_derived_cases():
    cases = []
    for incomes, expenses, dependent in product(
        INCOME_PROFILES, EXPENSE_PROFILES, [False, True]
    ):
        if dependent:
            incomes = (*incomes, 2_000)
            expenses = (
                *expenses,
                {"real_estate_taxes": 3_000, "investment_interest_expense": 500},
            )
        cases.append({"incomes": incomes, "expenses": expenses})
    return cases


def _situation(cases, year):
    situation = {
        "people": {},
        "tax_units": {},
        "families": {},
        "spm_units": {},
        "households": {},
    }
    unit_slices = []
    dependents = []
    position = 0
    for unit_index, case in enumerate(cases):
        members = []
        for member_index, (income, expenses) in enumerate(
            zip(case["incomes"], case["expenses"])
        ):
            person_id = f"unit_{unit_index}_person_{member_index}"
            members.append(person_id)
            values = {
                "age": [45, 42, 10][member_index],
                "employment_income": max(income, 0),
                "self_employment_income": min(income, 0),
                **expenses,
            }
            situation["people"][person_id] = {
                variable: {str(year): value} for variable, value in values.items()
            }
            if member_index == 2:
                dependents.append(position + member_index)
        tax_unit = {"members": members}
        if "unit_override" in case:
            tax_unit["de_itemized_deductions_unit"] = {str(year): case["unit_override"]}
        situation["tax_units"][f"unit_{unit_index}"] = tax_unit
        for entity in ("families", "spm_units"):
            situation[entity][f"unit_{unit_index}"] = {"members": members}
        situation["households"][f"unit_{unit_index}"] = {
            "members": members,
            "state_code": {str(year): "DE"},
        }
        unit_slices.append(slice(position, position + len(members)))
        position += len(members)
    return situation, unit_slices, dependents


@pytest.mark.parametrize("year", [2024, 2026])
def test_source_derived_allocations_conserve_totals_and_remain_nonnegative(
    year, tax_benefit_system
):
    # Eighteen synthetic units cover capped and uncapped expenses, expenses
    # paid by dependents, positive/loss/zero incomes, and units with no expense.
    situation, unit_slices, dependents = _situation(_source_derived_cases(), year)
    simulation = Simulation(tax_benefit_system=tax_benefit_system, situation=situation)
    deductions = simulation.calculate("de_itemized_deductions_indv", year)
    unit_totals = simulation.calculate("de_itemized_deductions_unit", year)

    assert np.isfinite(deductions).all()
    assert (deductions >= 0).all()
    np.testing.assert_array_equal(deductions[dependents], 0)
    np.testing.assert_allclose(
        [deductions[unit_slice].sum() for unit_slice in unit_slices],
        unit_totals,
        rtol=0,
        atol=0.01,
    )


@pytest.mark.parametrize("year", [2024, 2026])
def test_lower_unit_override_preserves_payer_amounts_without_negative_deductions(
    year, tax_benefit_system
):
    # An inconsistent aggregate override cannot also conserve the unit total
    # while preserving the deduction specifically attributable to its payer.
    cases = []
    for incomes, payer, unit_override in product(INCOME_PROFILES, [0, 1], [0, 1_000]):
        expenses = [{}, {}, {}]
        expenses[payer] = {"real_estate_taxes": 5_000}
        cases.append(
            {
                "incomes": (*incomes, 2_000),
                "expenses": expenses,
                "unit_override": unit_override,
                "payer": payer,
            }
        )
    situation, unit_slices, dependents = _situation(cases, year)
    simulation = Simulation(tax_benefit_system=tax_benefit_system, situation=situation)
    deductions = simulation.calculate("de_itemized_deductions_indv", year)

    assert np.isfinite(deductions).all()
    assert (deductions >= 0).all()
    np.testing.assert_array_equal(deductions[dependents], 0)
    for case, unit_slice in zip(cases, unit_slices):
        expected = np.zeros(3)
        expected[case["payer"]] = 5_000
        np.testing.assert_allclose(deductions[unit_slice], expected, rtol=0, atol=0.01)


def test_batched_allocation_matches_single_unit_calculation(tax_benefit_system):
    cases = _source_derived_cases()
    batch_situation, unit_slices, _ = _situation(cases, 2024)
    batch = Simulation(tax_benefit_system=tax_benefit_system, situation=batch_situation)
    # The capped-expense, dependent-payer, loss-income case shares a batch
    # with differently sized units and positive/zero-income cases.
    case_index = 9
    single_situation, _, _ = _situation([cases[case_index]], 2024)
    single = Simulation(
        tax_benefit_system=tax_benefit_system, situation=single_situation
    )

    np.testing.assert_allclose(
        batch.calculate("de_itemized_deductions_indv", 2024)[unit_slices[case_index]],
        single.calculate("de_itemized_deductions_indv", 2024),
        rtol=0,
        atol=0.01,
    )
