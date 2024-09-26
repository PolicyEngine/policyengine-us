from policyengine_us.model_api import *


class weekly_hours_worked(Variable):
    value_type = float
    entity = Person
    label = "Weekly hours"
    documentation = "Average weekly hours worked"
    definition_period = YEAR
    unit = "hour"
    quantity_type = FLOW

    def formula(person, period, parameters):
        return person("hours_worked", period) / WEEKS_IN_YEAR
