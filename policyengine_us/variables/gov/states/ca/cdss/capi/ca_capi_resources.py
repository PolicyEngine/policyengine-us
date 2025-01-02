from policyengine_us.model_api import *


class ca_capi_resources(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "California CAPI resources"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf"

    def formula(spm_unit, period, parameters):
        general_resources = add(spm_unit, period, ["ssi_countable_resources"])
        vehicle_value = spm_unit.household("household_vehicles_value", period)
        p = parameters(period).gov.states.ca.cdss.capi.resources
        countable_vehicle_value = max_(
            vehicle_value - p.vehicle_value_threshold, 0
        )
        return general_resources + countable_vehicle_value
