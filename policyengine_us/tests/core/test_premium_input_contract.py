"""Premium payment methods are disjoint inputs with consumer-specific treatment.

Moving employee-paid premiums from non-pretax payments to pretax payroll
deductions leaves total medical spending unchanged. SNAP, HUD,
child-care deductions, Orange County General Relief and New Jersey
medical expenses count both payment methods. The CRFB broad income base adds
back the pretax premium excluded from federal wages. Michigan's wage exclusion
and non-pretax premium deduction likewise leave household resources unchanged.
North Dakota excludes pretax premiums from income and deducts non-pretax
premiums as medical expenses, also leaving renters' refund income unchanged.

Federal taxable and FICA wages, ACA/Medicaid MAGI, and tax deductions that
exclude pretax premiums distinguish the payment methods. SSI also excludes
qualified salary-reduction premiums from wages before its earned-income
disregard. The SGA work-earnings test retains payroll premium deductions.
Program premiums and
eligibility are held fixed here: changing MAGI can otherwise legitimately change
Marketplace, CHIP or Medicaid premiums, obscuring the spending invariant.

Each generated batch uses fresh vectorized simulations across several states;
no calculated arrays are shared between the two situations or across examples.
"""

import numpy as np
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.reforms.crfb.agi_surtax import agi_surtax_reform_object
from policyengine_us.system import system


YEAR = 2026
MONTH = "2026-01"
STATES = ("CA", "MO", "PA", "NJ", "OH", "MI", "ND")
SURTAX_ON = {
    "gov.contrib.crfb.surtax.in_effect": {"2000-01-01.2100-12-31": True},
    "gov.contrib.crfb.surtax.increased_base.in_effect": {"2000-01-01.2100-12-31": True},
}


@st.composite
def premium_transfers(draw):
    total = draw(st.integers(0, 12_000))
    pretax = draw(st.integers(0, total))
    transfer = draw(st.integers(0, total - pretax))
    return total, pretax, transfer


