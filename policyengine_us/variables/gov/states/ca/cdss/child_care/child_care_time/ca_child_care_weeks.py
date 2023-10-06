from policyengine_us.model_api import *


class ca_child_care_weeks(Variable):
    value_type = int
    entity = SPMUnit
    label = "California CalWORKs Child Care Weeks Per Month"
    definition_period = YEAR
    defined_for = StateCode.CA
