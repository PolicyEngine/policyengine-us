"""Relational checks for Virginia's owner-level 529 deduction.

Va. Code § 58.1-322.03(7) bounds the owner's deduction and exempts owners
aged 70 or older from the cap. Form 760 lines 9, 13 and 15 place it after
VAGI. Paired returns check these relationships without inputting VAGI or
taxable income, or reproducing the deduction formula as a test oracle.
"""

import numpy as np
import pytest

from policyengine_us import Simulation


# Mixed rows exercise the age boundary, cap boundary, and account counts in
# one vectorized calculation. Each return also has a contributing spouse
# and a dependent who contributes to their own account.
OWNER_CASES = (
    (69, 0, 0),
    (69, 0, 1),
    (69, 3_999, 1),
    (69, 4_000, 1),
    (69, 4_001, 1),
    (69, 10_000, 1),
    (69, 10_000, 2),
    (69, 4_001, 0),
    (70, 0, 1),
    (70, 4_001, 1),
    (70, 10_000, 2),
    (72, 10_000, 1),
)


def _owner_situation(year):
    situation = {
        entity: {}
        for entity in ("people", "tax_units", "spm_units", "families", "households")
    }
    for index, (age, contribution, accounts) in enumerate(OWNER_CASES):
        for contributes in (True, False):
            unit = f"unit_{index}_{contributes}"
            head, spouse, dependent = (
                f"head_{unit}",
                f"spouse_{unit}",
                f"dependent_{unit}",
            )
            for name, person_age, income, amount, count in (
                (head, age, 60_000, contribution, accounts),
                (spouse, 40, 40_000, 6_000, 1),
                (dependent, 10, 0, 3_000, 1),
            ):
                situation["people"][name] = {
                    "age": {year: person_age},
                    "employment_income": {year: income},
                    "investment_in_529_plan_indv": {year: amount if contributes else 0},
                    "count_529_contribution_beneficiaries": {year: count},
                }
            members = [head, spouse, dependent]
            for entity in ("tax_units", "spm_units", "families", "households"):
                situation[entity][unit] = {"members": members}
            situation["households"][unit]["state_code"] = {year: "VA"}
    return situation


@pytest.mark.parametrize("year", [2024, 2026])
def test_va_529_owner_bounds_aggregation_and_taxable_income_invariants(year):
    situation = _owner_situation(year)
    simulation = Simulation(situation=situation)

    amounts = simulation.calculate("investment_in_529_plan_indv", year)
    ages = simulation.calculate("age", year)
    accounts = simulation.calculate("count_529_contribution_beneficiaries", year)
    dependent = simulation.calculate("is_tax_unit_dependent", year)
    deduction = simulation.calculate("va_529_plan_deduction_person", year)
    total = simulation.calculate("va_529_plan_deduction", year)

    # Each owner keeps their deduction, bounded by their own contribution.
    assert np.all(deduction >= 0)
    assert np.all(deduction <= amounts)
    np.testing.assert_array_equal(deduction[dependent], 0)
    younger_owner = (ages < 70) & ~dependent
    assert np.all(deduction[younger_owner] <= 4_000 * accounts[younger_owner])
    uncapped_owner = (ages >= 70) & ~dependent
    np.testing.assert_array_equal(deduction[uncapped_owner], amounts[uncapped_owner])
    below_cap = younger_owner & (amounts <= 4_000 * accounts)
    np.testing.assert_array_equal(deduction[below_cap], amounts[below_cap])

    # Aggregation retains each tax unit's own owners; no rows leak together.
    # Core preserves situation dictionary insertion order: each tax unit has
    # head/spouse/dependent rows, and contributing/zero-contribution units pair.
    np.testing.assert_array_equal(total, deduction.reshape(-1, 3).sum(axis=1))

    # Moving Form 760 code 104 below VAGI leaves both VAGI measures unchanged
    # and reduces taxable income once, dollar for dollar. Income is high
    # enough here that the taxable-income floor cannot bind.
    for variable in ("va_agi_person", "va_agi"):
        # Paired returns differ only in the contribution leaf input.
        result = simulation.calculate(variable, year).reshape(len(OWNER_CASES), 2, -1)
        np.testing.assert_array_equal(
            result[:, 0],
            result[:, 1],
        )
    taxable = simulation.calculate("va_taxable_income", year).reshape(-1, 2)
    np.testing.assert_allclose(
        taxable[:, 1] - taxable[:, 0],
        total.reshape(-1, 2)[:, 0],
        rtol=0,
        atol=0.01,
    )
