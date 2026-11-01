from policyengine_us.model_api import *


class local_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local tax"
    documentation = "Total local tax liability after refundable credits."
    unit = USD

    adds = [
        "local_income_tax_before_refundable_credits",
        "local_occupational_tax",
    ]
    subtracts = [
        "nyc_refundable_credits",
        "md_montgomery_eitc",
    ]
