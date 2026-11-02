from policyengine_us.model_api import *


class ca_liheap_utility_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP utility heating eligibility"
    defined_for = StateCode.CA
    # PDF pages 9,182-184,193,202-203,205,219,264-265,279
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=9"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.eligibility
        heating_type = spm_unit("heating_type", period)
        utility_heat = np.isin(heating_type.decode_to_str(), p.utility_heating_fuels)
        return utility_heat & spm_unit("ca_liheap_basic_eligible", period)
