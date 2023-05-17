from policyengine_us.model_api import *


class nc_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC
    adds = ["nc_income_tax_before_refundable_credits"]
    subtracts = ["nc_refundable_credits"]