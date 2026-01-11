from policyengine_us.model_api import *


class hi_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF maximum benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf#page=22",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.tanf

        unit_size = spm_unit("spm_unit_size", period)
        capped_size = min_(unit_size, p.max_unit_size)

        # Get Standard of Need for household size
        son = p.standard_of_need.amount[capped_size]

        # Standard of Assistance = SON × 48%
        # NOTE: SOA is reduced by 20% after the family receives their initial
        # two full months of benefits for mandatory work-required households.
        # This reduction cannot be modeled as PolicyEngine cannot track
        # cumulative months of benefit receipt.
        return son * p.standard_of_assistance.rate
