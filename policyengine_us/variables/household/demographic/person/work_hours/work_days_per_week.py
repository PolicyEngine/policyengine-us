from policyengine_us.model_api import *


class work_days_per_week(Variable):
    value_type = float
    entity = Person
    label = "Work days per week"
    definition_period = YEAR
    unit = "day"
