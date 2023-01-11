from policyengine_us.model_api import *


class tax_exempt_unemployment_compensation(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt unemployment compensation"
    unit = USD
    definition_period = YEAR

    adds = ["unemployment_compensation"]
    subtracts = ["taxable_unemployment_compensation"]