def _situation(batch, moved):
    people = {}
    tax_units = {}
    spm_units = {}
    households = {}
    for row, (total, initial_pretax, transfer) in enumerate(batch):
        pretax = initial_pretax + (transfer if moved else 0)
        non_pretax = total - pretax
        for state in STATES:
            key = f"{state}_{row}"
            people[key] = {
                "age": {YEAR: 40},
                "is_tax_unit_head": {YEAR: True},
                "is_ssi_aged_blind_disabled": {YEAR: True},
                "employment_income": {YEAR: 250_000},
                "pre_tax_health_insurance_premiums": {YEAR: pretax},
                # These are alternative representations used by different
                # consumers, not additive premiums within the non-pretax set.
                "health_insurance_premiums": {YEAR: non_pretax},
                "health_insurance_premiums_without_medicare_part_b": {YEAR: non_pretax},
                "other_health_insurance_premiums": {YEAR: non_pretax},
                "other_medical_expenses": {YEAR: 300},
                "over_the_counter_health_expenses": {YEAR: 100},
                "medicare_enrolled": {YEAR: False},
                "is_medicare_eligible": {YEAR: False},
                "medicare_part_a_premium": {YEAR: 0},
                "medicare_part_b_premium": {YEAR: 0},
                "income_adjusted_part_d_premium_surcharge": {YEAR: 0},
                "employer_sponsored_insurance_premiums": {YEAR: 0},
                "self_employed_health_insurance_ald_person": {YEAR: 0},
                "general_assistance": {YEAR: 0},
                "ca_oc_general_relief_countable_earned_income": {MONTH: 5_000},
                "ca_oc_general_relief_gross_unearned_income": {MONTH: 0},
                "ca_oc_general_relief_receives_other_cash_assistance": {MONTH: False},
            }
            tax_units[key] = {
                "members": [key],
                "chip_premium": {YEAR: 0},
                "medicaid_premium": {YEAR: 0},
                "marketplace_net_premium": {YEAR: 0},
                "above_the_line_deductions": {YEAR: 0},
                "self_employed_health_insurance_ald": {YEAR: 0},
                "dependents_self_employed_health_insurance_ald": {YEAR: 0},
                "medical_expense_deduction": {YEAR: 0},
                "tax_unit_itemizes": {YEAR: False},
                "taxable_income": {YEAR: 300_000},
                "nj_agi": {YEAR: 50_000},
                "oh_employer_subsidized_health_plan_eligible": {YEAR: True},
            }
            spm_units[key] = {
                "members": [key],
                "tanf": {YEAR: 0},
                "mo_ccs_countable_income": {MONTH: 5_000},
                "pa_ccw_countable_income": {YEAR: 60_000},
                "pa_ccw_stepparent_deduction": {MONTH: 0},
            }
            households[key] = {
                "members": [key],
                "state_code": {YEAR: state},
                "in_oc": {YEAR: state == "CA"},
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "households": households,
        "marital_units": {key: {"members": [key]} for key in people},
        "families": {key: {"members": [key]} for key in people},
    }


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@example(batch=[(0, 0, 0), (12_000, 0, 12_000), (12_000, 6_000, 6_000)])
@example(batch=[(12_000, 12_000, 0), (1, 0, 1)])
@given(batch=st.lists(premium_transfers(), min_size=1, max_size=3))
def test_premium_transfer_respects_each_consumers_tax_treatment(batch):
    # Supplying the read-only reference system avoids rebuilding the country
    # for every generated example. Simulation clones it before applying these
    # reforms, giving each situation private policy state and result arrays.
    reform = (SURTAX_ON, agi_surtax_reform_object)
    baseline = Simulation(
        situation=_situation(batch, False), tax_benefit_system=system, reform=reform
    )
    moved = Simulation(
        situation=_situation(batch, True), tax_benefit_system=system, reform=reform
    )
    transfer = np.repeat([row[2] for row in batch], len(STATES))
    total = np.repeat([row[0] for row in batch], len(STATES))
    states = np.tile(STATES, len(batch))

    np.testing.assert_allclose(
        baseline.calculate("spm_unit_medical_out_of_pocket_expenses", YEAR),
        total + 400,
        rtol=0,
        atol=0.02,
    )
    # North Dakota starts from raw market wages, excludes the pretax
    # contribution once, and deducts only the remaining medical expenses.
    np.testing.assert_allclose(
        baseline.calculate("nd_renters_refund_income", YEAR),
        (250_000 - total - 300) * (states == "ND"),
        rtol=0,
        atol=0.02,
    )

    invariant_consumers = (
        ("spm_unit_health_insurance_premiums", YEAR),
        ("spm_unit_medical_out_of_pocket_expenses", YEAR),
        ("snap_allowable_medical_expenses", YEAR),
        ("hud_medical_expenses", YEAR),
        ("mo_ccs_adjusted_income", MONTH),
        ("pa_ccw_medical_expenses", YEAR),
        ("pa_ccw_adjusted_income", YEAR),
        ("ca_oc_general_relief_countable_income_person", MONTH),
        ("nj_medical_expense_deduction", YEAR),
        ("mi_household_resources", YEAR),
        ("nd_renters_refund_income", YEAR),
        ("agi_surtax", YEAR),
        ("ssi_engaged_in_sga", YEAR),
    )
    for variable, period in invariant_consumers:
        np.testing.assert_allclose(
            moved.calculate(variable, period),
            baseline.calculate(variable, period),
            rtol=0,
            atol=0.02,
            err_msg=variable,
        )

    tax_status_sensitive_consumers = (
        "irs_employment_income",
        "payroll_tax_gross_wages",
        "ssi_earned_income",
        "adjusted_gross_income",
        "aca_magi",
        "medicaid_magi",
        "medicaid_magi_person",
        "medical_expense_health_insurance_premiums",
        "medicaid_medically_needy_medical_expenses",
    )
    for variable in tax_status_sensitive_consumers:
        np.testing.assert_allclose(
            baseline.calculate(variable, YEAR) - moved.calculate(variable, YEAR),
            transfer,
            rtol=0,
            atol=0.02,
            err_msg=variable,
        )

    # These categorically eligible individuals remain above the earned-income
    # exclusions. SSI's 50% earned-income disregard halves the wage change.
    np.testing.assert_allclose(
        baseline.calculate("ssi_countable_income", YEAR)
        - moved.calculate("ssi_countable_income", YEAR),
        transfer / 2,
        rtol=0,
        atol=0.02,
    )

    for variable, state in (
        ("oh_insured_unreimbursed_medical_care_expense_amount", "OH"),
        ("mo_qualified_health_insurance_premiums", "MO"),
    ):
        np.testing.assert_allclose(
            baseline.calculate(variable, YEAR) - moved.calculate(variable, YEAR),
            transfer * (states == state),
            rtol=0,
            atol=0.02,
            err_msg=variable,
        )
