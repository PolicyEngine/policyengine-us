from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_survivors_pia_ratio_proxy(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Social Security survivors pia-ratio proxy assumption indicator"
    documentation = "The population PIA-ratio diagnostics use an eligibility, claiming, or birth-date approximation rather than a fully supplied record basis. This flag distinguishes sensitivity assumptions from observed history."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "survivors", "proxy"
        )
