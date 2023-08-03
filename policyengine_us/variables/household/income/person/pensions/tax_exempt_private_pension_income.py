from policyengine_us.model_api import *


class tax_exempt_private_pension_income(Variable):
    value_type = float
    entity = Person
    label = "tax-exempt private pension income"
    unit = USD
    documentation = "Tax-exempt income from non-government employee pensions."
    definition_period = YEAR
