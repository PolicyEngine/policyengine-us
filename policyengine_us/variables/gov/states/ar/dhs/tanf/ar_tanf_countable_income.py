from policyengine_us.model_api import *


class ar_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = StateCode.AR

    def formula(spm_unit, period, parameters):
        countable_earned = spm_unit("ar_tanf_countable_earned_income", period)
        unearned = spm_unit("tanf_gross_unearned_income", period)
        return countable_earned + unearned
