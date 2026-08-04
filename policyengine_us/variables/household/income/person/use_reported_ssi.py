from policyengine_us.model_api import *


class use_reported_ssi(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    default_value = False
    label = "Use reported SSI in program income tests"
    documentation = (
        "Deprecated: this switch only affects the applicable_ssi output, "
        "which no program reads anymore. To report SSI receipt, send the "
        "amount as the ssi input (or set receives_ssi); to report "
        "non-receipt, set takes_up_ssi_if_eligible to false. Retained for "
        "API partner compatibility until partners migrate "
        "(PolicyEngine/policyengine-us#9111)."
    )
