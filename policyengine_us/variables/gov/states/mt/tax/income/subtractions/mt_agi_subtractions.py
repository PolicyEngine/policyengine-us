from policyengine_us.model_api import *


class mt_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana AGI subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf"
    )
    defined_for = StateCode.MT
