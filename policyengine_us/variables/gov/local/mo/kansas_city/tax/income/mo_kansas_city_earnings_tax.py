from policyengine_us.model_api import *


class mo_kansas_city_earnings_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas City earnings tax"
    documentation = (
        "Kansas City earnings tax based on explicit taxable earnings inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = "https://www.kcmo.gov/city-hall/departments/finance/earnings-tax"
    adds = ["mo_kansas_city_earnings_tax_person"]
