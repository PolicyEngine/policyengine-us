from policyengine_us.model_api import *


class snap_utility_region_str(Variable):
    value_type = str
    entity = Household
    label = "SNAP utility region"
    definition_period = YEAR

    def formula(household, period):
        return household("snap_utility_region", period).decode_to_str()
