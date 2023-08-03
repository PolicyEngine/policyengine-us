from policyengine_us.model_api import *


class private_pension_income(Variable):
    value_type = float
    entity = Person
    label = "private pension income"
    unit = USD
    documentation = "Income from non-government employee pensions."
    definition_period = YEAR

    adds = [
        "tax_exempt_private_pension_income",
        "taxable_private_pension_income",
    ]
