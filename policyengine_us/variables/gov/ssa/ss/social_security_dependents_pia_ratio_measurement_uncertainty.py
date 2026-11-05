from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_dependents_pia_ratio_measurement_uncertainty(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Social Security dependents pia-ratio measurement uncertainty indicator"
    documentation = "The inference uses a reported annual benefit whose payment or survey measurement basis is not an exact eligibility-level PIA. Its conditional rounding interval does not quantify all measurement uncertainty."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "dependents", "measurement_uncertainty"
        )
