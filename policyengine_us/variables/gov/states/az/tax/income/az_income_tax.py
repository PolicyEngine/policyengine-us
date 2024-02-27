from policyengine_us.model_api import *


class az_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    adds = ["az_income_tax_before_refundable_credits"]
    subtracts = ["az_refundable_credits"]
