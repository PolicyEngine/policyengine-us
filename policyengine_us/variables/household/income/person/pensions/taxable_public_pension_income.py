from policyengine_us.model_api import *


class taxable_public_pension_income(Variable):
    value_type = float
    entity = Person
    label = "taxable public pension income"
    unit = USD
    documentation = "Taxable income from government employee pensions."
    definition_period = YEAR
