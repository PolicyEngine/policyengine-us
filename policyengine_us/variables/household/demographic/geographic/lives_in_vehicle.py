from policyengine_us.model_api import *


class lives_in_vehicle(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    documentation = "Whether a household is using their vehicle as their primary residence "
    label = "Lives in vehicle"

    def formula(household, period, parameters):
        # Assuming that the household has to be considered homeless
        # and own at least one vehicle
        is_homeless = household("is_homeless", period)
        total_vehicles_owned = household("household_vehicles_owned", period)
        return is_homeless & (total_vehicles_owned > 0)
