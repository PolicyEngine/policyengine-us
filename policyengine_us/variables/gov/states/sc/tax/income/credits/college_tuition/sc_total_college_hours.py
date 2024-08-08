from policyengine_us.model_api import *


class sc_total_college_hours(Variable):
    value_type = float
    entity = Person
    label = "South Carolina's total annual hours of college attended"  # excluding summer and interim
    unit = "hour"
    definition_period = YEAR
