from policyengine_us.model_api import *


class ny_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    adds = ["ny_income_tax_before_refundable_credits"]
    subtracts = ["ny_refundable_credits"]
