from policyengine_us.model_api import *


class sc_tanf_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF net income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://dss.sc.gov/media/3926/tanf_policy_manual_vol-60.pdf#page=131"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income.earned.disregard
        gross_earned_income = add(spm_unit, period, ["sc_tanf_earned_income"])
        monthly_income = gross_earned_income / MONTHS_IN_YEAR
        # Compute earned income after disregard, first four months has 50% disregard, the rest has $100 deduction.
        first_four_months_income = (
            monthly_income * p.percentage.rate * p.percentage.months
        )
        remaining_months = max_(MONTHS_IN_YEAR - p.percentage.months, 0)
        reduced_remaining_monthly_income = max_(monthly_income - p.amount, 0)
        remaining_income = reduced_remaining_monthly_income * remaining_months
        earned_income_after_disregard = (
            first_four_months_income + remaining_income
        )
        # exclude child support
        child_support = add(spm_unit, period, ["child_support_received"])
        net_earned_income = max_(
            earned_income_after_disregard - child_support, 0
        )
        unearned_income = add(spm_unit, period, ["sc_tanf_unearned_income"])
        return unearned_income + net_earned_income
