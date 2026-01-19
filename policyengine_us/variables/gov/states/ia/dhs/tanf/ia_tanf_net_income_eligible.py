from policyengine_us.model_api import *


class ia_tanf_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa TANF net income eligible (Test 2)"
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"

    def formula(spm_unit, period, parameters):
        gross_income = spm_unit("ia_tanf_gross_income", period)
        gross_earned_income = spm_unit("ia_tanf_gross_earned_income", period)
        standard_of_need = spm_unit("ia_tanf_standard_of_need", period)
        p = parameters(period).gov.states.ia.dhs.tanf.income
        earned_income_deduction = (
            gross_earned_income * p.earned_income_deduction
        )
        net_income = gross_income - earned_income_deduction
        return net_income < standard_of_need
