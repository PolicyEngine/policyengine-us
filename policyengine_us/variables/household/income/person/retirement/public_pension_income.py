from policyengine_us.model_api import *


class public_pension_income(Variable):
    value_type = float
    entity = Person
    label = "public pension income"
    unit = USD
    documentation = "Income from government employee pensions."
    definition_period = YEAR

    adds = [
        "tax_exempt_public_pension_income",
        "taxable_public_pension_income",
    ]
