from policyengine_us.model_api import *


class ak_atap_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alaska ATAP gross income eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.470"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # Test 1: Total nonexempt gross monthly income <= 185% standard
        gross_income = spm_unit("ak_atap_gross_income", period)
        gross_income_limit = spm_unit("ak_atap_gross_income_limit", period)
        return gross_income <= gross_income_limit
