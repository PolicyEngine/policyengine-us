from policyengine_us.model_api import *


class work_hours_per_day(Variable):
    value_type = float
    entity = Person
    label = "Work hours per day"
    definition_period = YEAR
    unit = "hour"
