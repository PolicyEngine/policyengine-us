from policyengine_us.model_api import *


class ak_atap_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.480"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        deduction = spm_unit("ak_atap_earned_income_deduction", period)
        return max_(gross_earned - deduction, 0)
