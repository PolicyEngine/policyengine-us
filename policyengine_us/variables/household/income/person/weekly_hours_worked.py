from policyengine_us.model_api import *


class weekly_hours_worked(Variable):
    value_type = float
    entity = Person
    label = "average weekly hours worked"
    unit = "hour"
    documentation = "Hours worked per week on average."
    definition_period = YEAR
    adds = [
        "weekly_hours_worked_before_lsr",
        "weekly_hours_worked_behavioural_response",
    ]


class weekly_hours_worked_before_lsr(Variable):
    value_type = float
    entity = Person
    label = "average weekly hours worked (before labor supply responses)"
    unit = "hour"
    definition_period = YEAR


class weekly_hours_worked_behavioural_response(Variable):
    value_type = float
    entity = Person
    label = "behavioural response in weekly hours worked"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        original = person("weekly_hours_worked_before_lsr", period)
        lsr = person("labor_supply_behavioral_response", period)
        original_emp = person("employment_income_before_lsr", period)
        original_self_emp = person("self_employment_income_before_lsr", period)
        original_earnings = original_emp + original_self_emp
        lsr_relative_change = np.where(
            original_earnings == 0, 0, lsr / original_earnings
        )
        return original * lsr_relative_change
