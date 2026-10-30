from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_survivors_pia_ratio_unmodeled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Social Security survivors pia-ratio unmodeled amount indicator"
    documentation = "Positive reported amount lacks an identified worker basis, composite ratio, or another input required for a supported inversion. The factor stays one; the amount is unmodeled for this lever."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "survivors", "unmodeled"
        )
