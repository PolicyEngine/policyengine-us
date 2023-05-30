from policyengine_us.model_api import *


class nj_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    adds = [
        "nj_property_tax_credit",
        "nj_eitc",
        "nj_cdcc",
        "nj_child_tax_credit",
    ]
