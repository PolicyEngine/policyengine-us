from policyengine_us.model_api import *


class ct_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    adds = ["ct_income_tax_before_refundable_credits"]
    subtracts = ["ct_refundable_credits"]
