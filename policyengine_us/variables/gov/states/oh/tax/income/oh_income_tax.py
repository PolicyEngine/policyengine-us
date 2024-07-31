from policyengine_us.model_api import *


class oh_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
    adds = ["oh_income_tax_before_refundable_credits"]
    subtracts = ["oh_refundable_credits"]
