from policyengine_us.model_api import *


class earned_income_last_year(Variable):
    value_type = float
    entity = Person
    label = "Earned income last year"
    unit = USD
    documentation = "Prior-year income from wages or self-employment"
    definition_period = YEAR

    adds = ["employment_income_last_year", "self_employment_income_last_year"]
