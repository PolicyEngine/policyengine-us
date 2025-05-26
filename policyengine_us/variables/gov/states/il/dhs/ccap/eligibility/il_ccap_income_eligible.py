from policyengine_us.model_api import *


class il_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Illinois Child Care Assistance Program (CCAP) due to income"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-50.230"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.income_limit
        countable_income = spm_unit("il_ccap_countable_income", period)
        # 225% fpg
        fpg = spm_unit("spm_unit_fpg", period)
        income_limit = fpg * p.rate
        return countable_income < income_limit
