from policyengine_us.model_api import *


class ga_tanf_earned_income_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF earned income disregard"
    unit = USD
    definition_period = MONTH
    reference = ("https://pamms.dhs.ga.gov/dfcs/tanf/1615/",)
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ga.dfcs.tanf.income.deductions.earned_income_disregard

        gross_earned = spm_unit("ga_tanf_gross_earned_income", period)
        work_expense = spm_unit("ga_tanf_work_expense_deduction", period)

        # Calculate income after work expense
        income_after_work_expense = max_(gross_earned - work_expense, 0)

        # Flat disregard amount
        flat_disregard = p.flat_amount

        # Percentage disregard (1/3) - applied only in first 4 months
        # For now, we apply the most generous interpretation:
        # $30 + 1/3 of remaining income after work expense
        percentage_disregard = p.percentage * income_after_work_expense

        # Total disregard is flat amount plus percentage of remaining
        total_disregard = flat_disregard + percentage_disregard

        # Apply only if there is earned income
        has_earned_income = gross_earned > 0
        return where(has_earned_income, total_disregard, 0)
