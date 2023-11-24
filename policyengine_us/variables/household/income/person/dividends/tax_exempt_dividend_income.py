from policyengine_us.model_api import *


class tax_exempt_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "tax-exempt dividend income"
    unit = USD
    definition_period = YEAR
