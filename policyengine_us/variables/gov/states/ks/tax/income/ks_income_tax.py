from policyengine_us.model_api import *


class ks_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas income tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS
    adds = ["ks_income_tax_before_refundable_credits"]
    subtracts = ["ks_refundable_credits"]
