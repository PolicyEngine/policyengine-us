from policyengine_us.model_api import *


class ks_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS
    adds = ["adjusted_gross_income", "ks_agi_additions"]
    subtracts = ["ks_agi_subtractions"]
