from policyengine_us.model_api import *


class monthly_hours_worked(Variable):
    value_type = float
    entity = Person
    label = "monthly hours worked"
    unit = USD
    documentation = "Monthly hours worked."
    definition_period = YEAR
