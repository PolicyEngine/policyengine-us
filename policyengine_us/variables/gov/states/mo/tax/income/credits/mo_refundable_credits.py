from policyengine_us.model_api import *


class mo_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri refundable credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.177&bid=49978&hl="
    )
    defined_for = StateCode.MA
    adds = ["mo_wftc", "mo_property_tax_credit"]
