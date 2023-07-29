from policyengine_us.model_api import *


class mt_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf"
    defined_for = StateCode.MT

    adds = [
        "mt_base_exemption",
        "mt_aged_exemption",
        "mt_blind_exemption",
        "mt_dependent_exemption",
    ]
