from policyengine_us.model_api import *


class al_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF countable earned income"
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2022/04/Appendix-N-Sec-2-Public-Assistance-Payment-Manual.pdf#page=30"
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        gross_earned = spm_unit("al_tanf_gross_earned_income", period)
        work_expense = spm_unit("al_tanf_work_expense_deduction", period)
        return max_(gross_earned - work_expense, 0)
