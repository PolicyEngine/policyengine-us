from policyengine_us.model_api import *


class wa_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=43.216.802",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15",
    )
    adds = ["wa_wccc"]
