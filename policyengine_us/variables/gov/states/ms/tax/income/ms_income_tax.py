from policyengine_us.model_api import *


class ms_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    adds = ["ms_income_tax_before_refundable_credits"]
    subtracts = ["ms_refundable_credits"]
