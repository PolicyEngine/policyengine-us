from policyengine_us.model_api import *


class mt_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    adds = [
        "mt_base_exemption",
        "mt_aged_exemption",
        "mt_blind_exemption",
        "mt_dependent_exemption",
    ]
