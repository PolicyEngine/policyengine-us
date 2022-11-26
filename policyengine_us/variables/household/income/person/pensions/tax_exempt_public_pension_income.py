from policyengine_us.model_api import *


class tax_exempt_public_pension_income(Variable):
    value_type = float
    entity = Person
    label = "Pension income"
    unit = USD
    documentation = "Tax-exempt income from government employee pensions."
    definition_period = YEAR
