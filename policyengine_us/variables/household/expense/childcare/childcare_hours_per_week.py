from policyengine_us.model_api import *


class childcare_hours_per_week(Variable):
    value_type = float
    entity = Person
    label = "Child care hours per week"
    definition_period = YEAR
    unit = "hour"

    def formula(person, period, parameters):
        days_per_week = person("childcare_days_per_week", period)
        hours_per_day = person("childcare_hours_per_day", period)
        return days_per_week * hours_per_day
