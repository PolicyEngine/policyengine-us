from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_disability_pia_ratio_claiming_adjustment(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = "/1"
    label = "Social Security disability pia-ratio claiming adjustment"
    documentation = "Worker claiming adjustment used in the baseline inversion under the explicitly selected scenario. Disability uses one. An auxiliary composite worker-benefit ratio already includes its claiming adjustment and is not divided twice."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "disability", "claiming_adjustment"
        )
