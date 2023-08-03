from policyengine_us.model_api import *


class nyc_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC income tax"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"
    adds = ["nyc_income_tax_before_refundable_credits"]
    subtracts = ["nyc_refundable_credits"]
