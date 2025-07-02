from policyengine_us.model_api import *


class work_hours_per_week(Variable):
    value_type = float
    entity = Person
    label = "Work hours per week"
    definition_period = YEAR
    unit = "hour"
