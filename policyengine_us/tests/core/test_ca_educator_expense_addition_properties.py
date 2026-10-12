"""California's educator addition changes only the state's AGI adjustment.

Schedule CA (540), Section C, line 11, restores the federally claimed
educator deduction. Compare otherwise identical fresh simulations, disabling
only that addition in the control. Unlike hand-worked YAML examples, this
property checks the model's dependency graph across generated expenses,
filing roles, other California adjustments and mixed-state populations.

The federal per-person cap is deliberately not reproduced here: the invariant
uses the deduction actually claimed on the federal return. Expenses include
zero, amounts on either side of the published caps, and excess expenses.
"""

from copy import deepcopy

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEARS = [2015, 2021, 2022, 2025, 2026]
# AGI is stored as float32; changing the order of sums around $300,000 can
# introduce a few cents of rounding even though the accounting is unchanged.
TOLERANCE = 0.05

expenses = st.one_of(
    st.sampled_from(
        [0, 1, 249.99, 250, 250.01, 299.99, 300, 300.01, 337.50, 349.99, 350, 350.01]
    ),
    st.integers(min_value=0, max_value=500_000).map(lambda cents: cents / 100),
)


@pytest.fixture(scope="module")
def reference_system():
    # Read-only policy source, rather than rebuilding the full model for each
    # example. US Simulation gives each call private entities, registration,
    # calculation holders and receipts; no mutable simulation is reused.
    return system


def _situation(year, head_expense, spouse_expense, dependent_expense, wages, hsa, ui):
    people = {}
    groups = {"tax_units": {}, "households": {}, "marital_units": {}}
    california = []

    for joint in (False, True):
        for state in ("CA", "NY"):
            suffix = f"{'joint' if joint else 'single'}_{state}"
            head = f"head_{suffix}"
            dependent = f"dependent_{suffix}"
            members = [head]
            couple = [head]

            def add_person(name, role, expense, earnings):
                values = {
                    "age": {"head": 45, "spouse": 43, "dependent": 20}[role],
                    "is_full_time_student": role == "dependent",
                    "is_tax_unit_head": role == "head",
                    "is_tax_unit_spouse": role == "spouse",
                    "is_tax_unit_dependent": role == "dependent",
                    "educator_expense": expense,
                    "employment_income": earnings,
                    "unemployment_compensation": ui if role == "head" else 0,
                }
                people[name] = {
                    variable: {year: value} for variable, value in values.items()
                }

            add_person(head, "head", head_expense, wages)
            if joint:
                spouse = f"spouse_{suffix}"
                add_person(spouse, "spouse", spouse_expense, wages / 2)
                members.append(spouse)
                couple.append(spouse)
            # A dependent's own deduction must not become a California
            # addition on the filer's return, even when it exceeds the cap.
            add_person(dependent, "dependent", dependent_expense, 5_000)
            members.append(dependent)
            groups["tax_units"][suffix] = {
                "members": members,
                "health_savings_account_ald": {year: hsa},
            }
            groups["households"][suffix] = {
                "members": members,
                "state_code": {year: state},
            }
            groups["marital_units"][f"couple_{suffix}"] = {"members": couple}
            groups["marital_units"][f"dependent_{suffix}"] = {"members": [dependent]}
            california.append(state == "CA")

    return {"people": people, **groups}, np.asarray(california)


@pytest.mark.parametrize("year", YEARS)
@settings(max_examples=8, deadline=None, derandomize=True)
@given(
    head_expense=expenses,
    spouse_expense=expenses,
    dependent_expense=st.integers(min_value=351, max_value=5_000),
    wages=st.integers(min_value=10_000, max_value=150_000),
    hsa=st.integers(min_value=0, max_value=2_000),
    ui=st.integers(min_value=0, max_value=10_000),
)
def test_ca_agi_restores_only_federally_claimed_educator_deduction(
    reference_system,
    year,
    head_expense,
    spouse_expense,
    dependent_expense,
    wages,
    hsa,
    ui,
):
    situation, california = _situation(
        year, head_expense, spouse_expense, dependent_expense, wages, hsa, ui
    )
    without_addition = deepcopy(situation)
    for tax_unit in without_addition["tax_units"].values():
        tax_unit["ca_educator_expense_addition"] = {year: 0}

    corrected = Simulation(tax_benefit_system=reference_system, situation=situation)
    control = Simulation(
        tax_benefit_system=reference_system, situation=without_addition
    )
    claimed = corrected.calculate("educator_expense_ald", year)
    expected_addition = california * claimed

    np.testing.assert_allclose(
        corrected.calculate("ca_educator_expense_addition", year),
        expected_addition,
        rtol=0,
        atol=TOLERANCE,
    )
    for variable in ("ca_additions", "ca_agi"):
        np.testing.assert_allclose(
            corrected.calculate(variable, year),
            control.calculate(variable, year) + expected_addition,
            rtol=0,
            atol=TOLERANCE,
            err_msg=variable,
        )

    # Only the California educator addition and its downstream calculations
    # can move. Federal deductions/AGI, other California adjustments and New
    # York AGI remain exactly the same in every row of the mixed population.
    for variable in (
        "educator_expense",
        "educator_expense_ald_person",
        "educator_expense_ald",
        "above_the_line_deductions",
        "irs_gross_income",
        "adjusted_gross_income",
        "ca_hsa_addition",
        "ca_agi_subtractions",
        "ny_agi",
    ):
        np.testing.assert_array_equal(
            corrected.calculate(variable, year),
            control.calculate(variable, year),
            err_msg=variable,
        )
