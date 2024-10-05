from policyengine_us.model_api import *


class md_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    adds = ["md_income_tax_before_refundable_credits"]
    subtracts = ["md_refundable_credits"]
