from policyengine_us.model_api import *


class snap_unit_prorate_people_count(Variable):
    value_type = int
    entity = SPMUnit
    label = "Number of people in SNAP unit subject to SNAP proration rules"
    definition_period = YEAR

    adds = ["is_snap_prorate_person"]
