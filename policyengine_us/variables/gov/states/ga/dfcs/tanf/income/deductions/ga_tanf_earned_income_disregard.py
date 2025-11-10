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

        person = spm_unit.members
        # Use federal TANF gross earned income variable
        gross_earned = spm_unit.sum(person("tanf_gross_earned_income", period))
        work_expense = spm_unit("ga_tanf_work_expense_deduction", period)

        # Calculate income after work expense
        income_after_work_expense = max_(gross_earned - work_expense, 0)

        # Flat disregard amount
        flat_disregard = p.flat_amount

        # Percentage disregard (1/3)
        # NOTE: In the full Georgia TANF policy, this disregard varies by time:
        # - Months 1-4: $30 + 1/3 of remaining income
        # - Months 5-12: $30 only
        # - Month 13+: No disregard
        # For this simplified implementation, we do not model time limits
        # and apply the most generous interpretation ($30 + 1/3) to all recipients
        percentage_disregard = p.percentage * income_after_work_expense

        # Total disregard is flat amount plus percentage of remaining
        total_disregard = flat_disregard + percentage_disregard

        # Apply only if there is earned income
        has_earned_income = gross_earned > 0
        return where(has_earned_income, total_disregard, 0)
