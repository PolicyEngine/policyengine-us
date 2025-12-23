from policyengine_us.model_api import *


class earned_income_before_lsr(Variable):
    value_type = float
    entity = Person
    label = "Earned income (before labor supply response)"
    unit = USD
    documentation = (
        "Income from wages or self-employment, before behavioral responses"
    )
    definition_period = YEAR

    adds = [
        "employment_income_before_lsr",
        "self_employment_income_before_lsr",
    ]
