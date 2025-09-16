from policyengine_us.model_api import *


class snap_unit_ineligible_people(Variable):
    value_type = int
    entity = SPMUnit
    label = "Number of ineligible people in SNAP unit"
    definition_period = YEAR

    adds = ["is_snap_ineligible_member_based_on_immigration_status"]
