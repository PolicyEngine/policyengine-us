from policyengine_us.model_api import *


class interest_income(Variable):
    value_type = float
    entity = Person
    label = "interest income"
    documentation = "Interest income from bonds, savings accounts, CDs, etc."
    unit = USD
    definition_period = YEAR
    adds = [
        "tax_exempt_interest_income",
        "taxable_interest_income",
    ]
