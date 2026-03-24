from policyengine_us.model_api import *


class mo_kansas_city_earnings_tax_taxable_earnings(Variable):
    value_type = float
    entity = Person
    label = "Kansas City earnings tax taxable earnings"
    documentation = "Earnings subject to Kansas City's 1% earnings tax for this person."
    unit = USD
    definition_period = YEAR
    default_value = 0
