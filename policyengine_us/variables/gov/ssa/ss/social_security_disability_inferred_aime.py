from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_disability_inferred_aime(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Social Security disability inferred eligibility-year monthly aime"
    documentation = "Baseline AIME inverse at the observed unreformed amount, using baseline claiming, identified worker ratio and baseline COLAs. This is the lower endpoint for an exact dime-rounded eligibility PIA. A configured annual measurement bound widens the interval without changing this point estimate. Zero denotes no inference; inspect the diagnostic flags."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "disability", "aime"
        )
