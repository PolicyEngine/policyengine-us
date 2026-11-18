from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_survivors_pia_ratio_pre_1983(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Social Security survivors pia-ratio unsupported pre-1983 benchmark"
    documentation = "Positive reported amount has a benchmark year before 1983. The population PIA-ratio factor remains one because the supported inverse assumes initial PIA dime truncation."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "survivors", "pre_1983"
        )
