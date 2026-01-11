from policyengine_us.model_api import *


class al_tanf_work_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF work expense deduction"
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2022/04/Appendix-N-Sec-2-Public-Assistance-Payment-Manual.pdf#page=30"
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhs.tanf.income
        gross_earned = spm_unit("al_tanf_gross_earned_income", period)
        return gross_earned * p.work_expense_rate
