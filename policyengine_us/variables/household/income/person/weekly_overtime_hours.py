from policyengine_us.model_api import *


class weekly_overtime_hours(Variable):
    value_type = float
    entity = Person
    label = "average weekly overtime hours worked"
    unit = "hour"
    documentation = "Hours worked per week on average."
    definition_period = YEAR

    def formula(person, period, parameters):
        weekly_hours_worked = person("weekly_hours_worked", period)
        full_time_worker = person("works_full_time", period)
        part_time_hours = parameters(period).gov.dol.part_time_hours
        hour_threshold = where(
            full_time_worker, part_time_hours * 2, part_time_hours
        )
        return max_(weekly_hours_worked - hour_threshold, 0)
