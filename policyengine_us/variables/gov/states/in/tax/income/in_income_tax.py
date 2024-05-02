from policyengine_us.model_api import *


class in_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana income tax"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/6"
    defined_for = StateCode.IN

    adds = ["in_income_tax_before_refundable_credits"]
    subtracts = ["in_refundable_credits"]
