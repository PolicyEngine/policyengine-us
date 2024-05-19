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


class weekly_hours_worked_behavioural_response_income_elasticity(Variable):
    value_type = float
    entity = Person
    label = "behavioural response in weekly hours worked (income effect)"
    unit = "hour"
    definition_period = YEAR

    def formula(person, period, parameters):
        original = person("weekly_hours_worked_before_lsr", period)
        lsr = person("labor_supply_behavioral_response", period)
        if (lsr != 0).any():
            income_effect = person("income_elasticity_lsr", period)
        else:
            income_effect = 0
        original_emp = person("employment_income_before_lsr", period)
        original_self_emp = person("self_employment_income_before_lsr", period)
        original_earnings = original_emp + original_self_emp
        lsr_relative_change = np.where(
            original_earnings == 0, 0, income_effect / original_earnings
        )
        return original * lsr_relative_change


class weekly_hours_worked_behavioural_response_substitution_elasticity(
    Variable
):
    value_type = float
    entity = Person
    label = "behavioural response in weekly hours worked (substitution effect)"
    unit = "hour"
    definition_period = YEAR

    def formula(person, period, parameters):
        original = person("weekly_hours_worked_before_lsr", period)
        lsr = person("labor_supply_behavioral_response", period)
        if (lsr != 0).any():
            substitution_effect = person("substitution_elasticity_lsr", period)
        else:
            substitution_effect = 0
        original_emp = person("employment_income_before_lsr", period)
        original_self_emp = person("self_employment_income_before_lsr", period)
        original_earnings = original_emp + original_self_emp
        lsr_relative_change = np.where(
            original_earnings == 0, 0, substitution_effect / original_earnings
        )
        return original * lsr_relative_change


class weekly_hours_worked_behavioural_response(Variable):
    value_type = float
    entity = Person
    label = "behavioural response in weekly hours worked"
    unit = "hour"
    definition_period = YEAR
    adds = [
        "weekly_hours_worked_behavioural_response_income_elasticity",
        "weekly_hours_worked_behavioural_response_substitution_elasticity",
    ]
