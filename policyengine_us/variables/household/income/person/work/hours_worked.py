from policyengine_us.model_api import *


class hours_worked(Variable):
    value_type = float
    entity = Person
    label = "Total amount of hours worked by this person"
    definition_period = YEAR
    unit = "hour"
