from policyengine_us.model_api import *


class is_any_family_members_over_60(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Is any family members over 60"
    definition_period = YEAR
    defined_for = StateCode.NY
