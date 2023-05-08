from policyengine_us.model_api import *


class ms_total_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi total exemption allowance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    adds = ["ms_regular_exemption", "ms_dependents_exemption"]
