from policyengine_us.model_api import *


class taxable_private_pension_income(Variable):
    value_type = float
    entity = Person
    label = "taxable private pension income"
    unit = USD
    documentation = "Taxable income from non-government employee pensions."
    definition_period = YEAR
