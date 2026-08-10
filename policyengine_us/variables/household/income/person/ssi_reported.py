from policyengine_us.model_api import *


class ssi_reported(Variable):
    value_type = float
    entity = Person
    label = "SSI (reported)"
    documentation = (
        "Deprecated: only feeds the applicable_ssi output, which no program "
        "reads anymore. Send reported SSI amounts as the ssi input instead. "
        "Retained for API partner compatibility until partners migrate "
        "(PolicyEngine/policyengine-us#9111)."
    )
    unit = USD
    definition_period = YEAR
