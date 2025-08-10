from policyengine_us.model_api import *


class hours_worked_last_week(Variable):
    value_type = float
    entity = Person
    label = "weekly hours worked on the previous week"
    unit = "hour"
    definition_period = YEAR
