from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_retirement_pia_ratio_missing_claim_age(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement pia-ratio missing or unusable claiming data"
    documentation = "Positive reported amount lacks usable data required by the selected claiming scenario. Under supplied_claim_age, missing, before-age-62 or after-age-70 values leave the factor at one without switching scenarios."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "retirement", "missing_claim_age"
        )
