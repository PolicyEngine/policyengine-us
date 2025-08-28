from policyengine_us.model_api import *


class az_liheap_crisis_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona LIHEAP crisis assistance"
    definition_period = YEAR
    defined_for = "az_liheap_eligible"
    reference = "https://des.az.gov/services/basic-needs/liheap"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap

        # Crisis assistance is up to the maximum amount
        # In the microsimulation, we'll use a fraction of the maximum
        # based on assumed crisis probability
        # This should be parameterized when actual crisis data is available

        # For now, return 0 as crisis assistance requires specific crisis conditions
        # which aren't currently modeled in the microsimulation
        return 0 * p.crisis_assistance_maximum
