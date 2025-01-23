from policyengine_us.model_api import *


class ma_eaedc_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC net income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500"  # (B) step 2

    def formula(spm_unit, period, parameters):
        # net icnome = (earned income - work-related-expense)*($30 and 1/3) - dependent_care_deduction + unearned income
        p = parameters(period).gov.states.ma.dta.tcap.eaedc
        gross_earned_income = add(
            spm_unit, period, ["ma_eaedc_non_disabled_earned_income"]
        )
        adjusted_earned_income = (
            gross_earned_income - p.deductions.work_related_expense
        )
        monthly_income = adjusted_earned_income / MONTHS_IN_YEAR
        # Compute earned income after disregard, first four months has flat $30 then 1/3 disregard, the rest has $30 deduction.
        first_four_months_income = (
            (monthly_income - p.deductions.income_disregards.amount)
            * p.deductions.income_disregards.rate
            * p.deductions.income_disregards.months
        )
        remaining_months = max_(
            MONTHS_IN_YEAR - p.deductions.income_disregards.months, 0
        )
        reduced_remaining_monthly_income = max_(
            monthly_income - p.deductions.income_disregards.amount, 0
        )
        remaining_income = reduced_remaining_monthly_income * remaining_months
        earned_income_after_disregard = (
            first_four_months_income + remaining_income
        )
        # dependent care deduction
        dependent_care_deduction = spm_unit(
            "ma_eaedc_dependent_care_deduction", period
        )

        net_earned_income = max_(
            earned_income_after_disregard - dependent_care_deduction, 0
        )
        unearned_income = add(spm_unit, period, ["ma_eaedc_unearned_income"])
        return unearned_income + net_earned_income
