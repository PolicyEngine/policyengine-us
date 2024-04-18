from policyengine_us.model_api import *


class ks_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas AGI additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS
