from policyengine_us.model_api import *


class ca_liheap_wood_heating(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = (
        "California LIHEAP ordinary wood heating component with approved delivery cost"
    )
    defined_for = "ca_liheap_basic_eligible"
    # PDF pages 10,188
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=10"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.payment
        heating_type = spm_unit("heating_type", period)
        approved_cost = spm_unit("ca_liheap_approved_wood_delivery_cost", period)
        return where(
            heating_type == heating_type.possible_values.WOOD,
            clip(approved_cost, 0, p.wpo_maximum),
            0,
        )
