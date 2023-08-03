from policyengine_us.model_api import *


class childcare_days_per_week(Variable):
    value_type = float
    entity = Person
    label = "Child care days per week"
    definition_period = YEAR
    unit = "day"
