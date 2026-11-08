from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_retirement_pia_ratio_claiming_adjustment(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = "/1"
    label = "Social Security retirement pia-ratio claiming adjustment"
    documentation = "Worker claiming adjustment from the explicitly selected scenario. Zero is an unavailable diagnostic sentinel for a positive retirement record until a usable adjustment is computed, including missing claiming data or an unsupported pre-1983 benchmark; inspect the flags rather than interpreting it as FRA or a benefit cut. A zero-benefit record keeps neutral adjustment one."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "retirement", "claiming_adjustment"
        )
