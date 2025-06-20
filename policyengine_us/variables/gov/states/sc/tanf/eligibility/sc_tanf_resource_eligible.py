from policyengine_us.model_api import *


class sc_tanf_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina TANF resource eligible"
    definition_period = YEAR
    defined_for = StateCode.SC

    def formula(spm_unit, period, parameters):
        resource_limit = parameters(period).gov.states.sc.tanf.resources.limit
        countable_resources = add(
            spm_unit, period, ["sc_tanf_countable_resources"]
        )
        # Each driver's license can exclude one vehicle.
        adult_count = spm_unit("spm_unit_count_adults", period)
        vehicle_count = spm_unit.household("household_vehicles_owned", period)
        vehicle_value = spm_unit.household("household_vehicles_value", period)
        avg_vehicle_value = np.zeros_like(vehicle_count)
        mask = vehicle_count != 0
        avg_vehicle_value[mask] = vehicle_value[mask] / vehicle_count[mask]
        countable_vehicle_value = (
            vehicle_count - adult_count
        ) * avg_vehicle_value
        return (
            countable_resources + countable_vehicle_value
        ) <= resource_limit
