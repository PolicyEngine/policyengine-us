from policyengine_us.model_api import *


class employment_income_last_year(Variable):
    value_type = float
    entity = Person
    label = "employment income last year"
    documentation = (
        "Wages and salaries in prior year, including tips and commissions."
    )
    unit = USD
    definition_period = YEAR
