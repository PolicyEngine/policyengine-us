from policyengine_us.model_api import *


class ca_scc_general_assistance_countable_vehicle_value(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    label = "Santa Clara County General Assistance countable vehicle value"
    defined_for = "in_scc"
    reference = "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/08Property/Motor_Vehicle.htm"

    def formula(spm_unit, period, parameters):
        # One vehicle is exempt only if its equity is within the limit; a
        # vehicle over the limit counts in full, as do additional vehicles.
        # We use the household-average vehicle value as a proxy for each
        # vehicle's equity (encumbrances are not modeled).
        p = parameters(period).gov.local.ca.scc.general_assistance.personal_property
        household = spm_unit.household
        vehicle_count = household("household_vehicles_owned", period)
        vehicle_value = household("household_vehicles_value", period)
        average_vehicle_value = where(
            vehicle_count > 0,
            vehicle_value / max_(vehicle_count, 1),
            0,
        )
        # The handbook Motor Vehicle chapter exempts a vehicle valued "up to
        # $4,650 or less" (inclusive); the GA-62 summary sheet says "worth
        # less than $4,650". We follow the operational handbook chapter.
        one_vehicle_exempt = average_vehicle_value <= p.vehicle_value_limit
        return vehicle_value - one_vehicle_exempt * average_vehicle_value
