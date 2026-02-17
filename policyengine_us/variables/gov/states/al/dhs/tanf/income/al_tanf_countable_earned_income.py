from policyengine_us.model_api import *


class al_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF countable earned income"
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2022/04/Appendix-N-Sec-2-Public-Assistance-Payment-Manual.pdf#page=37"
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhs.tanf.income
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        work_expense = gross_earned * p.work_expense_rate
        # Child care is deducted from earned income per Section 3115.B
        childcare_expenses = spm_unit("childcare_expenses", period)
        return max_(gross_earned - work_expense - childcare_expenses, 0)
