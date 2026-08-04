from policyengine_us.model_api import *


class monthly_hours_worked(Variable):
    value_type = float
    entity = Person
    label = "Average monthly hours worked"
    unit = "hour"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("hours_worked_last_week", period) * WEEKS_IN_YEAR / MONTHS_IN_YEAR
