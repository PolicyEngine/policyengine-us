from policyengine_us.model_api import *


class monthly_hours_worked(Variable):
    value_type = float
    entity = Person
    label = "average monthly hours worked"
    unit = "hour"
    documentation = "Hours worked per month on average."
    definition_period = MONTH
