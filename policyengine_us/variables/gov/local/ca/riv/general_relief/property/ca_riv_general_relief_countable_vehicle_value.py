from policyengine_us.model_api import *


class ca_riv_general_relief_countable_vehicle_value(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Riverside County General Relief countable vehicle value"
    definition_period = YEAR
    defined_for = "in_riv"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.local.ca.riv.general_relief.property.vehicle_exemption
        total_vehicle_value = spm_unit.household(
            "household_vehicles_value", period
        )
        return max_(total_vehicle_value - p.amount, 0)
