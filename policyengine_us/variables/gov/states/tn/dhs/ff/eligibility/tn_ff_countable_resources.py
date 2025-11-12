from policyengine_us.model_api import *


class tn_ff_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First countable resources"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Start with total household assets
        assets = spm_unit("spm_unit_assets", period)
        # Apply vehicle exemption - exempt up to $4,600 of equity in one vehicle
        p = parameters(period).gov.states.tn.dhs.ff.resources
        vehicle_exemption = p.vehicle_exemption
        # For simplification, apply the vehicle exemption as a deduction
        countable = max_(assets - vehicle_exemption, 0)
        return countable
