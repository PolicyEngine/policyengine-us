from policyengine_us.model_api import *


class ca_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP income eligible"
    defined_for = StateCode.CA
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=6,9,184"

    def formula(spm_unit, period, parameters):
        return spm_unit("ca_liheap_categorically_eligible", period) | (
            spm_unit("ca_liheap_countable_income", period)
            <= spm_unit("ca_liheap_income_limit", period)
        )
