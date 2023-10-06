from policyengine_us.model_api import *


class ca_child_care_days(Variable):
    value_type = int
    entity = SPMUnit
    label = "California CalWORKs Child Care Days Per Month"
    definition_period = YEAR
    defined_for = StateCode.CA
