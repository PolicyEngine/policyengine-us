from policyengine_us.model_api import *


class use_reported_ssi(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    default_value = False
    label = "Use reported SSI in program income tests"
    documentation = (
        "When True, programs that count applicable_ssi use ssi_reported "
        "instead of calculated ssi. This lets API partners show federal "
        "SSI entitlement and program eligibility in a single response."
    )
