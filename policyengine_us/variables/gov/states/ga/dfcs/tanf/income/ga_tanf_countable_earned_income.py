from policyengine_us.model_api import *


class ga_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = ("https://pamms.dhs.ga.gov/dfcs/tanf/1615/",)
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # Use federal TANF gross earned income variable
        gross_earned = spm_unit.sum(person("tanf_gross_earned_income", period))
        # Georgia only allows $250 standard work expense deduction
        # per PAMMS Section 1615 and 1605
        work_expense = spm_unit("ga_tanf_work_expense_deduction", period)
        return max_(gross_earned - work_expense, 0)
