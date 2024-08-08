from policyengine_us.model_api import *


class earned_income(Variable):
    value_type = float
    entity = Person
    label = "Earned income"
    unit = USD
    documentation = "Income from wages or self-employment"
    definition_period = YEAR

    adds = ["irs_employment_income", "self_employment_income"]
