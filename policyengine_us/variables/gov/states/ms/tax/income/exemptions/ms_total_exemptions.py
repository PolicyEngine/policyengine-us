from policyengine_us.model_api import *


class ms_total_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi total exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=6"

    adds = [
        "ms_regular_exemption",
        "ms_dependents_exemption",
        "ms_aged_exemption",
        "ms_blind_exemption",
    ]
