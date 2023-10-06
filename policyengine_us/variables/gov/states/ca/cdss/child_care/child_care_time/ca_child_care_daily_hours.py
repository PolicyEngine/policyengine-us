from policyengine_us.model_api import *


class ca_child_care_daily_hours(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Daily Child Care Hour"
    definition_period = YEAR
    defined_for = StateCode.CA
