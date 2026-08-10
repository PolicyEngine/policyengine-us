from policyengine_us.model_api import *


class ca_cc_general_assistance_countable_vehicle_value(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    label = "Contra Costa County General Assistance countable vehicle value"
    defined_for = "in_cc"
    reference = "https://ehsd.org/wp-content/uploads/2024/08/GA-Brochure_ENGLISH_July2024_FA_Digital.pdf#page=2"

    def formula(spm_unit, period, parameters):
        # One vehicle is exempt only if valued within the limit; a vehicle
        # over the limit counts in full, as do additional vehicles. We use
        # the household-average vehicle value as a proxy for each vehicle's
        # value.
        p = parameters(period).gov.local.ca.cc.general_assistance.personal_property
        household = spm_unit.household
        vehicle_count = household("household_vehicles_owned", period)
        vehicle_value = household("household_vehicles_value", period)
        average_vehicle_value = where(
            vehicle_count > 0,
            vehicle_value / max_(vehicle_count, 1),
            0,
        )
        one_vehicle_exempt = average_vehicle_value <= p.vehicle_value_limit
        return vehicle_value - one_vehicle_exempt * average_vehicle_value
