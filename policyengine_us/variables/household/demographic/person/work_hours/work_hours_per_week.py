from policyengine_us.model_api import *


class work_hours_per_week(Variable):
    value_type = float
    entity = Person
    label = "Work hours per week"
    definition_period = YEAR
    unit = "hour"

    def formula(person, period, parameters):
        days_per_week = person("work_days_per_week", period)
        hours_per_day = person("work_hours_per_day", period)
        return days_per_week * hours_per_day
