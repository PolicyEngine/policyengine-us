from policyengine_us.model_api import *


class ca_capi_countable_vehicle_value(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "California CAPI countable vehicle value"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf"

    def formula(spm_unit, period, parameters):
        vehicle_value = spm_unit.household("household_vehicles_value", period)
        p = parameters(period).gov.states.ca.cdss.capi.resources.vehicle
        return max_(vehicle_value - p.disregard, 0)
