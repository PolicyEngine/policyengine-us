from policyengine_us.model_api import *


class taxable_pension_income(Variable):
    value_type = float
    entity = Person
    label = "taxable pension income"
    unit = USD
    definition_period = YEAR

    adds = ["taxable_public_pension_income", "taxable_private_pension_income"]
