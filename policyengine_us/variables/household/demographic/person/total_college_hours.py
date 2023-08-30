from policyengine_us.model_api import *


class total_college_hours(Variable):
    value_type = float
    entity = Person
    label = "Total annual hours of college attended"
    unit = "hour"
    definition_period = YEAR
