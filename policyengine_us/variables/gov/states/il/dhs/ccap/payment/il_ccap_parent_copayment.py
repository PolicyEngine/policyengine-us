from policyengine_us.model_api import *


class il_ccap_parent_copayment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Child Care Assistance Program (CCAP) parent co-payment"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-50.320"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap
        countable_income = spm_unit("il_ccap_countable_income", period)
        size = spm_unit("spm_unit_size", period)
        # Parents need to pay this minimum amount to day care provider
        # The CCAP will help parents pay the rest of the childcare expense
        return p.parent_copayment[size].calc(countable_income) # create separate parameter file for size 
