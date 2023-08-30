from policyengine_us.model_api import *


class property_tax_credits_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona income to calculate property tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    adds = [
        "capital_gains_excluded_from_taxable_income",
        "tax_exempt_interest_income",
        "public_pension_income",
        "adjusted_gross_income",
    ]