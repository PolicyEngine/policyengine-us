from policyengine_us.model_api import *


class in_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana income tax before refundable credits"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/6"
    defined_for = StateCode.IN

    adds = ["in_agi_tax", "in_use_tax"]
