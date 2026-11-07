from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_dependents_pia_ratio_own_record_retired_worker(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Social Security dependents pia-ratio own-record retired-worker indicator"
    documentation = "Whether this component is identified as an own-record retired-worker amount for the population PIA-ratio approximation. This indicator does not establish insured status or validate survey benefit classification."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "dependents", "own_record_retired_worker"
        )
