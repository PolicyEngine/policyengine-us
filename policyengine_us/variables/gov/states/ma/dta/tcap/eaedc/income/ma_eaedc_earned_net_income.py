from policyengine_us.model_api import *


class ma_eaedc_earned_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC net earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500"  # (B) step 2

    def formula(spm_unit, period, parameters):
        # net income = (earned income - work-related-expense - $30)*(2/3) - dependent care deduction + unearned income
        p = parameters(period).gov.states.ma.dta.tcap.eaedc
        gross_earned_income = add(
            spm_unit, period, ["ma_eaedc_total_earned_income"]
        )
        monthly_income = gross_earned_income / MONTHS_IN_YEAR
        adjusted_monthly_income = (
            monthly_income - p.deductions.work_related_expenses
        )
        # Compute earned income after disregard, first four months has flat $30 then 1/3 disregard, the rest has $30 deduction.
        first_four_months_income = (
            (adjusted_monthly_income - p.deductions.income_disregard.flat)
            * (1 - p.deductions.income_disregard.percentage.rate)
            * p.deductions.income_disregard.percentage.months
        )
        remaining_months = max_(
            MONTHS_IN_YEAR - p.deductions.income_disregard.percentage.months, 0
        )
        reduced_remaining_monthly_income = max_(
            adjusted_monthly_income
            - p.deductions.income_disregard.percentage.months,
            0,
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
        return net_earned_income
