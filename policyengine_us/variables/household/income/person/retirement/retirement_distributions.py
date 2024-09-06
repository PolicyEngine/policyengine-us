from policyengine_us.model_api import *


class retirement_distributions(Variable):
    value_type = float
    entity = Person
    label = "Retirement account distributions"
    unit = USD
    definition_period = YEAR
    adds = [
        "taxable_retirement_distributions",
        "tax_exempt_retirement_distributions",
    ]
