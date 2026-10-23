from policyengine_us.model_api import *


class social_security_dependents_pia_ratio_factor(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = "/1"
    label = "Social Security dependents PIA ratio factor"
    documentation = (
        "Neutral extension point for a subsequent reported-benefit PIA reform."
    )

    def formula(person, period, parameters):
        return 1
