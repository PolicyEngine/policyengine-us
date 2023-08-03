from policyengine_us.model_api import *


class wa_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA
    adds = ["wa_capital_gains_tax"]
