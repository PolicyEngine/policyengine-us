from policyengine_us.model_api import *


class ak_atap_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alaska ATAP net income eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.470"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # Test 2: Countable income (after deductions) <= need standard
        countable_income = spm_unit("ak_atap_countable_income", period)
        need_standard = spm_unit("ak_atap_need_standard", period)
        return countable_income <= need_standard
