from policyengine_us.model_api import *


class snap_region_str(Variable):
    value_type = str
    entity = Household
    label = "SNAP region"
    definition_period = YEAR

    def formula(household, period):
        return household("snap_region", period).decode_to_str()
