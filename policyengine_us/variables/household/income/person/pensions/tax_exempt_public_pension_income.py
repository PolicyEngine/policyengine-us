from policyengine_us.model_api import *


class pension_income(Variable):
    value_type = float
    entity = Person
    label = "Pension income"
    unit = USD
    documentation = "Income from pensions, annuitities, life insurance or endowment contracts."
    definition_period = YEAR

