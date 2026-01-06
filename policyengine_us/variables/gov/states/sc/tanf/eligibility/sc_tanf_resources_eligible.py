from policyengine_us.model_api import *


class sc_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina TANF resources eligible"
    definition_period = MONTH
    defined_for = StateCode.SC

    def formula(spm_unit, period, parameters):
        resource_limit = parameters(period).gov.states.sc.tanf.resources.limit
        countable_resources = spm_unit("sc_tanf_countable_resources", period)
        # Each driver's license can exclude one vehicle.
        adult_count = spm_unit("spm_unit_count_adults", period.this_year)
        vehicle_count = spm_unit.household(
            "household_vehicles_owned", period.this_year
        )
        vehicle_value = spm_unit.household(
            "household_vehicles_value", period.this_year
        )
        avg_vehicle_value = np.zeros_like(vehicle_count)
        mask = vehicle_count != 0
        avg_vehicle_value[mask] = vehicle_value[mask] / vehicle_count[mask]
        countable_vehicle_value = (
            vehicle_count - adult_count
        ) * avg_vehicle_value
        return (
            countable_resources + countable_vehicle_value
        ) <= resource_limit
