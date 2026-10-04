from policyengine_us.model_api import *


class ca_liheap_utility_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP utility heating eligibility"
    defined_for = StateCode.CA
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=9,182,183,184,193,202,203,205,219,279"

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        utility_heat = (heating_type == types.ELECTRICITY) | (
            heating_type == types.NATURAL_GAS
        )
        return utility_heat & spm_unit("ca_liheap_basic_eligible", period)
