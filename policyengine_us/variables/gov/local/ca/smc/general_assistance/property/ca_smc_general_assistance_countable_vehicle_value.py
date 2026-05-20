from policyengine_us.model_api import *


class ca_smc_general_assistance_countable_vehicle_value(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Mateo County General Assistance countable vehicle value"
    definition_period = YEAR
    defined_for = "in_smc"
    reference = "https://www.smcgov.org/media/153295/download?inline=#page=2"

    def formula(spm_unit, period, parameters):
        household = spm_unit.household
        vehicle_count = household("household_vehicles_owned", period)
        vehicle_value = household("household_vehicles_value", period)
        average_vehicle_value = where(
            vehicle_count > 0,
            vehicle_value / vehicle_count,
            0,
        )
        return average_vehicle_value * max_(vehicle_count - 1, 0)
