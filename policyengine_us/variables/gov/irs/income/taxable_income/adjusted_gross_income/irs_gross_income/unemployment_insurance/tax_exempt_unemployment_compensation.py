from policyengine_us.model_api import *


class tax_exempt_unemployment_compensation(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt unemployment compensation"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        total_ui = person("unemployment_compensation", period)
        taxable_ui = person("taxable_unemployment_compensation", period)
        return total_ui - taxable_ui
