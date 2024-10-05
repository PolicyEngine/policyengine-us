from policyengine_us.model_api import *


class nm_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    adds = ["nm_income_tax_before_refundable_credits"]
    subtracts = ["nm_refundable_credits"]
