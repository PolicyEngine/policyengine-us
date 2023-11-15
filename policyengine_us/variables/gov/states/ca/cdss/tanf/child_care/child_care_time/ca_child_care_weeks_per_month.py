from policyengine_us.model_api import *


class ca_child_care_weeks_per_month(Variable):
    value_type = int
    entity = Person
    label = "California CalWORKs Child Care weeks per month"
    definition_period = YEAR
    defined_for = StateCode.CA
