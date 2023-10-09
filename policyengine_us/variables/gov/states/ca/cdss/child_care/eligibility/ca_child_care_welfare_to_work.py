from policyengine_us.model_api import *


class ca_child_care_welfare_to_work(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Welfare to Work"
    unit = "hour"
    definition_period = YEAR
    defined_for = StateCode.CA
