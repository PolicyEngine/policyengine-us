from policyengine_us.model_api import *


class ca_liheap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP categorically income eligible"
    defined_for = StateCode.CA
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=6,217,218"

    def formula(spm_unit, period, parameters):
        return (spm_unit("snap", period) > 0) | (spm_unit("ca_tanf", period) > 0)
