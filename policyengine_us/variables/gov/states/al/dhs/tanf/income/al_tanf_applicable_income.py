from policyengine_us.model_api import *


class al_tanf_applicable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alabama TANF Applicable Earned Income"
    defined_for = StateCode.AL
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        # Get the total earned income.
        total_earned_income = spm_unit("al_tanf_earned_income", period)
        # Get work expense deductions
        work_expense_deduction = spm_unit(
            "al_tanf_work_expense_deduction", period
        )
        # Get net self-employment income
        net_self_employment_income = spm_unit(
            "al_tanf_self_employment_net_income", period
        )
        # Calculate earned income after deductions
        applicable_earned_income = max_(
            total_earned_income
            + net_self_employment_income
            - work_expense_deduction,
            0,
        )
        # Get the total unearned income.
        total_unearned_income = spm_unit("al_tanf_unearned_income", period)
        # Total applicable income is earned income after deductions plus unearned income
        return applicable_earned_income + total_unearned_income
